from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from autospike import encode_signal, generate_synthetic_signal  # noqa: E402


class PublicApiTest(unittest.TestCase):
    def test_differential_public_api_shapes(self) -> None:
        signal, _ = generate_synthetic_signal(length=128, seed=1)
        result = encode_signal(signal, method="differential", threshold=0.06)

        self.assertEqual(result.method, "differential")
        self.assertEqual(len(result.spikes), len(signal))
        self.assertEqual(len(result.reconstruction), len(signal))
        self.assertIn("mse", result.metrics)

    def test_latency_public_api_shapes(self) -> None:
        signal = [index / 15.0 for index in range(16)]
        result = encode_signal(signal, method="latency", timesteps=8, normalize=False)

        self.assertEqual(len(result.spikes), 16)
        self.assertEqual(len(result.spikes[0]), 8)
        self.assertEqual(len(result.reconstruction), 16)
        self.assertTrue(all(sum(row) == 1 for row in result.spikes))

    def test_poisson_seed_is_reproducible(self) -> None:
        signal = [index / 15.0 for index in range(16)]
        first = encode_signal(signal, method="poisson", timesteps=8, seed=3, normalize=False)
        second = encode_signal(signal, method="poisson", timesteps=8, seed=3, normalize=False)

        self.assertEqual(first.spikes, second.spikes)


if __name__ == "__main__":
    unittest.main()
