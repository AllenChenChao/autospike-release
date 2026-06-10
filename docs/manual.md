# AutoSpike User Manual

## Overview

AutoSpike converts one-dimensional signals into spike (event) representations. It provides five encoding methods, each producing a different spike pattern from the same input signal. The library includes a Python API, command-line interface, synthetic signal generator, and quality metrics for evaluating encoding fidelity.

## Installation

```bash
pip install -e .
```

No external dependencies are required beyond Python 3.9+.

## Quick Start

### Python API

```python
from autospike import encode_signal, generate_synthetic_signal

signal, meta = generate_synthetic_signal(length=512, seed=7)
result = encode_signal(signal, method="differential", threshold=0.06)

print(len(result.spikes))       # number of samples
print(result.metrics)           # mse, snr_db, correlation, spike_count, spike_rate
```

Run the included example:

```bash
python examples/quickstart.py
```

### Command Line

Generate a synthetic signal and encode it:

```bash
autospike demo --output-dir outputs/demo --method differential --threshold 0.06
```

Encode an existing CSV:

```bash
autospike encode --input data.csv --output-dir outputs/result --method differential
```

---

## Python API Reference

### High-Level API

#### `encode_signal(signal, **kwargs) -> EncodeResult`

The primary entry point. Takes a one-dimensional signal and returns encoded spikes, reconstruction, and metrics.

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `signal` | array-like | *(required)* | One-dimensional numeric signal |
| `method` | `str` | `"differential"` | Encoding method: `poisson`, `latency`, `differential`, `lc`, `bsa` |
| `normalize` | `bool` | `True` | Normalize signal to `[0, 1]` before encoding |
| `timesteps` | `int` | `32` | Time resolution for poisson/latency encoding |
| `threshold` | `float` | `0.06` | Event threshold for differential/BSA encoding |
| `delta` | `float` | `0.05` | Step size for level-crossing encoding |
| `reset_mode` | `str` | `"soft"` | Accumulator reset mode for differential (`"full"` or `"soft"`) |
| `bsa_filter` | array-like | `None` | Custom filter kernel for BSA (uses exponential decay default) |
| `seed` | `int` | `None` | Random seed for stochastic encoders |

**Returns:** `EncodeResult`

#### `EncodeResult`

A frozen dataclass with these fields:

| Field | Type | Description |
|---|---|---|
| `method` | `str` | Encoding method used |
| `spikes` | `list` | Encoded spike/event representation |
| `reconstruction` | `list[float]` | Decoded signal in normalized domain |
| `metrics` | `dict[str, float]` | Quality metrics (see below) |
| `parameters` | `dict[str, Any]` | Normalized encoding parameters |

**Metrics returned:**

| Metric | Description |
|---|---|
| `mse` | Mean squared reconstruction error |
| `snr_db` | Signal-to-noise ratio in dB |
| `correlation` | Pearson correlation (original vs reconstruction) |
| `spike_count` | Sum of absolute spike/event values |
| `spike_rate` | `spike_count / spike_size` |

### Synthetic Signal Generator

#### `generate_synthetic_signal(**kwargs) -> tuple[list[float], dict]`

Generates a synthetic signal with sine wave base, Gaussian bursts, and noise. Useful for testing and examples.

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `length` | `int` | `512` | Number of samples (minimum 32) |
| `sample_rate` | `float` | `128.0` | Sample rate in Hz |
| `seed` | `int` | `7` | Random seed for reproducibility |
| `burst_count` | `int` | `2` | Number of Gaussian-windowed sine bursts |

**Returns:** `(signal_values, metadata_dict)`

### Low-Level Encoders

Each encoder has a matching decoder for reconstruction.

#### Poisson

```python
poisson_encode(values, timesteps=32, seed=None) -> list[list[int]]
poisson_decode(spikes) -> list[float]
```

Stochastic rate encoding. Each sample is represented by a row of `timesteps` binary spikes, where spike probability equals the sample value. Reproducible when `seed` is set.

#### Latency

```python
latency_encode(values, timesteps=32) -> list[list[int]]
latency_decode(spikes) -> list[float]
```

Single-spike-per-sample encoding. Larger values fire earlier (lower index), smaller values fire later. Exactly one spike per row at the index nearest to `(1 - value) * (timesteps - 1)`.

#### Differential

```python
differential_encode(values, threshold=0.06, reset_mode="soft") -> list[int]
differential_decode(spikes, initial_value, threshold=0.06) -> list[float]
```

Threshold-based event encoding. Tracks the cumulative difference between consecutive samples. Emits a `+1` spike when accumulation exceeds `+threshold`, or `-1` when it drops below `-threshold`.

- `reset_mode="full"`: Accumulator resets to zero after each spike.
- `reset_mode="soft"`: Accumulator is reduced by `threshold` after each spike (preserves residual).

#### Level-Crossing (LC)

```python
lc_encode(values, delta=0.05) -> list[int]
lc_decode(spikes, initial_value, delta=0.05) -> list[float]
```

Emits a signed integer spike whenever the signal crosses a multiple of `delta` from the reference level. The spike value indicates how many `delta` steps were crossed (positive or negative). After each crossing, the reference resets to the current value.

#### BSA (Ben's Spiker Algorithm)

```python
bsa_encode(values, filter_h, threshold=0.0) -> list[int]
bsa_decode(spikes, filter_h) -> list[float]
```

Filter-matching algorithm. Slides a kernel over the signal and emits a `1` at positions where convolving the kernel with the residual reduces absolute error more than not spiking (by at least `threshold`). Uses an exponential decay kernel by default.

