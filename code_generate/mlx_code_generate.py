#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


DEFAULT_MODEL = "mlx-community/Qwen2.5-Coder-7B-Instruct-4bit"
SYSTEM_PROMPT = (
    "Write only Python code. "
    "Return a complete, working Python script for the user's request. "
    "Include at least one function. "
    "Include an example call under if __name__ == '__main__': that prints the result. "
    "Do not include markdown fences or explanation."
)
PYTHON_START_PATTERNS = (
    "from ",
    "import ",
    "def ",
    "async def ",
    "class ",
    "@",
    "if __name__ ==",
    "\"\"\"",
    "'''",
    "#",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("request", nargs="+", help="What Python code to generate")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--max-kv-size", type=int, default=512)
    parser.add_argument("--output-file")
    return parser.parse_args()


def build_prompt(user_request: str) -> str:
    return f"Task: {user_request}"


def remove_known_artifacts(text: str) -> str:
    cleaned = text.replace("\r\n", "\n").strip()
    cleaned = cleaned.replace("<|im_end|>", "")
    cleaned = cleaned.replace("<|endoftext|>", "")
    return cleaned.strip()


def extract_fenced_code(text: str) -> str:
    match = re.search(r"```(?:python)?\s*\n(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text


def looks_like_python_start(line: str) -> bool:
    stripped = line.lstrip()
    if not stripped:
        return False
    if stripped.startswith(PYTHON_START_PATTERNS):
        return True
    if re.match(r"[A-Za-z_][A-Za-z0-9_]*\s*=", stripped):
        return True
    return False


def strip_non_code_prefix(text: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if looks_like_python_start(line):
            return "\n".join(lines[index:]).strip()
    return text.strip()


def salvage_valid_prefix(text: str) -> str:
    try:
        compile(text, "<generated>", "exec")
        return text
    except SyntaxError as exc:
        if exc.lineno and exc.lineno > 1:
            prefix = "\n".join(text.splitlines()[: exc.lineno - 1]).strip()
            if prefix:
                try:
                    compile(prefix, "<generated-prefix>", "exec")
                    return prefix
                except SyntaxError:
                    return text
    return text


def clean_response(text: str) -> str:
    cleaned = remove_known_artifacts(text)
    cleaned = extract_fenced_code(cleaned)
    cleaned = strip_non_code_prefix(cleaned)
    cleaned = remove_known_artifacts(cleaned)
    cleaned = re.sub(r"^```(?:python)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = salvage_valid_prefix(cleaned)
    return cleaned.strip() + "\n"


def normalize_output_path(path_str: str) -> Path:
    output_path = Path(path_str).expanduser()
    if output_path.suffix == "":
        output_path = output_path.with_suffix(".py")
    elif output_path.suffix != ".py":
        raise SystemExit("--output-file must end with .py or omit the extension")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def write_rejected_output(output_path: Path, text: str) -> Path:
    rejected_path = output_path.with_suffix(output_path.suffix + ".rejected.txt")
    rejected_path.write_text(text)
    return rejected_path


def main() -> int:
    args = parse_args()
    user_request = " ".join(args.request).strip()
    output_path = normalize_output_path(args.output_file) if args.output_file else None

    from mlx_lm import generate, load

    model, tokenizer = load(args.model)

    if hasattr(tokenizer, "apply_chat_template"):
        prompt = tokenizer.apply_chat_template(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_prompt(user_request)},
            ],
            tokenize=False,
            add_generation_prompt=True,
        )
    else:
        prompt = f"{SYSTEM_PROMPT}\n\n{build_prompt(user_request)}"

    response = generate(
        model,
        tokenizer,
        prompt=prompt,
        max_tokens=args.max_tokens,
        max_kv_size=args.max_kv_size,
        verbose=False,
    )

    cleaned = clean_response(response)

    try:
        compile(cleaned, "<generated>", "exec")
    except SyntaxError as exc:
        print(f"Generated code is not valid Python: {exc}", file=sys.stderr)
        if output_path:
            rejected_path = write_rejected_output(output_path, cleaned)
            print(f"Wrote cleaned rejected output to {rejected_path}", file=sys.stderr)
        else:
            print(cleaned)
        return 2

    if output_path:
        output_path.write_text(cleaned)
        print(f"Wrote {output_path}")
    else:
        print(cleaned, end="")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
