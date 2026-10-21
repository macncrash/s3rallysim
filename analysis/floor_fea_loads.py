"""Load cases for the moving floor's STEVE structural studies (cad/fea/floor_frame.py).

Usage: python3 floor_fea_loads.py <bodies_mesh_dir> <cad_source_dir> > floor_fea_loads.json

Each cockpit group (a seat with its rails and occupant, the dash frame with the wheel, the pedal box,
the footrest, the tunnel) bolts to the floor at a set of pads. For every case the group's inertial
load, m (g - a) with a = a_lin + alpha x r about the universal joint, acts at the group's centre of
mass; it is moved to the pads as the force and couple that bolts would carry, shared min-norm between
them. The floor's own mass is the study's gravity. The heave sleeve and spider hang on the yoke bores.

Supports in the studies: the eight clevis bores hold the floor vertically (the links), the two yoke
bores hold it sideways and fore-aft (the centre post); see docs/floor-structure.md.

Masses come from the CAD export as in platform_loads.py, with two changes: occupants from ergo.py,
and the pedal box at the Heusinkveld set's 6.6 kg instead of the CAD's 4.4 kg.
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import platform_loads as pl  # noqa: E402

G = 9.81
BRAKE_N = 1765  # Heusinkveld Ultimate+ brake load cell maximum, 180 kg
BRACE_N = 1000  # co-driver bracing on the footrest through a landing
PEDALS_KG = 6.6

# Pad ids (cad/fea/floor_frame.py) and their centres on the sheet top, mm.
TOP = 511
SEAT_D = {"sd_ir": (-512.7, 160), "sd_if": (77.3, 160), "sd_or": (-512.7, 500), "sd_of": (77.3, 500)}
SEAT_C = {"sc_ir": (-512.7, -160), "sc_if": (77.3, -160), "sc_or": (-512.7, -500), "sc_of": (77.3, -500)}
DASH = {"dash_lf": (301.7, 615), "dash_lb": (241.7, 615), "dash_cf": (301.7, 0), "dash_cb": (241.7, 0),
        "dash_rf": (301.7, -615), "dash_rb": (241.7, -615)}
PEDALS = {"ped_fl": (710, 440), "ped_fr": (710, 220), "ped_rl": (430, 440), "ped_rr": (430, 220)}
FOOT = {"foot_fl": (590, -180), "foot_fr": (590, -480), "foot_rl": (450, -180), "foot_rr": (450, -480)}
TUNNEL = {"tunnel": (-60, 50)}

GROUPS = {
    "seat_d": ({"seat_d", "mount_driver"}, "driver", SEAT_D),
    "seat_c": ({"seat_c", "mount_codriver"}, "codriver", SEAT_C),
    "dash": ({"dash", "wheel"}, None, DASH),
    "pedals": ({"pedals"}, None, PEDALS),
    "footrest": ({"footrest"}, None, FOOT),
    "tunnel": ({"tunnel", "dogbox", "dog_cap", "lever", "knob", "handbrake", "hb_lever", "button_box"}, None, TUNNEL),
}
HANGING = {"heave_car", "ujoint"}  # carried by the yoke bores


def solve(a, b):
    """Gaussian elimination with partial pivoting."""
    n = len(b)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(m[r][c]))
        m[c], m[piv] = m[piv], m[c]
        for r in range(n):
            if r != c and m[c][c]:
                f = m[r][c] / m[c][c]
                m[r] = [m[r][k] - f * m[c][k] for k in range(n + 1)]
    return [m[i][n] / m[i][i] for i in range(n)]


def to_pads(force, at, pads):
    """Pad forces (N) carrying `force` (N) acting at `at` (mm): equal shares plus the couple, min-norm."""
    names = list(pads)
    if len(names) == 1:
        return {names[0]: force}
    pts = [(pads[n][0] * 1e-3, pads[n][1] * 1e-3, TOP * 1e-3) for n in names]
    cen = [sum(p[i] for p in pts) / len(pts) for i in range(3)]
    r0 = [at[i] * 1e-3 - cen[i] for i in range(3)]
    moment = [r0[1] * force[2] - r0[2] * force[1], r0[2] * force[0] - r0[0] * force[2],
              r0[0] * force[1] - r0[1] * force[0]]
    # Rows: sum of forces (3) and sum of moments about the centroid (3); unknowns fx, fy, fz per pad.
    rows = [[0.0] * (3 * len(names)) for _ in range(6)]
    for k, p in enumerate(pts):
        r = [p[i] - cen[i] for i in range(3)]
        for i in range(3):
            rows[i][3 * k + i] = 1.0
        # r x f = (ry fz - rz fy, rz fx - rx fz, rx fy - ry fx)
        rows[3][3 * k + 2], rows[3][3 * k + 1] = r[1], -r[2]
        rows[4][3 * k + 0], rows[4][3 * k + 2] = r[2], -r[0]
        rows[5][3 * k + 1], rows[5][3 * k + 0] = r[0], -r[1]
    rhs = list(force) + moment
    keep = [i for i in range(6) if any(abs(v) > 1e-9 for v in rows[i])]
    aat = [[sum(rows[i][k] * rows[j][k] for k in range(len(rows[0]))) for j in keep] for i in keep]
    # A tiny ridge keeps the normal equations solvable when the pads are collinear.
    for i in range(len(keep)):
        aat[i][i] += 1e-12
    lam = solve(aat, [rhs[i] for i in keep])
    f = [sum(rows[keep[j]][k] * lam[j] for j in range(len(keep))) for k in range(len(rows[0]))]
    return {n: [f[3 * k], f[3 * k + 1], f[3 * k + 2]] for k, n in enumerate(names)}


def cross(u, v):
    return [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]


def cases():
    t = pl.TARGETS
    return {
        # Landing: 1 g of heave on top of gravity.
        "landing": {"a_lin": [0, 0, t["heave_acc"]], "alpha": [0, 0, 0], "extra": False},
        # Every cueing target at once: heave, surge, roll and pitch kicks.
        "combined": {"a_lin": [-t["surge_acc"], 0, t["heave_acc"]], "alpha": [t["roll_alpha"], t["pitch_alpha"], 0],
                     "extra": False},
        # Static, with the driver at full brake and the co-driver bracing.
        "brake": {"a_lin": [0, 0, 0], "alpha": [0, 0, 0], "extra": True},
    }


def build(rigid, ergo, crew):
    pivot = (pl_pivot[0], 0.0, pl_pivot[1])
    by_inst = {}
    for name, m, com, _i in rigid:
        if name == "pedals":
            m = PEDALS_KG
        by_inst.setdefault(name, []).append((m, [c * 1e3 for c in com]))
    occ = {role: pl.occupant(ergo, pct, role) for role, pct in crew.items() if pct}
    out = {}
    for cname, c in cases().items():
        loads = {}
        for gname, (insts, role, pads) in GROUPS.items():
            parts = [p for i in insts for p in by_inst.get(i, [])]
            if role in occ:
                parts.append((occ[role][1], [v * 1e3 for v in occ[role][2]]))
            m = sum(p[0] for p in parts)
            com = [sum(p[0] * p[1][i] for p in parts) / m for i in range(3)]
            r = [(com[i] - pivot[i]) * 1e-3 for i in range(3)]
            a = [c["a_lin"][i] + cross(c["alpha"], r)[i] for i in range(3)]
            force = [m * (-a[0]), m * (-a[1]), m * (-G - a[2])]
            for pad, f in to_pads(force, com, pads).items():
                loads[pad] = [loads.get(pad, [0, 0, 0])[i] + f[i] for i in range(3)]
        if c["extra"]:
            # Brake: the foot pushes the pedal face (60 deg sole) forward and down; the driver's back
            # pushes the seat the other way. Both act about 190 mm above the sheet at the pedal and
            # 300 mm up the seat back.
            push = [BRAKE_N * math.cos(math.radians(30)), 0, -BRAKE_N * math.sin(math.radians(30))]
            for pad, f in to_pads(push, (570, 330, TOP + 190), PEDALS).items():
                loads[pad] = [loads[pad][i] + f[i] for i in range(3)]
            for pad, f in to_pads([-v for v in push], (-560, 330, TOP + 300), SEAT_D).items():
                loads[pad] = [loads[pad][i] + f[i] for i in range(3)]
            brace = [BRACE_N * math.cos(math.radians(30)), 0, -BRACE_N * math.sin(math.radians(30))]
            for pad, f in to_pads(brace, (560, -330, TOP + 190), FOOT).items():
                loads[pad] = [loads[pad][i] + f[i] for i in range(3)]
            for pad, f in to_pads([-v for v in brace], (-560, -330, TOP + 300), SEAT_C).items():
                loads[pad] = [loads[pad][i] + f[i] for i in range(3)]
        m_hang = sum(p[0] for i in HANGING for p in by_inst.get(i, []))
        hang = -m_hang * (G + c["a_lin"][2])
        a0 = c["a_lin"]
        out[cname] = {
            "gravity_m_s2": [round(-a0[0], 3), round(-a0[1], 3), round(-G - a0[2], 3)],
            "pads_N": {k: [round(v, 1) for v in f] for k, f in loads.items()},
            "yoke_bores_z_N": round(hang / 2, 1),
            "total_N": [round(sum(f[i] for f in loads.values()) + (hang if i == 2 else 0), 1) for i in range(3)],
        }
    return out


pl_pivot = (-300, 430)
POST_FOOT_Z = 168  # mm column foot: carriage column plate top
HEAVE_STOP = 40  # mm the post is checked at the top stop, its shortest sleeve engagement
CARRIAGE = {"fl": (-250, 50), "fr": (-250, -50), "rl": (-350, 50), "rr": (-350, -50)}  # cad/fea/carriage.py pads


def centre_post(rigid, ergo, crew):
    """The post's peak side load (platform_loads.py's worst combination: surge plus pitch and roll kicks) at
    the universal joint, and the force and moment it puts on the carriage's column plate."""
    occ = [pl.occupant(ergo, pct, role) for role, pct in crew.items() if pct]
    pivot = (pl_pivot[0] * 1e-3, 0.0, pl_pivot[1] * 1e-3)
    floor = [b for b in rigid if b[0] in pl.FLOOR] + occ
    m, com, _i = pl.about_axis(floor, (0, 1, 0), pivot)
    dz = com[2] - pivot[2]
    t = pl.TARGETS
    fx = m * (t["surge_acc"] + t["pitch_alpha"] * dz)
    fy = m * t["roll_alpha"] * dz
    at = (pl_pivot[0], 0.0, pl_pivot[1] + HEAVE_STOP)
    global TOP
    top, TOP = TOP, POST_FOOT_Z  # to_pads works on a pad plane at TOP
    try:
        pads = to_pads([fx, fy, 0.0], at, CARRIAGE)
    finally:
        TOP = top
    arm = (at[2] - POST_FOOT_Z) * 1e-3
    return {
        "joint_force_N": [round(fx), round(fy), 0],
        "joint_z_mm": at[2],
        "foot_moment_Nm": [round(-arm * fy), round(arm * fx), 0],
        "carriage_pads_N": {k: [round(v, 1) for v in f] for k, f in pads.items()},
    }


def main():
    mesh_dir, src = sys.argv[1], sys.argv[2]
    sys.path.insert(0, src)
    import ergo  # noqa: E402
    import params  # noqa: E402
    global pl_pivot
    pl_pivot = (params.pivot_x, params.pivot_z)
    with open(os.path.join(mesh_dir, "manifest.json")) as fh:
        rigid = pl.point_masses(json.load(fh))
    crew = {"driver": 95, "codriver": 95}
    print(json.dumps({"crew": "95 + 95", "cases": build(rigid, ergo, crew),
                      "centre_post": centre_post(rigid, ergo, crew)}, indent=1))


if __name__ == "__main__":
    main()
