"""Motion-platform loads for the S3 Rally Pod, from the STEVE mesh export and the occupant model.

Usage: python3 platform_loads.py <bodies_mesh_dir> <cad_source_dir>

Each body's mass, centre of mass and inertia come from the export's manifest (exact CAD volume x
library density). Occupants are added as lumped masses from ergo.py, so mixed crews (a 95th
percentile driver with a 5th percentile or empty passenger seat) can be compared.

The floor (and everything on it, plus the heave sleeve and the universal joint, whose weight the
floor carries) is lifted by four corner actuators; the centre post takes the side and fore-aft
loads. For each crew it reports the moved mass and inertia about the universal joint, then every
actuator's force for each combination of the cueing targets below (shared as four equal springs
would share it), the peak crank torque, and the centre post's side load.
Targets are typical of compact rally/race motion rigs; change them to the cueing spec once the
motion software is chosen.
"""

import itertools
import json
import math
import os
import sys

G = 9.81
TARGETS = {
    "heave_acc": 1.0 * G,  # m/s^2 peak, landing / bump onset
    "surge_acc": 0.6 * G,  # m/s^2 peak, braking / launch onset
    "roll_alpha": math.radians(400),  # rad/s^2 peak
    "pitch_alpha": math.radians(400),  # rad/s^2 peak
}

# What the corner actuators carry, and what the surge drive moves. The yaw restraint's block rides its rail freely
# up and down, so the floor carries it through the rod end.
FLOOR = {
    "deck", "heave_car", "ujoint", "yaw_block", "seat_d", "seat_c", "mount_driver", "mount_codriver", "wheel", "dash", "pedals",
    "footrest", "tunnel", "dogbox", "dog_cap", "lever", "knob", "handbrake", "hb_lever", "button_box",
}
SURGE = FLOOR | {"sled", "drive_fl", "drive_fr", "drive_rl", "drive_rr", "crank_fl", "crank_fr", "crank_rl",
                 "crank_rr", "link_fl", "link_fr", "link_rl", "link_rr"}
OCCUPANTS = {"driver", "codriver"}


def point_masses(manifest):
    """(instance, mass kg, com m, inertia about own com kg m^2 as 3x3) per body with a material."""
    out = []
    for item in manifest["items"]:
        if item["instance"] in OCCUPANTS:
            continue  # mannequin solids are foam stand-ins; their mass is lumped below
        mp = item.get("mass_properties") or {}
        rho = item.get("density_g_cm3")
        if not rho or "volume_mm3" not in mp:
            continue
        m = mp["volume_mm3"] * rho * 1e-6
        com = [c * 1e-3 for c in mp["center_of_mass_mm"]]
        inertia = [[v * rho * 1e-6 * 1e-6 for v in row] for row in mp["inertia_mm5"]]
        out.append((item["instance"], m, com, inertia))
    return out


def occupant(ergo, pct, role):
    p = ergo.posture(pct, role)
    b = ergo.BODY[pct]
    m = p["mass_kg"]
    dx, dy, dz = 0.30, 2 * b["shoulder_half"] * 1e-3, b["torso"] * 1e-3
    inertia = [[m / 12 * (dy * dy + dz * dz), 0, 0], [0, m / 12 * (dx * dx + dz * dz), 0],
               [0, 0, m / 12 * (dx * dx + dy * dy)]]
    return (role, m, [c * 1e-3 for c in p["com"]], inertia)


def about_axis(bodies, axis, through):
    """Mass, com and moment of inertia about a line through `through` along unit `axis`."""
    m_tot = sum(b[1] for b in bodies)
    com = [sum(b[1] * b[2][i] for b in bodies) / m_tot for i in range(3)]
    i_tot = 0.0
    for _name, m, c, inertia in bodies:
        own = sum(axis[i] * inertia[i][j] * axis[j] for i in range(3) for j in range(3))
        r = [c[i] - through[i] for i in range(3)]
        along = sum(r[i] * axis[i] for i in range(3))
        i_tot += own + m * (sum(v * v for v in r) - along * along)
    return m_tot, com, i_tot


