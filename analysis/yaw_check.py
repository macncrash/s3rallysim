"""Floor yaw mode check for the S3 Rally Pod: does an off-centre crew excite it?

Usage: python3 yaw_check.py <bodies_mesh_dir> <cad_source_dir> <k_yaw_steel_Nm_per_rad> [<k_restraint_steel_N_per_m>]

The modal study (docs/floor-structure.md §2.5) leaves one low mode: the floor yawing about the universal joint,
with nothing but the joint, crosshead and heave guide to hold it. No cue drives yaw, but the crew's centre of mass is
off the joint, so surge, pitch and roll cues push on it sideways and twist the floor:

    T = m [ (a_surge + alpha_pitch dz) |dy| + alpha_roll dz |dx| ]

with (dx, dy, dz) the floor's centre of mass from the joint (the signs combined for the worst case). The floor is
taken as rigid on one yaw spring with structural damping zeta. The spring is the joint path k (from a STEVE static
study of the platform modal part: a couple on the floor's side faces), plus, with fix I, the yaw restraint's
sideways stiffness at its pin times the pin's distance from the joint squared (STEVE study of the yaw post part).
The steel and 6061 moduli bound both, as for the other studies.

For each crew it reports the yaw inertia about the joint, the natural frequency, and the false sideways
acceleration at the crew's seats (the yaw spring's motion, not commanded by any cue):
- static: the floor's twist and the seats' sideways shift under the peak cue (all axes at once);
- onset: the ringing left after a cue ramps up over a rise time t_r (the residual of a ramp input on an undamped
  oscillator, |sin(w t_r / 2) / (w t_r / 2)| times the static twist), for the peak surge cue alone;
- resonance: the false sideways acceleration per 0.1 g of surge content right at the yaw frequency.
Compared with ISO 2631-1 Annex C: about 0.015 m/s2 peak is the threshold of perception, 0.315 m/s2 rms "not
uncomfortable".

The mesh is the last bodies_mesh export (render/build/mesh); the floor parts added since (fixes G and H) are added
here as point masses. The links' horizontal stiffness, which would raise the frequency, is left out.
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import platform_loads as pl  # noqa: E402

ZETA = 0.02  # structural damping, bolted steel and aluminium frame
RISE_S = (0.05, 0.1, 0.2)  # cue onset rise times
PERCEIVE = 0.015  # m/s2 peak, ISO 2631-1 Annex C
E_RATIO = 69 / 210  # 6061 / steel modulus

# Floor parts added since the mesh export, as (name, kg, (x, y, z) mm, yaw inertia about their own centre kg m2):
# fixes H and G. 6061 cross tubes 40 x 60 x 4 at 1.99 kg/m, steel yoke bars 20 x 60 x 240, 6061 runner bars
# 20 x 40 x 670 and edge tubes 40 x 40 x 4 x 480.
EXTRA = [
    ("yoke tubes", 2 * 2.47, (-300, 0, 477), 2 * 2.47 * 1.24 ** 2 / 12 + 2 * 2.47 * 0.14 ** 2),
    ("yoke bars", 2 * 2.26, (-300, 0, 477), 2 * 2.26 * (0.24 ** 2 / 12 + 0.075 ** 2)),
    ("front cross tubes", 3 * 2.47, (437, 0, 477), 3 * 2.47 * 1.24 ** 2 / 12),
    ("runner bars", 2 * 1.45, (465, 0, 427), 2 * 1.45 * (0.67 ** 2 / 12 + 0.32 ** 2)),
    ("edge tubes", 2 * 0.75, (510, 0, 427), 2 * 0.75 * (0.48 ** 2 / 12 + 0.64 ** 2)),
]


def yaw_case(rigid, ergo, motion, crew, k):
    """k: the yaw spring in steel, N m/rad."""
    occ = [pl.occupant(ergo, pct, role) for role, pct in crew.items() if pct]
    pivot = (motion.pivot_x * 1e-3, 0.0, motion.pivot_z * 1e-3)
    floor = [b for b in rigid if b[0] in pl.FLOOR] + occ
    for name, m, c, i_own in EXTRA:
        floor.append((name, m, [v * 1e-3 for v in c], [[0, 0, 0], [0, 0, 0], [0, 0, i_own]]))
    m, com, i_yaw = pl.about_axis(floor, (0, 0, 1), pivot)
    dx, dy, dz = com[0] - pivot[0], com[1], com[2] - pivot[2]
    t = pl.TARGETS
    torque = m * ((t["surge_acc"] + t["pitch_alpha"] * dz) * abs(dy) + t["roll_alpha"] * dz * abs(dx))
    torque_surge = m * t["surge_acc"] * abs(dy)
    # The seats: the occupants' own centres of mass, or the driver's seat for an empty one.
    seats = [math.hypot(o[2][0] - pivot[0], o[2][1]) for o in occ]
    r = max(seats)
    out = {"floor_mass_kg": round(m, 1), "com_from_pivot_mm": [round(v * 1000) for v in (dx, dy, dz)],
           "yaw_inertia_kgm2": round(i_yaw, 1), "seat_radius_m": round(r, 3),
           "peak_yaw_torque_Nm": round(torque), "surge_only_yaw_torque_Nm": round(torque_surge)}
    for label, kk in (("steel", k), ("6061", k * E_RATIO)):
        w = math.sqrt(kk / i_yaw)
        static = torque / kk
        res = {"f_hz": round(w / 2 / math.pi, 1),
               "static_twist_mrad": round(static * 1e3, 2),
               "static_seat_shift_mm": round(static * r * 1e3, 2)}
        for tr in RISE_S:
            x = w * tr / 2
            ring = (torque_surge / kk) * abs(math.sin(x) / x)
            res[f"onset_{int(tr * 1000)}ms_ring_m_s2"] = round(ring * w ** 2 * r, 3)
        # At resonance: the twist is Q = 1 / (2 zeta) times the static twist for 0.1 g of surge content.
        res["resonance_per_0.1g_m_s2"] = round(m * 0.981 * abs(dy) / kk / (2 * ZETA) * w ** 2 * r, 2)
        out[label] = res
    return out


def main():
    mesh_dir, src, k_joint = sys.argv[1], sys.argv[2], float(sys.argv[3])
    k_restraint = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
    sys.path.insert(0, src)
    import ergo  # noqa: E402
    import motion  # noqa: E402
    import params  # noqa: E402
    motion.pivot_x, motion.pivot_z = params.pivot_x, params.pivot_z
    arm = (params.pivot_x - motion.YAW_PIN_X) * 1e-3 if k_restraint else 0.0
    k = k_joint + k_restraint * arm ** 2
    with open(os.path.join(mesh_dir, "manifest.json")) as fh:
        rigid = pl.point_masses(json.load(fh))
    crews = {
        "95 + 95": {"driver": 95, "codriver": 95},
        "95 + 5": {"driver": 95, "codriver": 5},
        "95 alone": {"driver": 95, "codriver": None},
        "5 alone": {"driver": 5, "codriver": None},
    }
    out = {"k_joint_steel_Nm_per_rad": k_joint, "k_restraint_steel_N_per_m": k_restraint, "restraint_arm_m": arm,
           "k_yaw_steel_Nm_per_rad": round(k), "zeta": ZETA, "perception_m_s2": PERCEIVE,
           "crews": {label: yaw_case(rigid, ergo, motion, crew, k) for label, crew in crews.items()}}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
