# vdat: vehicle-dynamics acceptance test

Compares logged real-car runs with pod runs against a spec, such as
[`requirements/vd-loose-surface.toml`](../../requirements/vd-loose-surface.toml). Written in pure Python (3.11+,
for `tomllib`).

```sh
python3 tools/vdat/selftest.py                                     # synthetic runs with known answers
python3 tools/vdat/vdat.py requirements/vd-loose-surface.toml <runs_dir> [--json]
```

## Runs

```
<runs_dir>/
  rig.toml                       measured rig timing: vehicle_model_hz = 1000, steer_to_motion_ms = 14, ...
  circle/packed/real/run1.csv    one run per CSV
  circle/packed/sim/run1.csv
  brake/loose/real/...           one folder per test id and condition in the spec
```

- **Header row:** the spec's canonical channel names (`[channels]`), in SI units.
- **Renaming a logger's channels:** add a `map.toml` to the `real/` or `sim/` folder:

  ```toml
  [channel_map]
  "G Force Lat" = "ay_mps2"
  ```

- **Converting logs:** export MDF4, MoTeC or AiM logs to CSV first, in SI units. `asammdf` does MDF4.
- **What a run must contain:**
  - Distance along the reference line (`dist_m`), because traces are compared against distance.
  - Each manoeuvre trimmed to itself, with a short steady lead-in.

## Output

One line per check:
- **`PASS` / `FAIL`**, the sim and real values, and the gap.
- **The real runs' spread**, for scalar checks: a band tighter than the spread can't be met.
- **`----`** when a check could not be run: missing runs, or the rig value not measured yet.

The exit code is 0 only when every check in the spec has been run and passed.
