# AutoSpec

AutoSpec is a small public interface for converting one-dimensional signals into spike/event representations.

This repository is intended to be a clean release surface: public API, command-line usage, synthetic examples, and documentation. Experimental code, private datasets, trained weights, and internal results should stay in the private research repository.

## What Is Included

- A stable Python API: `autospike.encode_signal`
- A command-line interface: `autospike encode` and `autospike demo`
- Synthetic quickstart examples
- Input/output documentation
- **[Full User Manual](docs/manual.md)**
- **[Paper reference and implementation notes](docs/paper.md)**
- Minimal tests for the public behavior

## Install From A Checkout

```bash
pip install -e .
```

## Python Quickstart

```python
from autospike import encode_signal, generate_synthetic_signal

signal, meta = generate_synthetic_signal(length=512, seed=7)
result = encode_signal(signal, method="differential", threshold=0.06)

print(len(result.spikes))
print(result.metrics)
```

You can also run the included quickstart:

```bash
python examples/quickstart.py
```

## CLI Quickstart

Generate a synthetic signal and encode it:

```bash
autospike demo --output-dir outputs/demo --method differential --threshold 0.06
```

Encode an existing one-column CSV:

```bash
autospike encode \
  --input examples/input_signal.csv \
  --output-dir outputs/encode \
  --method differential \
  --threshold 0.06
```

The CLI writes:

- `spikes.csv`
- `reconstruction.csv`
- `metrics.json`

## Public API Contract

Input:

- A one-dimensional numeric signal.
- Values may be raw or normalized. By default, AutoSpec normalizes them to `[0, 1]` before encoding.

Python call:

```python
encode_signal(
    signal,
    method="differential",
    normalize=True,
    threshold=0.06,
    timesteps=32,
    delta=0.05,
    seed=None,
)
```

Output:

- `EncodeResult.method`: selected encoding method.
- `EncodeResult.spikes`: spike/event list.
- `EncodeResult.reconstruction`: decoded signal list in the normalized domain.
- `EncodeResult.metrics`: MSE, SNR, correlation, spike count, and spike rate.
- `EncodeResult.parameters`: normalized method parameters.

Supported methods:

- `poisson`
- `latency`
- `differential`
- `lc`
- `bsa`

## Repository Boundary

Keep these items out of the public release repository:

- Private or licensed datasets
- Internal experiment scripts
- Model checkpoints and weights
- Large generated result folders
- Work logs and unpublished notes
- Secrets, credentials, local paths, or private server URLs

## License

License is intentionally left as `TBD` in this draft. Choose a final license before publishing the repository.
