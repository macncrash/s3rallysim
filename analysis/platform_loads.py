"""Motion-platform loads for the S3 Rally Pod, from the STEVE mesh export and the occupant model.

Usage: python3 platform_loads.py <bodies_mesh_dir> <cad_source_dir>

Each body's mass, centre of mass and inertia come from the export's manifest (exact CAD volume x
library density). Occupants are added as lumped masses from ergo.py, so mixed crews (a 95th
percentile driver with a 5th percentile or empty passenger seat) can be compared.

For each axis it reports the moved mass and inertia, the static load at the stop, and the peak
actuator force or torque for the cueing targets below. Targets are typical of compact rally/race
motion rigs; change them to the cueing spec once the motion software is chosen.
"""

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
    "roll_stop": math.radians(7),
    "pitch_stop": math.radians(7),
}
ROLL_AXIS_Z = 0.118  # m
PITCH_AXIS_Z = 0.176  # m

# Which instances each axis carries (outermost axis carries everything inside it).
HEAVE = {
    "deck", "heave_rod_l", "heave_rod_r", "seat_d", "seat_c", "mount_driver", "mount_codriver", "wheel",
    "dash", "pedals", "footrest", "tunnel", "dogbox", "dog_cap", "lever", "knob", "handbrake", "hb_lever",
    "button_box",
}
PITCH = HEAVE | {"pitch_cradle", "heave_body_l", "heave_body_r"}
ROLL = PITCH | {"roll_cradle"}
SURGE = ROLL | {"sled", "surge_rod"}
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
        m = mp["volume_mm3"] * rho * 1e-6  # kg
        com = [c * 1e-3 for c in mp["center_of_mass_mm"]]
        # inertia_mm5 is the volume's second moment about the com (mm^5); x density -> kg m^2.
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
        perp2 = sum(v * v for v in r) - along * along
        i_tot += own + m * perp2
    return m_tot, com, i_tot


def case(rigid, ergo, crew):
    occ = [occupant(ergo, pct, role) for role, pct in crew.items() if pct]
    rows = {}
    heave = [b for b in rigid if b[0] in HEAVE] + occ
    m, com, _ = about_axis(heave, (0, 0, 1), (0, 0, 0))
    rows["heave"] = {"mass_kg": m, "force_N": m * (G + TARGETS["heave_acc"]), "static_N": m * G,
                     "com_mm": [round(c * 1000) for c in com]}
    for name, members, axis, z, alpha, stop, lever in (
        ("pitch", PITCH, (0, 1, 0), PITCH_AXIS_Z, TARGETS["pitch_alpha"], TARGETS["pitch_stop"], 0),
        ("roll", ROLL, (1, 0, 0), ROLL_AXIS_Z, TARGETS["roll_alpha"], TARGETS["roll_stop"], 1),
    ):
        bodies = [b for b in rigid if b[0] in members] + occ
        m, com, inertia = about_axis(bodies, axis, (0, 0, z))
        # Gravity torque at the stop: the com's offset from the axis, turned by the stop angle.
        horiz = com[lever] if name == "roll" else com[0]
        height = com[2] - z
        static = m * G * abs(horiz)
        at_stop = m * G * (abs(horiz) * math.cos(stop) + height * math.sin(stop))
        rows[name] = {"mass_kg": m, "inertia_kgm2": inertia, "static_Nm": static, "gravity_at_stop_Nm": at_stop,
                      "peak_Nm": inertia * alpha + at_stop, "com_mm": [round(c * 1000) for c in com]}
    bodies = [b for b in rigid if b[0] in SURGE] + occ
    m, com, _ = about_axis(bodies, (1, 0, 0), (0, 0, 0))
    rows["surge"] = {"mass_kg": m, "force_N": m * TARGETS["surge_acc"]}
    return rows


def main():
    mesh_dir, src = sys.argv[1], sys.argv[2]
    sys.path.insert(0, src)
    import ergo  # noqa: E402  (needs the CAD source on the path)
    with open(os.path.join(mesh_dir, "manifest.json")) as fh:
        rigid = point_masses(json.load(fh))
    crews = {
        "95 + 95": {"driver": 95, "codriver": 95},
        "95 + 5": {"driver": 95, "codriver": 5},
        "95 alone": {"driver": 95, "codriver": None},
        "5 alone": {"driver": 5, "codriver": None},
    }
    out = {label: case(rigid, ergo, crew) for label, crew in crews.items()}
    print(json.dumps(out, indent=1, default=lambda v: round(v, 1)))


if __name__ == "__main__":
    main()
