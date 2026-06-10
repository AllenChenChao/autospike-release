from __future__ import annotations

import math
import random
from typing import Any


def _normalize01(values: list[float]) -> list[float]:
    span = max(values) - min(values)
    if span < 1e-12:
        return [0.0 for _ in values]
    low = min(values)
    return [(value - low) / span for value in values]


def generate_synthetic_signal(
    *,
    length: int = 512,
    sample_rate: float = 128.0,
    seed: int = 7,
    burst_count: int = 2,
) -> tuple[list[float], dict[str, Any]]:
    """Generate a public, synthetic signal for examples and tests."""

    if length < 32:
        raise ValueError("length must be at least 32")
    if sample_rate <= 0.0:
        raise ValueError("sample_rate must be positive")
    if burst_count < 0:
        raise ValueError("burst_count must be non-negative")

    rng = random.Random(seed)
    time = [index / sample_rate for index in range(length)]
    base_freq = rng.uniform(0.8, 3.0)
    base_phase = rng.uniform(0.0, 2.0 * math.pi)
    signal = [0.25 * math.sin(2.0 * math.pi * base_freq * item + base_phase) for item in time]
    bursts: list[dict[str, float]] = []

    for _ in range(burst_count):
        width = int(rng.uniform(0.06, 0.16) * length)
        width = max(8, min(width, length // 3))
        start = rng.randrange(0, length - width)
        burst_freq = rng.uniform(10.0, 24.0)
        burst_amp = rng.uniform(0.55, 0.95)
        phase = rng.uniform(0.0, 2.0 * math.pi)
        for offset in range(width):
            if width <= 1:
                window = 1.0
            else:
                window = 0.5 - 0.5 * math.cos(2.0 * math.pi * offset / (width - 1))
            burst = burst_amp * math.sin(2.0 * math.pi * burst_freq * time[offset] + phase) * window
            signal[start + offset] += burst
        bursts.append(
            {
                "start": float(start),
                "width": float(width),
                "frequency_hz": float(burst_freq),
                "amplitude": float(burst_amp),
            }
        )

    noise_std = 0.025
    signal = [value + rng.gauss(0.0, noise_std) for value in signal]
    metadata = {
        "length": length,
        "sample_rate": sample_rate,
        "seed": seed,
        "noise_std": noise_std,
        "bursts": bursts,
        "source": "synthetic",
    }
    return _normalize01(signal), metadata
