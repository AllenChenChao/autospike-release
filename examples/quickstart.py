from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from autospike import encode_signal, generate_synthetic_signal, save_array_csv  # noqa: E402
from autospike.io import save_json  # noqa: E402


def main() -> None:
    signal, metadata = generate_synthetic_signal(length=512, seed=7)
    result = encode_signal(signal, method="differential", threshold=0.06)

    output_dir = ROOT / "examples" / "outputs" / "quickstart"
    output_dir.mkdir(parents=True, exist_ok=True)
    save_array_csv(signal, output_dir / "synthetic_signal.csv")
    save_array_csv(result.spikes, output_dir / "spikes.csv")
    save_array_csv(result.reconstruction, output_dir / "reconstruction.csv")
    save_json(metadata, output_dir / "synthetic_metadata.json")
    save_json(
        {
            "method": result.method,
            "parameters": result.parameters,
            "metrics": result.metrics,
        },
        output_dir / "metrics.json",
    )

    print(f"wrote: {output_dir}")
    print(f"method: {result.method}")
    print(f"spike rows: {len(result.spikes)}")
    print(f"mse: {result.metrics['mse']:.6g}")
    print(f"spike_count: {result.metrics['spike_count']:.0f}")


if __name__ == "__main__":
    main()
