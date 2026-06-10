# Paper Reference

> This repository is the reference implementation for the AutoSpike paper.
> *[TBD: paper title, authors, venue, DOI]*

## About This Release

The public release removes the NumPy and PyTorch dependencies used in the
paper's experiments and re-implements the core encoders in pure Python
(standard library only).  This makes the library zero-dependency, easy to
install, and fully auditable.

All five encoding methods are **algorithmically equivalent** to the
original implementation.  The table below maps each encoder between the
two codebases.

## Encoder Implementation Comparison

| Encoding Method | Internal (paper experiments) | Public (this repo) |
|---|---|---|
| **Poisson** | `poisson_encode` — torch tensor ops, `(T,F)` shape | `poisson_encode` — `random.Random`, 1D `list` shape |
| **Latency** | `latency_encode` — torch `scatter_`, `(T,F)` shape | `latency_encode` — Python loops, 1D `list` shape |
| **Differential** | `diff_encode` — numpy broadcasting, `(T,F)` shape, `reset` param | `differential_encode` — Python loops, 1D `list` shape, `reset_mode` param |
| **LC** | `lc_encode` — numpy, supports `single`/`multi` event modes | `lc_encode` — Python loops, `multi` mode only |
| **BSA** | `bsa_encode` — numpy, `np.convolve` decode, `(T,F)` shape | `bsa_encode` — Python loops, manual decode, 1D `list` shape |

> Core encoding/decoding algorithms are equivalent.  Single-channel results
> match within floating-point tolerance under the same parameters.
>
> The internal codebase also contains extensive evaluation infrastructure
> (parameter sweeps, cross-modality profiling, downstream ANN tasks,
> figure-generation pipelines) that is excluded from this public release.
