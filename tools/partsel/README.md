# partsel: part selector

Checks candidate bought parts against a requirement and says which fit, which don't and why, with every
number traced back to the vendor document it came from. Plain Python 3.11+, no installs. Brought over from the
robits project's parts methodology.

```
python3 tools/partsel/partsel.py requirements/crank-gearbox.toml            # summary table
python3 tools/partsel/partsel.py requirements/crank-gearbox.toml --detail   # reasons + a source for every value
python3 tools/partsel/partsel.py requirements/crank-servo.toml --brief --set bus_vdc=560   # what-if: 400 V drive
python3 tools/partsel/to_cad.py                                             # selection.toml -> cad/pod/bought.py
python3 tools/partsel/to_cad.py --check                                     # is bought.py up to date?
```

Verdicts: **PASS** (every hard check met), **FAIL** (a hard check not met), **CHECK** (nothing failed, but a value
a check needs is missing from the card). Checks marked `prefer = true` only change the ranking.

Requirements live in [`requirements/`](../../requirements/), one file per need. Their numbers come from this
repo's analyses (`analysis/platform_loads.json`, `cad/pod/ergo.py`), so a change in loads or ergonomics is one
re-run away from a new verdict.

## Derived values

| Field | How |
|---|---|
| `bus_vdc_needed` | Back-EMF constant x speed x sqrt(2) x 1.15 (peak line-line voltage plus 15% for IR drop and control headroom) |
| `current_at_peak_torque_arms` | Required peak torque / torque constant |
| `emergency_stop_torque_nm`, `max_accel_output_torque_nm` | Gearboxes that print rules: T2N x `estop_torque_factor`, then x `accel_torque_pct_of_estop` / 100 |
| `permissible_alternating_load_n` | Rod ends: housing static rating x the maker's `alternating_load_factor` |

## From selection to CAD

`requirements/selection.toml` names the chosen part for each requirement, with a status (`chosen` or
`provisional`) and why. `to_cad.py` re-runs the selector, refuses a part that fails unless it's marked
provisional, and writes every chosen card's values into `cad/pod/bought.py`. The STEVE components read sizes and
masses from there, so the model, the selection and the vendor sources stay in step.
