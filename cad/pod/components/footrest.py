import math
from steve import Component
from params import deck_top, seat_y
from ergo import HEEL, SOLE, SOLE_DEG, add, mul

# Co-driver footrest: a heel plate and an angled bracing plate at the same heel point and sole
# angle as the driver's pedals, so the co-driver can brace through landings.
footrest = Component("footrest", name="Co-driver footrest")
hx, hz = HEEL[0], HEEL[2]
footrest.box("heel", 120, 360, 10, at=(hx - 20, -seat_y, hz - 5))
c = add((hx, -seat_y, hz + 8), mul(SOLE, 190))
footrest.box("brace", 230, 360, 10, at=c, op="new")
footrest.move("brace_tilt", ["brace"], rotate=((c, (0, 1, 0)), -SOLE_DEG))
low = (hx + 150, -seat_y, deck_top + 30)
for name, dy in (("leg_l", 150), ("leg_r", -150)):
    footrest.box(name, 30, 20, 2 * (c[2] - deck_top) * 0.55, at=(low[0] - 30, -seat_y + dy, deck_top + (c[2] - deck_top) * 0.55), op="new")
footrest.material("aluminum-6061-t6", color="#3a414c")
footrest.material("abs", bodies=["brace"], color="#1a1a1a")
