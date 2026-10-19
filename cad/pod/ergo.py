"""Occupants of the S3 Rally Pod: body sizes, seated posture, and the mounts they set.

Millimetres and degrees, design frame: +X forward, +Y the driver's left, +Z up, floor stack at rest.
Body sizes are seated link lengths for a 5th percentile woman and a 95th percentile man
(approximations from ANSUR II and Pheasant's tables), wearing race gear: FIA helmet with intercom,
HANS, suit and boots.

The pedals and the wheel are placed for the 95th percentile with the seat fully back. A smaller
person lifts the cushion until they see over the rim, slides the seat forward on its rails until
the knee angle matches, then pulls the column out until the elbow angle matches.
"""

import math

from params import (
    layout, deck_top, seat_y, seat_rake, h30, heel_x, sole_deg, knee_deg, elbow_deg,
    wheel_z, wheel_tilt, wheel_r, seat_travel, seat_lift_max, column_travel, column_len,
)

rally = layout < 0.5

# Formula template: one reclined seat on the centreline, feet higher, wheel lower.
RAKE = seat_rake if rally else 38
H30 = h30 if rally else 110
DRIVER_Y = seat_y if rally else 0
WHEEL_Z = wheel_z if rally else wheel_z - 130
WHEEL_TILT = wheel_tilt if rally else 12
KNEE = knee_deg if rally else 145
SOLE_DEG = sole_deg if rally else 72
WHEEL_R = wheel_r if rally else 135
COLUMN_TRAVEL = column_travel if rally else 110

BODY = {
    5: {
        "stature": 1530, "mass_kg": 50, "gear_kg": 6,
        "thigh": 380, "shank": 385, "ankle_up": 70, "ankle_back": 17, "heel_ball": 160,
        "torso": 385, "neck_eye": 215, "upper_arm": 280, "forearm": 300,
        "shoulder_half": 175, "hip_half": 90, "hip_up": 80,
        "r_thigh": 68, "r_shank": 48, "r_arm": 42, "r_forearm": 36, "chest": 220, "helmet": 138,
    },
    95: {
        "stature": 1880, "mass_kg": 110, "gear_kg": 6,
        "thigh": 465, "shank": 470, "ankle_up": 85, "ankle_back": 21, "heel_ball": 205,
        "torso": 530, "neck_eye": 245, "upper_arm": 395, "forearm": 390,
        "shoulder_half": 210, "hip_half": 110, "hip_up": 95,
        "r_thigh": 92, "r_shank": 62, "r_arm": 56, "r_forearm": 46, "chest": 280, "helmet": 150,
    },
}

