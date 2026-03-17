# MLX coding experiment

## Goal

Benchmark a local coding inference with `mlx-community/Qwen2.5-Coder-7B-Instruct-4bit` on this machine and record:

- hardware used
- generation success
- load time
- generation time
- output token count
- approximate throughput
- sampled process CPU and RSS during the run

## Hardware

- MacBook Air
- Apple M4
- 10 CPU cores (4 performance, 6 efficiency)
- 8 GPU cores
- 16 GB unified memory
- MLX device: `Device(gpu, 0)`

## Command

```bash
cd ~/Projects/mlx-test
uv sync
mlx-code-benchmark
```

## Results

### Run 1 — `2026-03-15`

- Model: `mlx-community/Qwen2.5-Coder-7B-Instruct-4bit`
- Outcome: success
- Load time: about `1.76s`
- Generation time: about `1.61s`
- Prompt tokens: `57`
- Output tokens: `17`
- Approximate throughput: about `10.55` tokens/s
- Peak sampled process CPU: about `92.2%`
- Peak sampled process RSS: about `2,845,440 KB` (~`2.7 GB`)
- `ru_maxrss`: about `3,160,621,056` bytes (~`2.9 GB`)

Observed output:

```python
def hello_world():
    print('Hello, world!')
```

Notes:

- The model completed inference successfully on this machine without hitting Metal out-of-memory
- The response still included markdown fences and a trailing chat token marker, so the output is usable but not perfectly clean
- This is a much better default local coding model for this machine than the `30B` Qwen3-Coder test in `EXPERIMENT_01.md`

## Artifacts

The benchmark command writes per-run files under `artifacts/`, including:

- `hardware.txt` (sanitized summary)
- `gpu.txt` (sanitized summary)
- `process_samples.csv`
- `stdout.log`
- `stderr.log`
- `metrics.json`
- `response.py`

Run directory:

- `artifacts/mlx-code-benchmark-20260315-144515`
