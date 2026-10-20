import math
from steve import Component
from ergo import BODY, RAKE, SEAT_HX, SEAT_CUSHION
from bought import RALLY_SEAT

# Recaro Pro Racer SPG XL (bought.py): a glass-fibre shell, 915 mm tall, in its own frame with the
# origin at the cushion bottom centre. Shaped round the 95th percentile; smaller occupants sit on the
# lift cushion and a foam insert.
seat = Component("seat", name="Rally seat " + RALLY_SEAT["model"].split(",")[0])
b = BODY[95]
r = math.radians(RAKE)
up = (-math.sin(r), 0.0, math.cos(r))
fwd = (math.cos(r), 0.0, math.sin(r))
hip = (SEAT_HX, 0.0, SEAT_CUSHION + b["hip_up"])
behind = b["chest"] / 2 + 30  # back shell inner face behind the torso centreline
# The shell is a ~5 mm glass-fibre laminate (~1.8 g/cm3). The library has E-glass, not laminate, so
# the shell is drawn 3.3 mm thick in E-glass: the same mass, the card's 10 kg with cushion and belt.
T = 3.3
HEIGHT = RALLY_SEAT["overall_height_mm"]


def along(d_up, d_fwd):
    return (hip[0] + up[0] * d_up + fwd[0] * d_fwd, 0.0, hip[2] + up[2] * d_up + fwd[2] * d_fwd)


def tilted(cid, length, width, height, centre):
    seat.box(cid, length, width, height, at=centre, op="new")
    seat.move(cid + "_tilt", [cid], rotate=((centre, (0, 1, 0)), -RAKE))


seat.box("pan", 470, 500, T, at=(10, 0, T / 2))
seat.box("cushion", 430, 440, 40, at=(15, 0, T + 20), op="new")  # foam pad on the pan
seat.box("thigh_l", 380, T, 120, at=(20, 250, 60), op="new")
seat.box("thigh_r", 380, T, 120, at=(20, -250, 60), op="new")
back_h = HEIGHT - 40
tilted("back", T, 500, back_h, along(back_h / 2 - 140, -behind - 25))
for name, s in (("l", 1), ("r", -1)):
    c = along(330, -behind + 70)
    tilted("rib_" + name, 190, T, 560, (c[0], s * 250, c[2]))
    c = along(b["torso"] + 260, -behind + 95)
    tilted("head_" + name, 230, T, 300, (c[0], s * (b["helmet"] + 45), c[2]))
seat.cylinder("belt", 6, 300, at=(40, -150, T + 44), direction=(0, 1, 0), op="new")
seat.material("glass-fibre-e", color="#141414")
seat.material("eps-foam", bodies=["cushion"], color="#1c1c1c")
seat.material("abs", bodies=["belt"], color="#c1121f")
