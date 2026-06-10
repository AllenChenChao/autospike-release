"""Public AutoSpec API."""

from .api import EncodeResult, encode_signal
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
from .io import load_signal_csv, save_array_csv
from .synthetic import generate_synthetic_signal

__all__ = [
    "EncodeResult",
    "bsa_decode",
    "bsa_encode",
    "differential_decode",
    "differential_encode",
    "encode_signal",
    "generate_synthetic_signal",
    "latency_decode",
    "latency_encode",
    "lc_decode",
    "lc_encode",
    "load_signal_csv",
    "poisson_decode",
    "poisson_encode",
    "save_array_csv",
]
