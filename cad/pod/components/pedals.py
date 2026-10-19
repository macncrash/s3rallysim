import math
from steve import Component
from params import deck_top
from ergo import rally, DRIVER_Y, HEEL, SOLE, SOLE_DEG, BODY, add, mul

# Floor-hinged pedal box in the design frame: heel plate at the heel point, pads along the sole
# line where the ball of the foot lands for every size from the 5th to the 95th percentile.
pedals = Component("pedals", name="Pedal box")
hx, hz = HEEL[0], HEEL[2]
pedals.box("plate", 360, 300, 8, at=(hx + 100, DRIVER_Y, deck_top + 4))
pedals.box("heel", 120, 300, 10, at=(hx - 20, DRIVER_Y, hz - 5), op="new")
ball = (BODY[5]["heel_ball"] + BODY[95]["heel_ball"]) / 2
pad_c = add((hx, 0.0, hz + 8), mul(SOLE, ball))
normal = (-math.sin(math.radians(SOLE_DEG)), 0.0, math.cos(math.radians(SOLE_DEG)))
arms = (("brake", 0.0), ("throttle", -78.0), ("clutch", 78.0)) if rally else (("brake", 78.0), ("throttle", -78.0))
for name, dy in arms:
    y = DRIVER_Y + dy
    c = (pad_c[0], y, pad_c[2])
    pedals.box(name + "_pad", 120, 64, 10, at=c, op="new")
    pedals.move(name + "_pad_tilt", [name + "_pad"], rotate=((c, (0, 1, 0)), -SOLE_DEG))
    pivot = (hx + 150, y, deck_top + 22)
    back = add(c, mul(normal, -12))
    d = (back[0] - pivot[0], 0.0, back[2] - pivot[2])
    n = math.hypot(d[0], d[2])
    pedals.cylinder(name + "_arm", 9, n, at=pivot, direction=(d[0] / n, 0.0, d[2] / n), op="new")
    pedals.box(name + "_hinge", 40, 50, 30, at=(pivot[0], y, deck_top + 23), op="new")
pedals.material("aluminum-6061-t6", color="#2f343b")
pedals.material("abs", bodies=[name + "_pad" for name, _ in arms], color="#1a1a1a")
