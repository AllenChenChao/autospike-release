# Input And Output

## Input Signal

AutoSpec public examples use a single one-dimensional signal.

Accepted Python input:

- `list[float]`
- `tuple[float, ...]`
- one-dimensional array-like values that iterate as numbers

Accepted CLI input:

- CSV with one numeric column.
- CSV with one numeric row.

Example:

```csv
0.10
0.12
0.15
0.18
0.23
```

By default, the public API normalizes values to `[0, 1]`.

## Output Files

The CLI writes three core files:

- `spikes.csv`: encoded spike/event representation.
- `reconstruction.csv`: decoded signal in the normalized domain.
- `metrics.json`: method, parameters, and reconstruction metrics.

For `autospike demo`, two additional files are written:

- `synthetic_signal.csv`
- `synthetic_metadata.json`

## Spike Array Shapes

Shape depends on the method:

- `poisson`: list of `signal_length` rows, each with `timesteps` values.
- `latency`: list of `signal_length` rows, each with `timesteps` values.
- `differential`: list of `signal_length` signed events.
- `lc`: list of `signal_length` signed level-crossing events.
- `bsa`: list of `signal_length` binary events.

The high-level API keeps these native shapes so downstream users can choose their own model input layout.
