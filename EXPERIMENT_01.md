# MLX coding experiment

## Goal

Benchmark a local coding inference with `mlx-community/Qwen3-Coder-30B-A3B-Instruct-3bit` on this machine and record:

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
mlx-code-benchmark --model mlx-community/Qwen3-Coder-30B-A3B-Instruct-3bit
```

## Results

### Run 1 — `2026-03-15`

- Model download completed successfully
- Benchmark runtime before failure: about `275s`
- Peak sampled process CPU: about `56.0%`
- Peak sampled process RSS: about `3,945,568 KB` (~`3.8 GB`)
- Outcome: failed during model execution with Metal out-of-memory

Observed error:

```text
[METAL] Command buffer execution failed: Insufficient Memory
```

Interpretation:

- On this `16 GB` M4 Air, `Qwen3-Coder-30B-A3B-Instruct-3bit` is still too large to reliably run a coding inference in the current machine state
- The model can be downloaded and begins loading, but generation fails once Metal memory pressure gets high enough
- The sampled RSS understates total unified-memory pressure because Metal/GPU allocations are not fully reflected in normal process RSS

Practical takeaway:

- This model is not a good default local coding model for this machine
- The next useful experiment should be a materially smaller coding model

## Artifacts

The benchmark command writes per-run files under `artifacts/`, including:

- `hardware.txt` (sanitized summary)
- `gpu.txt` (sanitized summary)
- `process_samples.csv`
- `stdout.log`
- `stderr.log`
- `metrics.json` on successful runs
- `response.py` on successful runs

Latest run directory:

- `artifacts/mlx-code-benchmark-20260315-140542`
