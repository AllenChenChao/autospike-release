from __future__ import annotations

import argparse
from pathlib import Path

from .api import SUPPORTED_METHODS, encode_signal
from .io import load_signal_csv, save_array_csv, save_json
from .synthetic import generate_synthetic_signal


def _add_common_encode_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--method",
        choices=sorted(SUPPORTED_METHODS),
        default="differential",
        help="Encoding method.",
    )
    parser.add_argument("--timesteps", type=int, default=32, help="Timesteps for poisson/latency encoding.")
    parser.add_argument("--threshold", type=float, default=0.06, help="Threshold for differential/BSA encoding.")
    parser.add_argument("--delta", type=float, default=0.05, help="Delta for LC encoding.")
    parser.add_argument("--reset-mode", choices=["full", "soft"], default="soft", help="Differential reset mode.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for stochastic encoders.")
    parser.add_argument(
        "--no-normalize",
        action="store_true",
        help="Require input values to already be in [0, 1].",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="autospike", description="AutoSpike public CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    encode = subparsers.add_parser("encode", help="Encode a one-dimensional CSV signal.")
    encode.add_argument("--input", required=True, type=Path, help="One-column or one-row CSV input.")
    encode.add_argument("--output-dir", required=True, type=Path, help="Directory for output files.")
    _add_common_encode_args(encode)

    demo = subparsers.add_parser("demo", help="Generate a synthetic signal and encode it.")
    demo.add_argument("--output-dir", required=True, type=Path, help="Directory for demo output files.")
    demo.add_argument("--length", type=int, default=512, help="Synthetic signal length.")
    demo.add_argument("--sample-rate", type=float, default=128.0, help="Synthetic sample rate in Hz.")
    demo.add_argument("--burst-count", type=int, default=2, help="Number of synthetic bursts.")
    _add_common_encode_args(demo)

    return parser


def _run_encode(args: argparse.Namespace) -> None:
    signal = load_signal_csv(args.input)
    _write_result(signal, args)


def _run_demo(args: argparse.Namespace) -> None:
    signal, metadata = generate_synthetic_signal(
        length=args.length,
        sample_rate=args.sample_rate,
        seed=7 if args.seed is None else args.seed,
        burst_count=args.burst_count,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    save_array_csv(signal, args.output_dir / "synthetic_signal.csv")
    save_json(metadata, args.output_dir / "synthetic_metadata.json")
    _write_result(signal, args)


def _write_result(signal, args: argparse.Namespace) -> None:
    result = encode_signal(
        signal,
        method=args.method,
        normalize=not args.no_normalize,
        timesteps=args.timesteps,
        threshold=args.threshold,
        delta=args.delta,
        reset_mode=args.reset_mode,
        seed=args.seed,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    save_array_csv(result.spikes, args.output_dir / "spikes.csv")
    save_array_csv(result.reconstruction, args.output_dir / "reconstruction.csv")
    save_json(
        {
            "method": result.method,
            "parameters": result.parameters,
            "metrics": result.metrics,
        },
        args.output_dir / "metrics.json",
    )
    print(f"method: {result.method}")
    print(f"spikes: {args.output_dir / 'spikes.csv'}")
    print(f"reconstruction: {args.output_dir / 'reconstruction.csv'}")
    print(f"metrics: {args.output_dir / 'metrics.json'}")
    print(f"mse: {result.metrics['mse']:.6g}")
    print(f"spike_count: {result.metrics['spike_count']:.0f}")


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "encode":
        _run_encode(args)
    elif args.command == "demo":
        _run_demo(args)
    else:
        parser.error(f"unknown command: {args.command}")
