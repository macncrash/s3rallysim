"""Seated occupant in race gear, built from an ergo.posture() into a Component.

Capsule limbs, a torso block on the seat-back line, an FIA closed-face helmet with an intercom
boom mic, a HANS yoke on the shoulders with tethers to the helmet, gloves, boots and harness straps.
Modelled in the design frame. Mass comes from a lumped mass in main.py, not from these solids.
"""

import math

import ergo
from ergo import BODY, add, sub, mul, unit, norm, SOLE, SOLE_DEG, RAKE

FOAM = "eps-foam"


def _capsule(c, cid, a, b, r, end_a=True, end_b=True):
    d = sub(b, a)
    c.cylinder(cid, r, norm(d), at=a, direction=unit(d), op="new")
    if end_a:
        c.sphere(cid + "_a", r, at=a, op="join", body=cid)
    if end_b:
        c.sphere(cid + "_b", r, at=b, op="join", body=cid)


def _tilted_box(c, cid, length, width, height, centre, deg):
    """Box tilted about a Y axis through its centre: +deg turns its top toward -X and its front up."""
    c.box(cid, length, width, height, at=centre, op="new")
    c.move(cid + "_tilt", [cid], rotate=((centre, (0, 1, 0)), -deg))


def build(c, pct, role, suit):
    p = ergo.posture(pct, role)
    b = BODY[pct]
    r = math.radians(RAKE)
    fwd = (math.cos(r), 0.0, math.sin(r))  # perpendicular to the back, toward the wheel
    up = p["torso_dir"]
    hip, neck, head = p["hip"], p["neck"], p["head"]
    half = b["shoulder_half"]

    # Pelvis and trunk on the seat-back line.
    c.cylinder("pelvis", b["r_thigh"] + 18, 2 * (b["hip_half"] + 40), at=add(hip, (0, -(b["hip_half"] + 40), 0)),
               direction=(0, 1, 0), op="new")
    trunk = b["torso"] - 40
    _tilted_box(c, "torso", b["chest"], 2 * half + 30, trunk, add(add(hip, mul(up, trunk / 2 + 10)), mul(fwd, 10)),
                RAKE)
    _capsule(c, "neck", add(neck, mul(up, -30)), add(head, (20, 0, -60)), 52)

    # Helmet, visor, chin bar and intercom boom mic.
    hr = b["helmet"]
    c.sphere("helmet", hr, at=head, op="new")
    eye = p["eye"]
    c.box("visor", 30, 2 * hr * 0.7, hr * 0.42, at=add(eye, (hr * 0.62 - 25, 0, 6)), op="new")
    c.box("chin", 70, 2 * hr * 0.6, hr * 0.4, at=add(head, (hr * 0.72, 0, -hr * 0.55)), op="new")
    mic_root = add(head, (hr * 0.35, 0.82 * hr, -hr * 0.45))
    mouth = add(head, (hr * 0.98, 0.18 * hr, -hr * 0.42))
    _capsule(c, "boom_mic", mic_root, mouth, 5)
    c.sphere("mic_capsule", 11, at=mouth, op="new")

    # HANS: yoke on the upper back and two collar legs down the chest, tethered to the helmet.
    yoke_c = add(add(neck, mul(up, -40)), mul(fwd, -b["chest"] / 2 - 10))
    _tilted_box(c, "hans_yoke", 26, 2 * half * 0.55, 150, yoke_c, RAKE)
    for side, s in (("l", 1), ("r", -1)):
        top = add(add(neck, (0, s * half * 0.45, 0)), mul(up, 30))
        front = add(add(add(neck, (0, s * half * 0.38, 0)), mul(fwd, b["chest"] / 2 + 12)), mul(up, -200))
        _capsule(c, "hans_leg_" + side, add(yoke_c, (0, s * half * 0.45, 40)), top, 16)
        _capsule(c, "hans_collar_" + side, top, front, 16)
        tether_top = add(head, (-hr * 0.15, s * hr * 0.92, -hr * 0.1))
        _capsule(c, "tether_" + side, add(top, (0, 0, 10)), tether_top, 4)

    # Arms, gloves, legs, boots.
    for side, s in (("l", 1), ("r", -1)):
        _capsule(c, "upper_arm_" + side, p["shoulder_" + side], p["elbow_" + side], b["r_arm"])
        _capsule(c, "forearm_" + side, p["elbow_" + side], p["hand_" + side], b["r_forearm"], end_b=False)
        c.sphere("glove_" + side, b["r_forearm"] + 10, at=p["hand_" + side], op="new")
        _capsule(c, "thigh_" + side, p["hip_" + side], p["knee_" + side], b["r_thigh"])
        _capsule(c, "shank_" + side, p["knee_" + side], p["ankle_" + side], b["r_shank"], end_b=False)
        heel, ball = p["heel_" + side], p["ball_" + side]
        boot_len = b["heel_ball"] / 0.72
        boot_c = add(add(heel, mul(SOLE, boot_len / 2 - 10)), (-math.sin(math.radians(SOLE_DEG)) * 42, 0,
                                                                math.cos(math.radians(SOLE_DEG)) * 42))
        _tilted_box(c, "boot_" + side, boot_len, b["r_shank"] * 1.7, 80, boot_c, SOLE_DEG)
        c.sphere("ankle_" + side, b["r_shank"] + 4, at=p["ankle_" + side], op="join", body="shank_" + side)

    # Six-point harness: shoulder straps over the HANS to the lap buckle.
    buckle = add(add(hip, mul(fwd, b["r_thigh"] + 40)), (0, 0, 40))
    for side, s in (("l", 1), ("r", -1)):
        over = add(add(neck, (0, s * half * 0.42, 0)), mul(up, 40))
        _capsule(c, "strap_" + side, over, add(buckle, (0, s * 40, 0)), 9)
    c.box("buckle", 30, 70, 70, at=buckle, op="new")

    if role == "codriver":
        # Pace notes on the lap, between the hands.
        notes = add(mul(add(p["hand_l"], p["hand_r"]), 0.5), (0, 0, 15))
        _tilted_box(c, "pace_notes", 210, 150, 12, notes, 30)

    c.material(FOAM, color=suit)
    c.material(FOAM, bodies=["helmet", "chin"], color="#f2f2f2")
    c.material(FOAM, bodies=["visor"], color="#1b2a38")
    c.material(FOAM, bodies=["hans_yoke", "hans_leg_l", "hans_leg_r", "hans_collar_l", "hans_collar_r"],
               color="#2a2a2a")
    c.material(FOAM, bodies=["tether_l", "tether_r", "strap_l", "strap_r"], color="#c1121f")
    c.material(FOAM, bodies=["boom_mic", "mic_capsule", "buckle"], color="#111111")
    c.material(FOAM, bodies=["glove_l", "glove_r", "boot_l", "boot_r"], color="#151515")
    if role == "codriver":
        c.material(FOAM, bodies=["pace_notes"], color="#f4e9c8")
    return p
