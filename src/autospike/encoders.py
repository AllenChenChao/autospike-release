from __future__ import annotations

"""Public-reference spike encoders.

Derived from the internal AutoSpike codebase. See `docs/paper.md`
for details and an implementation comparison table.
"""

import math
import random
from typing import Any


def _as_1d_float(values: Any) -> list[float]:
    if isinstance(values, (int, float)):
        array = [float(values)]
    else:
        array = []
        for item in values:
            if isinstance(item, (list, tuple)):
                array.extend(float(value) for value in item)
            else:
                array.append(float(item))
    if not array:
        raise ValueError("values must not be empty")
    return array


def _require_positive(value: float, name: str) -> None:
    if value <= 0.0:
        raise ValueError(f"{name} must be positive")


def poisson_encode(values: Any, *, timesteps: int = 32, seed: int | None = None) -> list[list[int]]:
    values = [min(1.0, max(0.0, value)) for value in _as_1d_float(values)]
    if timesteps < 1:
        raise ValueError("timesteps must be at least 1")
    rng = random.Random(seed)
    return [[1 if rng.random() <= value else 0 for _ in range(timesteps)] for value in values]


def poisson_decode(spikes: Any) -> list[float]:
    rows = [list(row) for row in spikes]
    if not rows or any(not isinstance(row, list) for row in rows):
        raise ValueError("poisson spikes must have shape (samples, timesteps)")
    return [sum(float(value) for value in row) / len(row) for row in rows]


def latency_encode(values: Any, *, timesteps: int = 32) -> list[list[int]]:
    values = [min(1.0, max(0.0, value)) for value in _as_1d_float(values)]
    if timesteps < 2:
        raise ValueError("timesteps must be at least 2")
    spikes: list[list[int]] = []
    for value in values:
        index = round((1.0 - value) * (timesteps - 1))
        row = [0 for _ in range(timesteps)]
        row[index] = 1
        spikes.append(row)
    return spikes


def latency_decode(spikes: Any) -> list[float]:
    rows = [list(row) for row in spikes]
    if not rows or any(not isinstance(row, list) for row in rows):
        raise ValueError("latency spikes must have shape (samples, timesteps)")
    decoded: list[float] = []
    for row in rows:
        timesteps = len(row)
        if sum(row) == 0:
            decoded.append(0.0)
        else:
            index = max(range(timesteps), key=lambda item: row[item])
            decoded.append(min(1.0, max(0.0, 1.0 - index / float(timesteps - 1))))
    return decoded


def _normalize_reset_mode(reset_mode: str) -> str:
    if reset_mode not in {"full", "soft"}:
        raise ValueError("reset_mode must be 'full' or 'soft'")
    return reset_mode


def differential_encode(values: Any, *, threshold: float = 0.06, reset_mode: str = "soft") -> list[int]:
    values = _as_1d_float(values)
    _require_positive(threshold, "threshold")
    mode = _normalize_reset_mode(reset_mode)

    spikes = [0 for _ in values]
    accumulator = 0.0
    for index in range(1, len(values)):
        accumulator += values[index] - values[index - 1]
        if accumulator >= threshold:
            spikes[index] = 1
            accumulator = 0.0 if mode == "full" else accumulator - threshold
        elif accumulator <= -threshold:
            spikes[index] = -1
            accumulator = 0.0 if mode == "full" else accumulator + threshold
    return spikes


def differential_decode(spikes: Any, *, initial_value: float, threshold: float = 0.06) -> list[float]:
    spikes = _as_1d_float(spikes)
    _require_positive(threshold, "threshold")
    current = float(initial_value)
    reconstruction = []
    for spike in spikes:
        current += spike * threshold
        reconstruction.append(current)
    return reconstruction


def lc_encode(values: Any, *, delta: float = 0.05) -> list[int]:
    values = _as_1d_float(values)
    _require_positive(delta, "delta")
    spikes = [0 for _ in values]
    reference = float(values[0])

    for index in range(1, len(values)):
        diff = float(values[index] - reference)
        if diff >= delta:
            steps = int(math.floor(diff / delta))
        elif diff <= -delta:
            steps = int(math.ceil(diff / delta))
        else:
            steps = 0
        spikes[index] = steps
        if steps != 0:
            reference = float(values[index])
    return spikes


def lc_decode(spikes: Any, *, initial_value: float, delta: float = 0.05) -> list[float]:
    spikes = _as_1d_float(spikes)
    _require_positive(delta, "delta")
    current = float(initial_value)
    reconstruction = []
    for spike in spikes:
        current += spike * delta
        reconstruction.append(current)
    return reconstruction


def _normalize_bsa_filter(filter_h: Any) -> list[float]:
    kernel = _as_1d_float(filter_h)
    if not kernel:
        raise ValueError("BSA filter must not be empty")
    return kernel


def bsa_encode(values: Any, filter_h: Any, *, threshold: float = 0.0) -> list[int]:
    values = _as_1d_float(values)
    kernel = _normalize_bsa_filter(filter_h)
    if threshold < 0.0:
        raise ValueError("threshold must be non-negative")

    spikes = [0 for _ in values]
    residual = list(values)
    kernel_len = len(kernel)
    for index in range(len(values)):
        if index + kernel_len > len(values):
            break
        window = residual[index : index + kernel_len]
        error_with_spike = sum(abs(a - b) for a, b in zip(window, kernel))
        error_without_spike = sum(abs(value) for value in window)
        if error_with_spike <= error_without_spike - threshold:
            spikes[index] = 1
            for offset, kernel_value in enumerate(kernel):
                residual[index + offset] -= kernel_value
    return spikes


def bsa_decode(spikes: Any, filter_h: Any) -> list[float]:
    spikes = _as_1d_float(spikes)
    kernel = _normalize_bsa_filter(filter_h)
    reconstruction = [0.0 for _ in spikes]
    for index, spike in enumerate(spikes):
        if spike == 0:
            continue
        for offset, kernel_value in enumerate(kernel):
            target = index + offset
            if target >= len(reconstruction):
                break
            reconstruction[target] += spike * kernel_value
    return reconstruction
