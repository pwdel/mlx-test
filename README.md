# mlx-test

Scratch repo for experimenting with [MLX](https://github.com/ml-explore/mlx).

## Why MLX

MLX is Apple's array framework for machine learning research on Apple silicon. The official README highlights:

- Familiar NumPy-style and Python APIs
- Lazy computation
- Unified memory between CPU and GPU
- Support for distributed communication primitives

## Local setup

- This repo uses `.envrc` with `direnv`
- Entering the repo sets `CODEX_HOME` to this repo's `.codex`
- Entering the repo also auto-activates `.venv` if it already exists
- Entering the repo adds `bin/` to `PATH` for local helper commands
- `uv sync` creates or updates `.venv` from `pyproject.toml`

## Path note

- Use `~/Projects/...` in shell-facing files like `.envrc`, README examples, and terminal commands
- Keep `[projects."/absolute/path"]` entries in `config.toml` as absolute paths when you need them; `config.toml` is not shell-expanded like `.envrc`
- To avoid checking in machine-specific paths, prefer keeping path-specific trust settings in `~/.codex/config.toml` or setting trust locally instead of committing them to the repo

## First run

```bash
cd ~/Projects/mlx-test
direnv allow
uv sync
python -c "import mlx.core as mx; print(mx.array([1, 2, 3]))"
```

## Smoke test

```bash
cd ~/Projects/mlx-test
mlx-smoke-test
```

## Code model smoke test

```bash
cd ~/Projects/mlx-test
uv sync
mlx-code-smoke-test
```

- This uses `mlx-community/Qwen2.5-Coder-7B-Instruct-4bit`
- The first run downloads the model locally, so expect a large one-time download
- The command asks the model for a tiny Python `hello_world()` function and checks that the response contains `def hello_world`

## Code model benchmark

```bash
cd ~/Projects/mlx-test
uv sync
mlx-code-benchmark
```

- This records hardware info plus per-second process CPU and RSS samples
- The run writes artifacts under `artifacts/`
- `hardware.txt` and `gpu.txt` are sanitized summaries; they do not include serial numbers, UUIDs, or UDIDs
- The current default benchmark model is `mlx-community/Qwen2.5-Coder-7B-Instruct-4bit`
- You can override the model for a one-off run with `mlx-code-benchmark --model <huggingface-model-id>`
- See `EXPERIMENT_01.md` and `EXPERIMENT_02.md` for benchmark results

## Usage

- See `USE.md` for a repeatable local workflow that generates Python code with the same smaller model used in `EXPERIMENT_02.md`
- The reusable local generator now lives at `code_generate/mlx_code_generate.py`
