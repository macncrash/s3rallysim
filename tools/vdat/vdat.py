"""Vehicle-dynamics acceptance test: compares logged real-car runs with pod runs against a spec.

Usage: python3 vdat.py <spec.toml> <runs_dir> [--json]

<runs_dir>/<test id>/<condition>/real/*.csv and .../sim/*.csv hold one run per file, with a header row of
the spec's canonical channel names (a map.toml with a [channel_map] table in the real/ or sim/ folder
renames a logger's own names). <runs_dir>/rig.toml holds the rig measurements for the spec's [rig] checks.

Metrics (the spec's `metric` strings):
  <scalar>                        a named scalar from each run (SCALARS below); real mean vs sim mean
  curve_rms:<y>:<x>               RMS gap between the sim and real curves of y against x, on a common x grid
  trace_rms:<ch>:<dist|time>      RMS gap between the sim and real traces, aligned on distance or time
  trace_rms_peak:<ch>:<axis>      the same, as a fraction of the real trace's peak
  r2:<ch>:<axis>                  coefficient of determination of the sim trace against the real trace
  peak_abs:<ch>                   peak absolute value
  frf_gain_db:<out>:<in>          frequency-response gain gap (dB), worst over the band up to f_max_hz
  frf_phase_deg:<out>:<in>        frequency-response phase gap (deg), worst over the band
  delta:<metric>                  (tests with `delta`) sim change between conditions / real change
Bands: rel (fraction of the real value), abs (same units), min / max (sim value alone), ratio [lo, hi].
Every scalar check also reports the real runs' own spread: a band tighter than that spread can't be met.
Pure Python, so it runs anywhere the rest of the repo does.
"""

import csv
import math
import os
import sys
import tomllib

G = 9.81


# ---- runs ---------------------------------------------------------------------------------------------

def load_run(path, channel_map):
    with open(path, newline="") as fh:
        rows = list(csv.reader(fh))
    head = [channel_map.get(h.strip(), h.strip()) for h in rows[0]]
    cols = {h: [] for h in head}
    for row in rows[1:]:
        if not row:
            continue
        for h, v in zip(head, row):
            cols[h].append(float(v) if v.strip() else math.nan)
    return cols


def load_runs(folder):
    if not os.path.isdir(folder):
        return []
    cmap = {}
    if os.path.exists(os.path.join(folder, "map.toml")):
        with open(os.path.join(folder, "map.toml"), "rb") as fh:
            cmap = tomllib.load(fh).get("channel_map", {})
    return [load_run(os.path.join(folder, f), cmap) for f in sorted(os.listdir(folder)) if f.endswith(".csv")]


# ---- signal helpers ------------------------------------------------------------------------------------

def smooth(t, y, window_s):
    """Centred moving average over window_s seconds."""
    out, j0, j1, acc = [], 0, 0, 0.0
    for i in range(len(t)):
        while j1 < len(t) and t[j1] <= t[i] + window_s / 2:
            acc += y[j1]
            j1 += 1
        while t[j0] < t[i] - window_s / 2:
            acc -= y[j0]
            j0 += 1
        out.append(acc / (j1 - j0))
    return out


def interp(xs, ys, x):
    """Linear interpolation; xs ascending."""
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    lo, hi = 0, len(xs) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if xs[mid] <= x:
            lo = mid
        else:
            hi = mid
    f = (x - xs[lo]) / (xs[hi] - xs[lo]) if xs[hi] != xs[lo] else 0.0
    return ys[lo] + f * (ys[hi] - ys[lo])


def monotone(xs, ys):
    """Keep samples where x strictly increases (distance stalls when the car stops)."""
    ox, oy = [], []
    for x, y in zip(xs, ys):
        if not ox or x > ox[-1]:
            ox.append(x)
            oy.append(y)
    return ox, oy


def resample(run, ch, axis, grid):
    key = "dist_m" if axis == "dist" else "time_s"
    xs, ys = monotone(run[key], run[ch])
    if axis == "time":
        x0 = xs[0]
        xs = [x - x0 for x in xs]
    return [interp(xs, ys, g) for g in grid]


def common_grid(runs, axis, n=2000):
    key = "dist_m" if axis == "dist" else "time_s"
    if axis == "dist":
        lo = max(min(r[key]) for r in runs)
        hi = min(max(r[key]) for r in runs)
    else:
        lo, hi = 0.0, min(r[key][-1] - r[key][0] for r in runs)
    return [lo + (hi - lo) * k / (n - 1) for k in range(n)]


def mean_trace(traces):
    return [sum(v) / len(v) for v in zip(*traces)]


