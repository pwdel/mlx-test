# Using `mlx-test`

## Goal

Use the local MLX coding model from `EXPERIMENT_02.md` to generate small working Python programs on this machine.

## Prerequisites

```bash
cd ~/Projects/mlx-test
direnv allow
uv sync
```

- `direnv allow` loads the repo-local `.envrc`
- `uv sync` creates or updates `.venv`

## Verify the model path

```bash
cd ~/Projects/mlx-test
mlx-code-smoke-test
```

- This uses the same default model as the successful benchmark: `mlx-community/Qwen2.5-Coder-7B-Instruct-4bit`

## Generate code to stdout

```bash
cd ~/Projects/mlx-test
mlx-code-generate "Write a function named square_and_print that takes an integer, squares it, returns the squared value, and prints the result from main."
```

- The command asks the local model for a complete Python script
- It requests at least one function plus an example `__main__` block that prints a result
- It strips common chat formatting such as markdown fences and trailing chat markers
- It syntax-checks the generated code before returning success

## Work inside `code_generate/`

```bash
cd ~/Projects/mlx-test/code_generate
./mlx_code_generate.py \
  --output-file square_and_print.py \
  "Write a function named square_and_print that takes an integer, squares it, returns the squared value, and prints the result from main."
```

- This keeps the generator script and your generated `.py` files in the same working directory
- This assumes you entered the repo with `direnv` active so `python3` resolves to the repo `.venv`
- If `--output-file` has no extension, `.py` is added automatically
- If the cleaned output still is not valid Python, the command does not write the target `.py` file; it writes a sibling `.rejected.txt` file instead

## Save generated code to a file

```bash
cd ~/Projects/mlx-test
mlx-code-generate \
  --output-file generated_sum.py \
  "Write a function named sum_three_numbers that takes three integers, returns their sum, and prints the result from main."
python generated_sum.py
```

- `--output-file generated_sum` also works and becomes `generated_sum.py`
- `--output-file notes.txt` is rejected because the target is expected to be a Python file

## Override the model or generation settings

```bash
cd ~/Projects/mlx-test
mlx-code-generate \
  --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit \
  --max-tokens 384 \
  --max-kv-size 512 \
  "Write a function named reverse_words that reverses word order in a string and prints the result from main."
```

## Replicating `EXPERIMENT_02`

If you want to reproduce the benchmarked setup instead of ad hoc generation:

```bash
cd ~/Projects/mlx-test
uv sync
mlx-code-benchmark
```

- The current default benchmark model is `mlx-community/Qwen2.5-Coder-7B-Instruct-4bit`
- Benchmark artifacts are written under `artifacts/`
- See `EXPERIMENT_02.md` for the last successful run on this machine