def share(points, fz, my, mx):
    """Four vertical actuator forces giving total fz, moment my about the pivot's Y axis (from x
    offsets) and mx about its X axis (from y offsets), shared as four equal springs would."""
    # Minimum-norm solution of A f = b, A = [[1...], [dx...], [y...]].
    rows = [[1.0] * 4, [p[0] for p in points], [p[1] for p in points]]
    aat = [[sum(rows[i][k] * rows[j][k] for k in range(4)) for j in range(3)] for i in range(3)]
    rhs = [fz, my, mx]
    # Solve the 3x3 by Gaussian elimination.
    m = [row[:] + [rhs[i]] for i, row in enumerate(aat)]
    for c in range(3):
        piv = max(range(c, 3), key=lambda r: abs(m[r][c]))
        m[c], m[piv] = m[piv], m[c]
        for r in range(3):
            if r != c:
                f = m[r][c] / m[c][c]
                m[r] = [m[r][k] - f * m[c][k] for k in range(4)]
    lam = [m[i][3] / m[i][i] for i in range(3)]
    return [sum(rows[i][k] * lam[i] for i in range(3)) for k in range(4)]


def case(rigid, ergo, motion, crew):
    occ = [occupant(ergo, pct, role) for role, pct in crew.items() if pct]
    pivot = (motion.pivot_x * 1e-3, 0.0, motion.pivot_z * 1e-3)
    floor = [b for b in rigid if b[0] in FLOOR] + occ
    m, com, i_pitch = about_axis(floor, (0, 1, 0), pivot)
    _, _, i_roll = about_axis(floor, (1, 0, 0), pivot)
    m_surge = sum(b[1] for b in rigid if b[0] in SURGE) + sum(o[1] for o in occ)
    dx, dy, dz = com[0] - pivot[0], com[1], com[2] - pivot[2]
    points = [((x - motion.pivot_x) * 1e-3, y * 1e-3) for _n, x, y in motion.ACTUATORS]
    names = [n for n, _x, _y in motion.ACTUATORS]

    peak = {n: 0.0 for n in names}
    low = {n: 1e9 for n in names}
    post = 0.0
    t = TARGETS
    for sh, ss, sp, sr in itertools.product((-1, 0, 1), repeat=4):
        az, ax = sh * t["heave_acc"], ss * t["surge_acc"]
        ap, ar = sp * t["pitch_alpha"], sr * t["roll_alpha"]
        fz = m * (G + az)
        # Moments the actuators must supply about the universal joint: weight and vertical
        # acceleration through the com's offset, surge acceleration through its height, and the
        # angular accelerations through the inertias.
        my = fz * dx + m * ax * dz + i_pitch * ap
        mx = fz * dy + i_roll * ar
        for n, f in zip(names, share(points, fz, my, mx)):
            peak[n] = max(peak[n], f)
            low[n] = min(low[n], f)
        # Side and fore-aft load on the centre post: surge, plus roll and pitch acceleration of the
        # com about the joint.
        post = max(post, math.hypot(m * ax + m * ap * dz, m * ar * dz))
    static = share(points, m * G, m * G * dx, m * G * dy)
    r = motion.crank_r * 1e-3
    return {
        "floor_mass_kg": round(m, 1),
        "floor_com_mm": [round(c * 1000) for c in com],
        "com_from_pivot_mm": [round(dx * 1000), round(dy * 1000), round(dz * 1000)],
        "inertia_pitch_kgm2": round(i_pitch, 1),
        "inertia_roll_kgm2": round(i_roll, 1),
        "surge_mass_kg": round(m_surge, 1),
        "surge_force_N": round(m_surge * t["surge_acc"]),
        "actuator_static_N": {n: round(f) for n, f in zip(names, static)},
        "actuator_peak_N": {n: round(peak[n]) for n in names},
        "actuator_min_N": {n: round(low[n]) for n in names},
        "crank_peak_Nm": round(max(max(peak.values()), -min(low.values())) * r),
        "crank_static_Nm": round(max(abs(f) for f in static) * r),
        "post_side_load_N": round(post),
    }


def main():
    mesh_dir, src = sys.argv[1], sys.argv[2]
    sys.path.insert(0, src)
    import ergo  # noqa: E402  (the CAD source must be on the path)
    import motion  # noqa: E402
    import params  # noqa: E402
    motion.pivot_x, motion.pivot_z = params.pivot_x, params.pivot_z
    with open(os.path.join(mesh_dir, "manifest.json")) as fh:
        rigid = point_masses(json.load(fh))
    crews = {
        "95 + 95": {"driver": 95, "codriver": 95},
        "95 + 5": {"driver": 95, "codriver": 5},
        "95 alone": {"driver": 95, "codriver": None},
        "5 alone": {"driver": 5, "codriver": None},
    }
    out = {"targets": {k: round(v, 3) for k, v in TARGETS.items()},
           "crews": {label: case(rigid, ergo, motion, crew) for label, crew in crews.items()}}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