### I/O Utilities

```python
from autospike import load_signal_csv, save_array_csv
from autospike.io import save_json, save_metadata_csv
```

| Function | Description |
|---|---|
| `load_signal_csv(path)` | Load a one-column or one-row CSV as `list[float]` |
| `save_array_csv(values, path)` | Save nested or flat array to CSV (one value or one row per line) |
| `save_json(data, path)` | Save dict to formatted JSON (handles `inf`, `-inf`, `nan`) |
| `save_metadata_csv(rows, path)` | Save list of dicts as CSV with header |

---

## CLI Reference

### `autospike encode`

Encode an existing signal from a CSV file.

```bash
autospike encode \
  --input data.csv \
  --output-dir outputs/result \
  --method differential \
  --threshold 0.06
```

**Arguments:**

| Flag | Type | Default | Description |
|---|---|---|---|
| `--input` | `Path` | *(required)* | CSV file (one column or one row, numeric) |
| `--output-dir` | `Path` | *(required)* | Output directory |
| `--method` | `str` | `differential` | Encoding method |
| `--timesteps` | `int` | `32` | Timesteps for poisson/latency |
| `--threshold` | `float` | `0.06` | Threshold for differential/BSA |
| `--delta` | `float` | `0.05` | Delta for LC |
| `--reset-mode` | `str` | `soft` | `full` or `soft` |
| `--seed` | `int` | `None` | Random seed |
| `--no-normalize` | flag | *(off)* | Skip normalization (values must already be in `[0, 1]`) |

### `autospike demo`

Generate a synthetic signal and encode it in one step.

```bash
autospike demo --output-dir outputs/demo --method differential --threshold 0.06
```

Same encoding arguments as `encode`, plus:

| Flag | Type | Default | Description |
|---|---|---|---|
| `--output-dir` | `Path` | *(required)* | Output directory |
| `--length` | `int` | `512` | Synthetic signal length |
| `--sample-rate` | `float` | `128.0` | Sample rate in Hz |
| `--burst-count` | `int` | `2` | Number of synthetic bursts |

### Output Files

All commands write these files to `--output-dir`:

| File | Content |
|---|---|
| `spikes.csv` | Encoded spike representation |
| `reconstruction.csv` | Decoded signal (normalized domain) |
| `metrics.json` | Method, parameters, and quality metrics |

`demo` also writes:

| File | Content |
|---|---|
| `synthetic_signal.csv` | Generated input signal |
| `synthetic_metadata.json` | Signal metadata (seed, bursts, noise) |

---

## Encoding Methods Compared

| Method | Spike Shape | Stochastic | Parameter | Best For |
|---|---|---|---|---|
| `poisson` | `(N, T)` binary | Yes | `timesteps` | Rate-based models |
| `latency` | `(N, T)` one-hot | No | `timesteps` | Precise timing |
| `differential` | `(N,)` signed | No | `threshold` | Change detection |
| `lc` | `(N,)` signed int | No | `delta` | Level tracking |
| `bsa` | `(N,)` binary | No | `threshold`, kernel | Filter matching |

Where `N` = signal length, `T` = timesteps.

### Choosing a Method

- Use **differential** when you care about *changes* in the signal (default, good general-purpose).
- Use **lc** (level-crossing) when you need to track the signal level with fewer events.
- Use **poisson** when you need a population-rate code with multiple discrete time bins.
- Use **latency** when you need exactly one spike per sample with precise timing.
- Use **bsa** when you have a specific filter kernel that matches your signal characteristics.

---

## Input Format

### Python

Accepted input types for `encode_signal`:

- `list[float]`
- `tuple[float, ...]`
- Any one-dimensional iterable of numbers

Multi-dimensional inputs are flattened automatically.

### CSV (CLI)

The CLI expects a CSV with:

- One numeric column (values per row), or
- One numeric row (values in a single row)

Empty rows are ignored.

Example (`data.csv`):

```csv
0.10
0.12
0.15
0.18
0.23
```

### Normalization

By default, signals are normalized to `[0, 1]` before encoding. Pass `normalize=False` (Python) or `--no-normalize` (CLI) if your values are already in `[0, 1]`.

---

## Examples

### Encode with Different Methods

```python
from autospike import encode_signal, generate_synthetic_signal

signal, _ = generate_synthetic_signal(length=256, seed=42)

for method in ["differential", "lc", "poisson", "latency", "bsa"]:
    result = encode_signal(signal, method=method)
    print(f"{method:>12}: mse={result.metrics['mse']:.6f},  spikes={result.metrics['spike_count']:.0f}")
```

### Reproducible Results

```python
from autospike import encode_signal

signal = [i / 100 for i in range(100)]

a = encode_signal(signal, method="poisson", timesteps=8, seed=42)
b = encode_signal(signal, method="poisson", timesteps=8, seed=42)

assert a.spikes == b.spikes  # same seed, same result
```

### Using Low-Level Encoders Directly

```python
from autospike import differential_encode, differential_decode

values = [0.1, 0.12, 0.15, 0.18, 0.23, 0.35, 0.62, 0.92, 0.70, 0.42]
spikes = differential_encode(values, threshold=0.1, reset_mode="soft")
reconstructed = differential_decode(spikes, initial_value=values[0], threshold=0.1)
```

### Batch Processing with CLI

```bash
for method in differential lc poisson latency bsa; do
    autospike demo --output-dir "outputs/${method}" --method "${method}"
done
```

## Paper Reference

See [docs/paper.md](paper.md) for the paper citation and a comparison table of the public implementation against the original internal codebase.
