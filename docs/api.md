# AutoSpike Public API

The public Python entry point is:

```python
from autospike import encode_signal
```

## encode_signal

```python
encode_signal(
    signal,
    method="differential",
    normalize=True,
    timesteps=32,
    threshold=0.06,
    delta=0.05,
    reset_mode="soft",
    bsa_filter=None,
    seed=None,
)
```

Input:

- `signal`: one-dimensional numeric array-like object.
- `normalize`: if `True`, AutoSpike maps the signal to `[0, 1]` before encoding. If `False`, all values must already be in `[0, 1]`.

Methods:

- `poisson`: stochastic rate encoding. Uses `timesteps` and `seed`.
- `latency`: one-spike latency encoding. Uses `timesteps`.
- `differential`: signed threshold events. Uses `threshold` and `reset_mode`.
- `lc`: level-crossing events. Uses `delta`.
- `bsa`: Ben's Spiker Algorithm style filter matching. Uses `threshold` and `bsa_filter`.

Return value:

```python
EncodeResult(
    method="differential",
    spikes=...,
    reconstruction=...,
    metrics=...,
    parameters=...,
)
```

Metrics:

- `mse`: mean squared reconstruction error.
- `snr_db`: signal-to-noise ratio in dB.
- `correlation`: Pearson correlation, with stable handling for constant signals.
- `spike_count`: sum of absolute spike/event values.
- `spike_rate`: `spike_count / spikes.size`.

## Low-Level Encoders

The package also exposes low-level functions:

```python
poisson_encode(values, timesteps=32, seed=None)
poisson_decode(spikes)
latency_encode(values, timesteps=32)
latency_decode(spikes)
differential_encode(values, threshold=0.06, reset_mode="soft")
differential_decode(spikes, initial_value, threshold=0.06)
lc_encode(values, delta=0.05)
lc_decode(spikes, initial_value, delta=0.05)
bsa_encode(values, filter_h, threshold=0.0)
bsa_decode(spikes, filter_h)
```

The draft public package intentionally has no hard runtime dependency beyond Python. It accepts plain one-dimensional Python sequences and also works with one-dimensional array-like objects that can be iterated as numbers.