def linfit(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    return (sum((a - mx) * (b - my) for a, b in zip(x, y)) / sxx) if sxx else math.nan


# ---- scalars from one run ------------------------------------------------------------------------------

def understeer_gradient(r):
    """Handwheel angle against lateral acceleration (deg per g), fitted over 10-80 % of the run's peak."""
    ay = [abs(v) / G for v in smooth(r["time_s"], r["ay_mps2"], 0.5)]
    st = [abs(v) for v in smooth(r["time_s"], r["steer_deg"], 0.5)]
    peak = max(ay)
    pts = [(a, s) for a, s in zip(ay, st) if 0.1 * peak <= a <= 0.8 * peak]
    return linfit([p[0] for p in pts], [p[1] for p in pts])


def max_ay_g(r):
    return max(abs(v) for v in smooth(r["time_s"], r["ay_mps2"], 0.5)) / G


def brake_window(r):
    """From brake application (brake_bar > 2, or decel > 0.1 g) to below 0.5 m/s."""
    t, v = r["time_s"], r["speed_mps"]
    if "brake_bar" in r:
        i0 = next(i for i, b in enumerate(r["brake_bar"]) if b > 2.0)
    else:
        ax = smooth(t, r["ax_mps2"], 0.2)
        i0 = next(i for i, a in enumerate(ax) if a < -0.1 * G)
    i1 = next((i for i in range(i0, len(v)) if v[i] < 0.5), len(v) - 1)
    return i0, i1


def stop_distance_m(r):
    i0, i1 = brake_window(r)
    return r["dist_m"][i1] - r["dist_m"][i0]


def mean_decel_g(r):
    i0, i1 = brake_window(r)
    dv = r["speed_mps"][i0] - r["speed_mps"][i1]
    return dv / (r["time_s"][i1] - r["time_s"][i0]) / G


def time_to_60kph_s(r):
    t, v = r["time_s"], r["speed_mps"]
    v0 = v[0]
    i0 = next(i for i, s in enumerate(v) if s > v0 + 0.3)
    i1 = next(i for i, s in enumerate(v) if s >= 60 / 3.6)
    return t[i1] - t[i0]


def step_window(r):
    """Steer step: 50 % of the final handwheel angle; steady state = the last second."""
    t, st = r["time_s"], r["steer_deg"]
    t_end = t[-1]
    steady = [i for i, x in enumerate(t) if x >= t_end - 1.0]
    s_ss = sum(st[i] for i in steady) / len(steady)
    i50 = next(i for i, s in enumerate(st) if abs(s) >= 0.5 * abs(s_ss))
    return i50, steady, s_ss


def yaw_gain_dps_per_deg(r):
    _i50, steady, s_ss = step_window(r)
    return sum(r["yaw_rate_dps"][i] for i in steady) / len(steady) / s_ss


def ay_gain_g_per_deg(r):
    _i50, steady, s_ss = step_window(r)
    return sum(r["ay_mps2"][i] for i in steady) / len(steady) / G / s_ss


def yaw_response_time_s(r):
    i50, steady, _s = step_window(r)
    y_ss = sum(r["yaw_rate_dps"][i] for i in steady) / len(steady)
    i90 = next(i for i in range(i50, len(r["time_s"])) if abs(r["yaw_rate_dps"][i]) >= 0.9 * abs(y_ss))
    return r["time_s"][i90] - r["time_s"][i50]


def flight(r):
    """Airborne while vertical specific force is under 0.3 g; returns (take-off, landing) indices."""
    az = r["az_mps2"]
    i0 = next(i for i, a in enumerate(az) if a < 0.3 * G)
    i1 = next(i for i in range(i0, len(az)) if az[i] >= 0.3 * G)
    return i0, i1


def airtime_s(r):
    i0, i1 = flight(r)
    return r["time_s"][i1] - r["time_s"][i0]


def landing_pitch_deg(r):
    return r["pitch_deg"][flight(r)[1]]


def landing_peak_az_g(r):
    _i0, i1 = flight(r)
    t = r["time_s"]
    win = [r["az_mps2"][i] for i in range(i1, len(t)) if t[i] <= t[i1] + 0.3]
    return max(win) / G


def section_time_s(r):
    return r["time_s"][-1] - r["time_s"][0]


SCALARS = {f.__name__: f for f in (understeer_gradient, max_ay_g, stop_distance_m, mean_decel_g, time_to_60kph_s,
                                   yaw_gain_dps_per_deg, ay_gain_g_per_deg, yaw_response_time_s, airtime_s,
                                   landing_pitch_deg, landing_peak_az_g, section_time_s)}
SCALARS["understeer_gradient_deg_per_g"] = understeer_gradient


def peak_abs(r, ch):
    return max(abs(v) for v in r[ch] if not math.isnan(v))


# ---- frequency response --------------------------------------------------------------------------------

def frf(r, out, inp, freqs, seg_s=10.0):
    """H(f) = Sxy / Sxx at each frequency: Hann-windowed segments, half overlap, single-bin DFTs."""
    t = r["time_s"]
    dt = (t[-1] - t[0]) / (len(t) - 1)
    n = int(seg_s / dt)
    x, y = r[inp], r[out]
    w = [0.5 - 0.5 * math.cos(2 * math.pi * k / (n - 1)) for k in range(n)]
    res = []
    for f in freqs:
        sxy, sxx = complex(0, 0), 0.0
        for s in range(0, len(x) - n + 1, n // 2):
            mx = sum(x[s:s + n]) / n
            my = sum(y[s:s + n]) / n
            cx = cy = complex(0, 0)
            for k in range(n):
                e = complex(math.cos(2 * math.pi * f * k * dt), -math.sin(2 * math.pi * f * k * dt))
                cx += w[k] * (x[s + k] - mx) * e
                cy += w[k] * (y[s + k] - my) * e
            sxy += cy * cx.conjugate()
            sxx += abs(cx) ** 2
        res.append(sxy / sxx if sxx else complex(math.nan, 0))
    return res


def frf_band(f_max, f_min=0.2, n=10):
    return [f_min + (f_max - f_min) * k / (n - 1) for k in range(n)]


# ---- metrics over runs ---------------------------------------------------------------------------------

def scalar_values(metric, runs):
    if metric.startswith("peak_abs:"):
        return [peak_abs(r, metric.split(":", 1)[1]) for r in runs]
    return [SCALARS[metric](r) for r in runs]


def evaluate(check, real, sim):
    """One check: returns dict with real, sim, gap and pass."""
    metric = check["metric"]
    kind = metric.split(":")[0]
    if kind in ("trace_rms", "trace_rms_peak", "r2"):
        _k, ch, axis = metric.split(":")
        grid = common_grid(real + sim, axis)
        ref = mean_trace([resample(r, ch, axis, grid) for r in real])
        gaps = []
        for s in sim:
            tr = resample(s, ch, axis, grid)
            if kind == "r2":
                mean = sum(ref) / len(ref)
                ss_tot = sum((v - mean) ** 2 for v in ref)
                ss_res = sum((a - b) ** 2 for a, b in zip(tr, ref))
                gaps.append(1 - ss_res / ss_tot)
            else:
                rms = math.sqrt(sum((a - b) ** 2 for a, b in zip(tr, ref)) / len(ref))
                gaps.append(rms / max(abs(v) for v in ref) if kind == "trace_rms_peak" else rms)
        worst = min(gaps) if kind == "r2" else max(gaps)
        return band(check, value=worst, gap=worst)
    if kind == "curve_rms":
        _k, ych, xch = metric.split(":")
        curves = []
        for group in (real, sim):
            pts = sorted((abs(x), abs(y)) for r in group for x, y in zip(r[xch], r[ych]))
            curves.append(pts)
        lo = max(c[0][0] for c in curves)
        hi = min(c[-1][0] for c in curves)
        grid = [lo + (hi - lo) * k / 99 for k in range(100)]
        binned = [[binned_mean(c, g, (hi - lo) / 50) for g in grid] for c in curves]
        rms = math.sqrt(sum((a - b) ** 2 for a, b in zip(*binned)) / len(grid))
        return band(check, value=rms, gap=rms)
    if kind in ("frf_gain_db", "frf_phase_deg"):
        _k, out, inp = metric.split(":")
        freqs = frf_band(check.get("f_max_hz", 2.0))
        hr = [sum(v) / len(v) for v in zip(*[frf(r, out, inp, freqs) for r in real])]
        hs = [sum(v) / len(v) for v in zip(*[frf(r, out, inp, freqs) for r in sim])]
        if kind == "frf_gain_db":
            gaps = [abs(20 * math.log10(abs(b) / abs(a))) for a, b in zip(hr, hs)]
        else:
            gaps = [abs(math.degrees(math.atan2((b / a).imag, (b / a).real))) for a, b in zip(hr, hs)]
        return band(check, value=max(gaps), gap=max(gaps))
    rv, sv = scalar_values(metric, real), scalar_values(metric, sim)
    rm, sm = sum(rv) / len(rv), sum(sv) / len(sv)
    spread = (max(rv) - min(rv)) / 2
    out = band(check, value=sm, gap=sm - rm, ref=rm)
    out["real_spread"] = spread
    if "rel" in check and rm:
        out["real_spread_rel"] = spread / abs(rm)
    return out


def binned_mean(pts, x, half):
    ys = [p[1] for p in pts if abs(p[0] - x) <= half]
    return sum(ys) / len(ys) if ys else math.nan


def band(check, value, gap, ref=None):
    ok = True
    if "rel" in check:
        # Against a real value when there is one; trace_rms_peak's gap is already a fraction of the peak.
        ok = abs(gap) <= check["rel"] * (abs(ref) if ref is not None else 1.0)
    if "abs" in check:
        ok = ok and abs(gap) <= check["abs"]
    if "min" in check:
        ok = ok and value >= check["min"]
    if "max" in check:
        ok = ok and value <= check["max"]
    return {"value": value, "gap": gap, "ref": ref, "pass": bool(ok)}


def evaluate_delta(check, runs, delta):
    """Sim change between conditions as a fraction of the real change; same sign and inside `ratio`."""
    metric = check["metric"].split(":", 1)[1]
    vals = {}
    for side in ("real", "sim"):
        for cond in (delta["from"], delta["to"]):
            v = []
            for src in delta["sources"]:
                rs = runs.get((src, cond, side), [])
                try:
                    v += scalar_values(metric, rs)
                except (KeyError, StopIteration):
                    continue  # this source doesn't carry the metric
            vals[(side, cond)] = sum(v) / len(v) if v else math.nan
    d_real = vals[("real", delta["to"])] - vals[("real", delta["from"])]
    d_sim = vals[("sim", delta["to"])] - vals[("sim", delta["from"])]
    if math.isnan(d_real) or math.isnan(d_sim):
        return {"pass": None, "note": "needs runs on both surfaces"}
    if d_real == 0:
        return {"pass": None, "note": "the real car shows no change between the surfaces"}
    ratio = d_sim / d_real
    lo, hi = check["ratio"]
    return {"value": ratio, "gap": d_sim - d_real, "ref": d_real, "pass": lo <= ratio <= hi}


# ---- driver --------------------------------------------------------------------------------------------

def run(spec_path, runs_dir):
    with open(spec_path, "rb") as fh:
        spec = tomllib.load(fh)
    runs = {}
    for test in spec["test"]:
        for cond in test["conditions"]:
            for side in ("real", "sim"):
                runs[(test["id"], cond, side)] = load_runs(os.path.join(runs_dir, test["id"], cond, side))
    results = []
    for test in spec["test"]:
        # A test with `sources` checks each source test's runs on their own (traces only align within one
        # manoeuvre), one row per source.
        srcs = test.get("sources", [test["id"]]) if "delta" not in test else [None]
        for cond in ([None] if "delta" in test else test["conditions"]):
            for src in srcs:
                for check in test["checks"]:
                    name = test["id"] if src in (None, test["id"]) else f"{test['id']}/{src}"
                    row = {"test": name, "condition": cond, "metric": check["metric"], "why": check["why"]}
                    try:
                        if "delta" in test:
                            row.update(evaluate_delta(check, runs, test["delta"]))
                        else:
                            real, sim = runs.get((src, cond, "real"), []), runs.get((src, cond, "sim"), [])
                            if len(real) < spec["min_real_runs"] or len(sim) < spec["min_sim_runs"]:
                                row.update({"pass": None, "note": f"needs runs: {len(real)} real, {len(sim)} sim"})
                            else:
                                row.update(evaluate(check, real, sim))
                    except (KeyError, StopIteration, ZeroDivisionError, ValueError) as err:
                        row.update({"pass": False, "note": f"could not evaluate: {type(err).__name__} {err}"})
                    results.append(row)
    rig_path = os.path.join(runs_dir, "rig.toml")
    rig = {}
    if os.path.exists(rig_path):
        with open(rig_path, "rb") as fh:
            rig = tomllib.load(fh)
    for check in spec.get("rig", {}).get("checks", []):
        row = {"test": "rig", "condition": None, "metric": check["metric"], "why": check["why"]}
        if check["metric"] in rig:
            v = rig[check["metric"]]
            row.update(band(check, value=v, gap=v))
        else:
            row.update({"pass": None, "note": "not measured"})
        results.append(row)
    return spec, results


def fmt(v):
    return "" if v is None else (f"{v:.4g}" if isinstance(v, float) else str(v))


def main():
    spec_path, runs_dir = sys.argv[1], sys.argv[2]
    spec, results = run(spec_path, runs_dir)
    if "--json" in sys.argv:
        import json
        print(json.dumps(results, indent=1, default=str))
    else:
        print(spec["title"])
        for r in results:
            mark = {True: "PASS", False: "FAIL", None: "----"}[r["pass"]]
            extra = r.get("note") or f"sim {fmt(r.get('value'))}  real {fmt(r.get('ref'))}  gap {fmt(r.get('gap'))}"
            if "real_spread" in r:
                extra += f"  real spread +-{fmt(r['real_spread'])}"
            print(f"{mark}  {r['test']:<11} {fmt(r['condition']):<7} {r['metric']:<40} {extra}")
    done = [r for r in results if r["pass"] is not None]
    passed = sum(1 for r in done if r["pass"])
    print(f"\n{passed}/{len(done)} evaluated checks pass, {len(results) - len(done)} not run")
    sys.exit(0 if done and passed == len(done) and len(done) == len(results) else 1)


if __name__ == "__main__":
    main()
