from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

from .encoders import (
    bsa_decode,
    bsa_encode,
    differential_decode,
    differential_encode,
    latency_decode,
    latency_encode,
    lc_decode,
    lc_encode,
    poisson_decode,
    poisson_encode,
)


SUPPORTED_METHODS = {"poisson", "latency", "differential", "lc", "bsa"}


@dataclass(frozen=True)
class EncodeResult:
    """Container returned by the public AutoSpec API."""

    method: str
    spikes: list[Any]
    reconstruction: list[float]
    metrics: dict[str, float]
    parameters: dict[str, Any]


def _flatten_signal(signal: Any) -> list[float]:
    if isinstance(signal, (int, float)):
        return [float(signal)]

    values: list[float] = []
    for item in signal:
        if isinstance(item, (list, tuple)):
            values.extend(float(value) for value in item)
        else:
            values.append(float(item))
    return values


def normalize_signal(signal: Any) -> list[float]:
    values = _flatten_signal(signal)
    if not values:
        raise ValueError("signal must not be empty")
    min_value = min(values)
    max_value = max(values)
    span = max_value - min_value
    if span < 1e-12:
        return [0.0 for _ in values]
    return [(value - min_value) / span for value in values]


def _as_signal(signal: Any, normalize: bool) -> list[float]:
    values = _flatten_signal(signal)
    if not values:
        raise ValueError("signal must not be empty")
    if normalize:
        return normalize_signal(values)
    if any(value < 0.0 or value > 1.0 for value in values):
        raise ValueError("signal values must be in [0, 1] when normalize=False")
    return values


def _default_bsa_filter(length: int = 12) -> list[float]:
    return [math.exp(-index / 3.0) for index in range(length)]


def _correlation(x: list[float], y: list[float]) -> float:
    if len(x) != len(y):
        raise ValueError("correlation inputs must have the same size")
    x_mean = sum(x) / len(x)
    y_mean = sum(y) / len(y)
    x_centered = [value - x_mean for value in x]
    y_centered = [value - y_mean for value in y]
    x_norm = math.sqrt(sum(value * value for value in x_centered))
    y_norm = math.sqrt(sum(value * value for value in y_centered))
    if x_norm < 1e-12 or y_norm < 1e-12:
        return 1.0 if all(abs(a - b) < 1e-12 for a, b in zip(x, y)) else 0.0
    return sum(a * b for a, b in zip(x_centered, y_centered)) / (x_norm * y_norm)


def _spike_count(spikes: Any) -> float:
    if isinstance(spikes, (int, float)):
        return abs(float(spikes))
    total = 0.0
    for item in spikes:
        if isinstance(item, (list, tuple)):
            total += _spike_count(item)
        else:
            total += abs(float(item))
    return total


def _spike_size(spikes: Any) -> int:
    if isinstance(spikes, (int, float)):
        return 1
    total = 0
    for item in spikes:
        if isinstance(item, (list, tuple)):
            total += _spike_size(item)
        else:
            total += 1
    return total


def compute_metrics(signal: list[float], reconstruction: list[float], spikes: Any) -> dict[str, float]:
    if len(signal) != len(reconstruction):
        raise ValueError("reconstruction shape does not match signal shape")

    error = [a - b for a, b in zip(signal, reconstruction)]
    mse = sum(value * value for value in error) / len(error)
    power = sum(value * value for value in signal) / len(signal)
    snr_db = float("inf") if mse <= 0.0 else 10.0 * math.log10(power / mse)
    spike_count = _spike_count(spikes)
    spike_size = _spike_size(spikes)
    spike_rate = spike_count / spike_size if spike_size else 0.0

    return {
        "mse": mse,
        "snr_db": snr_db,
        "correlation": _correlation(signal, reconstruction),
        "spike_count": spike_count,
        "spike_rate": spike_rate,
    }


def encode_signal(
    signal: Any,
    *,
    method: str = "differential",
    normalize: bool = True,
    timesteps: int = 32,
    threshold: float = 0.06,
    delta: float = 0.05,
    reset_mode: str = "soft",
    bsa_filter: Any | None = None,
    seed: int | None = None,
) -> EncodeResult:
    """Encode a one-dimensional signal and decode it for quality metrics."""

    method = method.lower()
    if method not in SUPPORTED_METHODS:
        names = ", ".join(sorted(SUPPORTED_METHODS))
        raise ValueError(f"method must be one of: {names}")

    values = _as_signal(signal, normalize=normalize)
    params: dict[str, Any] = {
        "normalize": normalize,
        "method": method,
    }

    if method == "poisson":
        spikes = poisson_encode(values, timesteps=timesteps, seed=seed)
        reconstruction = poisson_decode(spikes)
        params.update({"timesteps": timesteps, "seed": seed})
    elif method == "latency":
        spikes = latency_encode(values, timesteps=timesteps)
        reconstruction = latency_decode(spikes)
        params.update({"timesteps": timesteps})
    elif method == "differential":
        spikes = differential_encode(values, threshold=threshold, reset_mode=reset_mode)
        reconstruction = differential_decode(spikes, initial_value=values[0], threshold=threshold)
        params.update({"threshold": threshold, "reset_mode": reset_mode})
    elif method == "lc":
        spikes = lc_encode(values, delta=delta)
        reconstruction = lc_decode(spikes, initial_value=values[0], delta=delta)
        params.update({"delta": delta})
    else:
        kernel = _default_bsa_filter() if bsa_filter is None else _flatten_signal(bsa_filter)
        spikes = bsa_encode(values, kernel, threshold=threshold)
        reconstruction = bsa_decode(spikes, kernel)
        params.update({"threshold": threshold, "bsa_filter": kernel})

    return EncodeResult(
        method=method,
        spikes=spikes,
        reconstruction=[float(value) for value in reconstruction],
        metrics=compute_metrics(values, reconstruction, spikes),
        parameters=params,
    )
