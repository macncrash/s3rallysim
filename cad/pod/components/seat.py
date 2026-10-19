import math
from steve import Component
from ergo import BODY, RAKE, SEAT_HX, SEAT_CUSHION

# FIA-style composite bucket in its own frame: origin at the cushion bottom centre.
# Shaped round the 95th percentile; smaller occupants sit on the lift cushion and a foam insert.
seat = Component("seat", name="FIA bucket seat")
b = BODY[95]
r = math.radians(RAKE)
up = (-math.sin(r), 0.0, math.cos(r))
fwd = (math.cos(r), 0.0, math.sin(r))
hip = (SEAT_HX, 0.0, SEAT_CUSHION + b["hip_up"])
behind = b["chest"] / 2 + 30  # back shell inner face behind the torso centreline


def along(d_up, d_fwd):
    return (hip[0] + up[0] * d_up + fwd[0] * d_fwd, 0.0, hip[2] + up[2] * d_up + fwd[2] * d_fwd)


def tilted(cid, length, width, height, centre):
    seat.box(cid, length, width, height, at=centre, op="new")
    seat.move(cid + "_tilt", [cid], rotate=((centre, (0, 1, 0)), -RAKE))


seat.box("cushion", 470, 500, SEAT_CUSHION, at=(10, 0, SEAT_CUSHION / 2))
seat.box("thigh_l", 380, 40, 120, at=(20, 230, SEAT_CUSHION + 30), op="new")
seat.box("thigh_r", 380, 40, 120, at=(20, -230, SEAT_CUSHION + 30), op="new")
back_h = 1020
tilted("back", 50, 500, back_h, along(back_h / 2 - 140, -behind - 25))
for name, s in (("l", 1), ("r", -1)):
    c = along(330, -behind + 70)
    tilted("rib_" + name, 190, 40, 560, (c[0], s * 250, c[2]))
    c = along(b["torso"] + 260, -behind + 95)
    tilted("head_" + name, 230, 40, 300, (c[0], s * (b["helmet"] + 45), c[2]))
seat.cylinder("belt", 6, 300, at=(40, -150, SEAT_CUSHION + 14), direction=(0, 1, 0), op="new")
seat.material("abs", color="#141414")
seat.material("abs", bodies=["belt"], color="#c1121f")
