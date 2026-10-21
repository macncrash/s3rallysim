"""Self-test for vdat.py: synthetic runs with known answers.

Usage: python3 selftest.py

Writes runs for the circle, brake, traction, step-steer, sweep and jump tests twice: once with a "sim" a few
per cent off the "real" car (every check must pass), once with the sim's grip 25 % high (the grip checks must
fail). Each real run gets a little run-to-run scatter, as a real car would.
"""

import csv
import math
import os
import random
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))
import vdat  # noqa: E402

G = 9.81
DT = 0.01
SPEC = os.path.join(os.path.dirname(__file__), "..", "..", "requirements", "vd-loose-surface.toml")
CH = ["time_s", "dist_m", "speed_mps", "ax_mps2", "ay_mps2", "az_mps2", "yaw_rate_dps", "pitch_deg", "sideslip_deg",
      "steer_deg", "steer_torque_nm", "brake_bar", "slip"]


def write(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(CH)
        for r in rows:
            w.writerow([f"{r.get(c, 0.0):.5f}" for c in CH])


def integrate(rows):
    d = 0.0
    for r in rows:
        d += r["speed_mps"] * DT
        r["dist_m"] = d
    return rows


def circle(grip, k_us):
    rows, n = [], int(60 / DT)
    for i in range(n):
        ay = grip * G * i / n
        rows.append({"time_s": i * DT, "speed_mps": math.sqrt(ay * 40 + 1), "ay_mps2": ay, "az_mps2": G,
                     "steer_deg": 60 + k_us * ay / G, "sideslip_deg": 4 * (ay / G) ** 2 / grip,
                     "yaw_rate_dps": math.degrees(math.sqrt(ay * 40 + 1) / 40), "steer_torque_nm": 2 + 0.8 * ay})
    return integrate(rows)


def brake(grip, v0):
    rows, v, t = [], v0, 0.0
    while t < 1.0 or v > 0:
        on = t >= 1.0
        a = -grip * G if on else 0.0
        v = max(0.0, v + a * DT)
        rows.append({"time_s": t, "speed_mps": v, "ax_mps2": a, "az_mps2": G, "brake_bar": 40.0 if on else 0.0})
        t += DT
    rows += [{"time_s": t + k * DT, "speed_mps": 0.0, "az_mps2": G} for k in range(50)]
    return integrate(rows)


def traction(grip):
    rows, v, t = [], 0.0, 0.0
    while v < 70 / 3.6:
        a = min(grip * G * 0.6, 6.0) if t >= 0.5 else 0.0
        v += a * DT
        rows.append({"time_s": t, "speed_mps": v, "ax_mps2": a, "az_mps2": G, "slip": 0.15 * grip if t >= 0.5 else 0})
        t += DT
    return integrate(rows)


def first_order(u, tau):
    y, out = 0.0, []
    for x in u:
        y += (x - y) * DT / tau
        out.append(y)
    return out


def step(gain, tau):
    n = int(4 / DT)
    st = [0.0 if i * DT < 1 else 30.0 for i in range(n)]
    yaw = first_order([gain * s for s in st], tau)
    return integrate([{"time_s": i * DT, "speed_mps": 60 / 3.6, "steer_deg": st[i], "yaw_rate_dps": yaw[i],
                       "ay_mps2": math.radians(yaw[i]) * 60 / 3.6, "az_mps2": G,
                       "steer_torque_nm": 0.1 * st[i] + 0.2 * math.radians(yaw[i]) * 60 / 3.6} for i in range(n)])


def sweep(gain, tau, seed):
    rnd = random.Random(seed)
    n = int(60 / DT)
    st, s = [], 0.0
    for _ in range(n):
        s += (rnd.gauss(0, 1) * 40 - s) * DT / 0.08  # band-limited random steer
        st.append(s)
    yaw = first_order([gain * x for x in st], tau)
    return integrate([{"time_s": i * DT, "speed_mps": 60 / 3.6, "steer_deg": st[i], "yaw_rate_dps": yaw[i],
                       "ay_mps2": math.radians(yaw[i]) * 60 / 3.6, "az_mps2": G} for i in range(n)])


def jump(air, pitch, peak):
    rows, t = [], 0.0
    while t < 3:
        if 1.0 <= t < 1.0 + air:
            az, p = 0.0, pitch * (t - 1.0) / air
        elif 1.0 + air <= t < 1.1 + air:
            az, p = peak * G, pitch
        else:
            az, p = G, 0.0
        rows.append({"time_s": t, "speed_mps": 20.0, "az_mps2": az, "pitch_deg": p})
        t += DT
    return integrate(rows)


def build(root, grip_bias):
    rnd = random.Random(1)

    def jit(x, s=0.01):
        return x * (1 + rnd.uniform(-s, s))
    for k in range(3):
        write(f"{root}/circle/packed/real/{k}.csv", circle(jit(0.8), jit(40)))
        write(f"{root}/circle/packed/sim/{k}.csv", circle(0.8 * 1.03 * grip_bias, 40 * 1.05))
        for cond, g in (("packed", 0.75), ("loose", 0.6)):
            write(f"{root}/brake/{cond}/real/{k}.csv", brake(jit(g), 80 / 3.6))
            write(f"{root}/brake/{cond}/sim/{k}.csv", brake(g * 1.02 * grip_bias, 80 / 3.6))
            write(f"{root}/traction/{cond}/real/{k}.csv", traction(jit(g)))
            write(f"{root}/traction/{cond}/sim/{k}.csv", traction(g * 1.01 * grip_bias))
        write(f"{root}/step_steer/packed/real/{k}.csv", step(jit(0.5), jit(0.15)))
        write(f"{root}/step_steer/packed/sim/{k}.csv", step(0.5 * 1.05 * grip_bias, 0.16))
        write(f"{root}/sweep/packed/real/{k}.csv", sweep(0.5, 0.15, k))
        write(f"{root}/sweep/packed/sim/{k}.csv", sweep(0.5 * 1.05 * grip_bias, 0.16, 10 + k))
        write(f"{root}/jump/packed/real/{k}.csv", jump(jit(0.6), jit(-4), jit(3.0)))
        write(f"{root}/jump/packed/sim/{k}.csv", jump(0.62, -4.5, 3.2))


def main():
    grip_checks = {("circle", "max_ay_g"), ("brake", "stop_distance_m"), ("brake", "mean_decel_g"),
                   ("step_steer", "yaw_gain_dps_per_deg")}
    ok = True
    for bias, expect in ((1.0, True), (1.25, False)):
        with tempfile.TemporaryDirectory() as root:
            build(root, bias)
            _spec, results = vdat.run(SPEC, root)
        for r in results:
            if r["pass"] is None:
                continue  # tests this self-test has no runs for
            if not expect and (r["test"], r["metric"]) not in grip_checks:
                continue  # with the grip off, only the grip checks have a known answer
            want = expect
            if r["pass"] != want:
                ok = False
                print(f"bias {bias}: {r['test']} {r['condition']} {r['metric']}: pass={r['pass']}, wanted {want}, "
                      f"{r.get('note') or (r.get('value'), r.get('ref'), r.get('gap'))}")
    print("selftest", "ok" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