# Seat: the hip joint sits this far forward of the seat origin (cushion bottom, centre),
# and the seat origin sits on rails this high above the floor.
SEAT_HX = -95
SEAT_CUSHION = 64
SIGHT_OVER_RIM = 60  # mm eye above the rim top for a clear view of the road


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def mul(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def norm(a):
    return math.sqrt(dot(a, a))


def unit(a):
    n = norm(a)
    return (a[0] / n, a[1] / n, a[2] / n)


def angle_at(a, b, c):
    """Angle ABC in degrees."""
    u, v = unit(sub(a, b)), unit(sub(c, b))
    return math.degrees(math.acos(max(-1.0, min(1.0, dot(u, v)))))


def two_link(root, tip, l1, l2, pole):
    """Middle joint of a two-link chain from root to tip, bending toward pole. Clamped at full reach."""
    d = sub(tip, root)
    dist = min(norm(d), l1 + l2 - 1e-6)
    axis = unit(d)
    a = max(-1.0, min(1.0, (l1 * l1 + dist * dist - l2 * l2) / (2 * l1 * dist)))
    up = unit(sub(pole, mul(axis, dot(pole, axis))))
    return add(add(root, mul(axis, l1 * a)), mul(up, l1 * math.sqrt(1 - a * a)))


# Floor-hinged pedals: heel point on the heel plate, sole at sole_deg.
HEEL = (heel_x, 0.0, deck_top + 14)
SOLE = (math.cos(math.radians(SOLE_DEG)), 0.0, math.sin(math.radians(SOLE_DEG)))
WHEEL_FACE = (-math.cos(math.radians(WHEEL_TILT)), 0.0, math.sin(math.radians(WHEEL_TILT)))
WHEEL_UP = (math.sin(math.radians(WHEEL_TILT)), 0.0, math.cos(math.radians(WHEEL_TILT)))
RIM_TOP = WHEEL_Z + WHEEL_R * WHEEL_UP[2]


def ankle(pct, y):
    b = BODY[pct]
    s, c = math.sin(math.radians(SOLE_DEG)), math.cos(math.radians(SOLE_DEG))
    # Neutral ankle sits ahead of the heel and above it; the foot pitches up by sole_deg.
    ax = b["ankle_back"] * 2 * c - b["ankle_up"] * s
    az = b["ankle_back"] * 2 * s + b["ankle_up"] * c
    return (HEEL[0] + ax, y, HEEL[2] + az)


def _eye_above_hip(pct):
    b = BODY[pct]
    r = math.radians(RAKE)
    t = math.radians(RAKE - 14)
    return b["torso"] * math.cos(r) + b["neck_eye"] * math.cos(t) + 85 * math.sin(t)


def _hip_z0(pct):
    return HEEL[2] + H30 + (BODY[pct]["hip_up"] - BODY[95]["hip_up"])


def seat_lift(pct):
    """Cushion lift so the eye clears the rim top; none for the 95th percentile."""
    need = RIM_TOP + SIGHT_OVER_RIM - (_hip_z0(pct) + _eye_above_hip(pct))
    return max(0.0, min(seat_lift_max, need))


def hip_z(pct):
    return _hip_z0(pct) + seat_lift(pct)


def seat_x_for(pct):
    """Seat origin x that gives the target knee angle for this body, before the rail clamp."""
    b = BODY[pct]
    a = ankle(pct, 0.0)
    d2 = b["thigh"] ** 2 + b["shank"] ** 2 - 2 * b["thigh"] * b["shank"] * math.cos(math.radians(KNEE))
    dz = hip_z(pct) - a[2]
    return a[0] - math.sqrt(d2 - dz * dz) - SEAT_HX


SEAT_X_REAR = seat_x_for(95)


def seat_x(pct):
    return min(max(seat_x_for(pct), SEAT_X_REAR), SEAT_X_REAR + seat_travel)


def seat_z(pct):
    """Seat origin height: hip point minus the hip's height above the seat origin."""
    return hip_z(pct) - SEAT_CUSHION - BODY[pct]["hip_up"]


def shoulders(pct, y, sx):
    b = BODY[pct]
    hip = (sx + SEAT_HX, y, hip_z(pct))
    r = math.radians(RAKE)
    return hip, add(hip, (-b["torso"] * math.sin(r), 0.0, b["torso"] * math.cos(r)))


def wheel_x_for(pct, sx):
    """Wheel centre x that gives the target elbow angle with hands at quarter to three."""
    b = BODY[pct]
    _hip, sc = shoulders(pct, DRIVER_Y, sx)
    d2 = b["upper_arm"] ** 2 + b["forearm"] ** 2 - 2 * b["upper_arm"] * b["forearm"] * math.cos(
        math.radians(elbow_deg))
    dy = WHEEL_R - b["shoulder_half"]
    dz = WHEEL_Z - sc[2]
    return sc[0] + math.sqrt(max(0.0, d2 - dy * dy - dz * dz))


WHEEL_X_HOME = wheel_x_for(95, SEAT_X_REAR)
DASH = add((WHEEL_X_HOME, DRIVER_Y, WHEEL_Z), mul(WHEEL_FACE, -column_len))


def wheel_x(pct):
    return min(max(wheel_x_for(pct, seat_x(pct)), WHEEL_X_HOME), WHEEL_X_HOME + COLUMN_TRAVEL)


def grip(centre, side):
    """Rim point at quarter to three: side +1 left hand, -1 right hand."""
    return add(centre, (0.0, side * WHEEL_R, 0.0))


def posture(pct, role):
    """Joint centres for one occupant. role: "driver" or "codriver"."""
    b = BODY[pct]
    y = DRIVER_Y if role == "driver" else -seat_y
    sx = seat_x(pct)
    hip, sc = shoulders(pct, y, sx)
    r = math.radians(RAKE)
    t = math.radians(RAKE - 14)
    eye = add(sc, (-b["neck_eye"] * math.sin(t) + 85 * math.cos(t), 0.0,
                   b["neck_eye"] * math.cos(t) + 85 * math.sin(t)))
    head = add(eye, (-85, 0.0, 45))
    out = {
        "pct": pct, "role": role, "y": y, "seat_x": sx, "seat_z": seat_z(pct), "lift": seat_lift(pct),
        "hip": hip, "neck": sc, "eye": eye, "head": head, "helmet_r": b["helmet"],
        "torso_dir": (-math.sin(r), 0.0, math.cos(r)), "mass_kg": b["mass_kg"] + b["gear_kg"],
    }
    feet = {"l": 78.0, "r": -78.0}
    wc = (wheel_x(pct), DRIVER_Y, WHEEL_Z)
    for side, s in (("l", 1), ("r", -1)):
        h = add(hip, (0.0, s * b["hip_half"], 0.0))
        a = ankle(pct, y + feet[side])
        k = two_link(h, a, b["thigh"], b["shank"], (0.6, 0.0, 1.0))
        heel = (HEEL[0], a[1], HEEL[2])
        sh = add(sc, (0.0, s * b["shoulder_half"], 0.0))
        if role == "driver":
            hand = grip(wc, s)
        else:
            # Pace notes held on the lap.
            hand = add(add(mul(k, 0.55), mul(h, 0.45)), (0.0, -s * 25, 110))
        e = two_link(sh, hand, b["upper_arm"], b["forearm"], (-0.2, s * 0.6, -1.0))
        out.update({
            "hip_" + side: h, "knee_" + side: k, "ankle_" + side: a, "heel_" + side: heel,
            "ball_" + side: add(heel, mul(SOLE, b["heel_ball"])), "shoulder_" + side: sh,
            "elbow_" + side: e, "hand_" + side: hand,
        })
    if role == "driver":
        out["wheel"] = wc
    # Torso mass centre, about 45 % up the trunk: where the lumped occupant mass goes.
    out["com"] = add(hip, mul(out["torso_dir"], 0.45 * b["torso"]))
    return out


def report(p):
    """Comfort angles and reach for one posture."""
    r = {
        "seat_fwd_mm": round(p["seat_x"] - SEAT_X_REAR, 1),
        "seat_lift_mm": round(p["lift"], 1),
        "knee_deg": round(angle_at(p["hip_l"], p["knee_l"], p["ankle_l"]), 1),
        "hip_deg": round(angle_at(p["neck"], p["hip"], p["knee_l"]), 1),
        "ankle_deg": round(angle_at(p["knee_l"], p["ankle_l"], p["ball_l"]), 1),
        "elbow_deg": round(angle_at(p["shoulder_l"], p["elbow_l"], p["hand_l"]), 1),
        "eye": tuple(round(v) for v in p["eye"]),
        "helmet_top_z": round(p["head"][2] + p["helmet_r"]),
        "mass_kg": p["mass_kg"],
    }
    if "wheel" in p:
        r["column_out_mm"] = round(p["wheel"][0] - WHEEL_X_HOME, 1)
        r["eye_over_rim_mm"] = round(p["eye"][2] - RIM_TOP)
    return r
