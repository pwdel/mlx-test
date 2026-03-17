from __future__ import annotations

import argparse
import json
import platform
import resource
import time
from pathlib import Path

import mlx.core as mx
from mlx_lm import generate, load


DEFAULT_MODEL = "mlx-community/Qwen2.5-Coder-7B-Instruct-4bit"
PROMPT = (
    "Write only Python code. "
    "Return a function named hello_world() that prints 'Hello, world!'. "
    "Do not include markdown fences or explanation."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics-json", required=True)
    parser.add_argument("--output-file", required=True)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--max-tokens", type=int, default=96)
    parser.add_argument("--max-kv-size", type=int, default=512)
    return parser.parse_args()


def maybe_token_count(tokenizer, text: str) -> int | None:
    try:
        if hasattr(tokenizer, "encode"):
            return len(tokenizer.encode(text))
    except Exception:
        return None
    return None


def main() -> int:
    args = parse_args()
    metrics_path = Path(args.metrics_json)
    output_path = Path(args.output_file)

    load_started = time.perf_counter()
    model, tokenizer = load(args.model)
    load_seconds = time.perf_counter() - load_started

    if hasattr(tokenizer, "apply_chat_template"):
        prompt = tokenizer.apply_chat_template(
            [{"role": "user", "content": PROMPT}],
            tokenize=False,
            add_generation_prompt=True,
        )
    else:
        prompt = PROMPT

    generate_started = time.perf_counter()
    response = generate(
        model,
        tokenizer,
        prompt=prompt,
        max_tokens=args.max_tokens,
        max_kv_size=args.max_kv_size,
        verbose=False,
    )
    generate_seconds = time.perf_counter() - generate_started

    output_path.write_text(response)

    prompt_tokens = maybe_token_count(tokenizer, prompt)
    output_tokens = maybe_token_count(tokenizer, response)
    tokens_per_second = None
    if output_tokens and generate_seconds > 0:
        tokens_per_second = output_tokens / generate_seconds

    max_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    metrics = {
        "model": args.model,
        "device": str(mx.default_device()),
        "platform": platform.platform(),
        "load_seconds": load_seconds,
        "generate_seconds": generate_seconds,
        "prompt_tokens": prompt_tokens,
        "output_tokens": output_tokens,
        "tokens_per_second": tokens_per_second,
        "max_kv_size": args.max_kv_size,
        "max_rss": max_rss,
        "success": "def hello_world" in response,
    }

    metrics_path.write_text(json.dumps(metrics, indent=2))
    print(response)

    return 0 if metrics["success"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
