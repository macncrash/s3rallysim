import math
import cadquery as cq
from steve import Component
from params import driver_pct, column_len
from ergo import DRIVER_Y, WHEEL_Z, WHEEL_R, WHEEL_FACE, WHEEL_UP, WHEEL_X_HOME, DASH, wheel_x, add, sub, mul, unit, norm

# Steering wheel and column, in the design frame. The column hangs from the dash crossbar and
# telescopes toward the driver; nothing reaches down into the footwell.
wheel = Component("wheel", name="Steering wheel and column")
centre = (wheel_x(driver_pct), DRIVER_Y, WHEEL_Z)
fwd = mul(WHEEL_FACE, -1.0)  # from the wheel toward the dash

# Fixed outer column from the crossbar clamp, inner shaft out to the quick release.
qr_at = add(centre, mul(fwd, 60))
run = sub(qr_at, DASH)
axis = unit(run)
outer_len = column_len - 120
wheel.cylinder("column", 26, outer_len, at=DASH, direction=axis, op="new")
wheel.cylinder("shaft", 17, norm(run) - outer_len + 30, at=add(DASH, mul(axis, outer_len - 30)), direction=axis,
               op="new")
wheel.cylinder("quick_release", 32, 36, at=qr_at, direction=WHEEL_FACE, op="new")
hub_at = add(centre, mul(fwd, 26))
wheel.cylinder("hub", 45, 32, at=hub_at, direction=WHEEL_FACE, op="new")

# Rim: a 350 mm dished ring, 32 mm grip, on three spokes.
grip_r = 16
rim = cq.Solid.makeTorus(WHEEL_R, grip_r, cq.Vector(*centre), cq.Vector(*WHEEL_FACE))
wheel.add("rim", rim, op="new")
side = (0.0, 1.0, 0.0)
for name, deg in (("spoke_l", 0), ("spoke_r", 180), ("spoke_b", 270)):
    a = math.radians(deg)
    d = (side[0] * math.cos(a) + WHEEL_UP[0] * math.sin(a), side[1] * math.cos(a),
         side[2] * math.cos(a) + WHEEL_UP[2] * math.sin(a))
    wheel.cylinder(name, 11, WHEEL_R - 8, at=add(centre, mul(fwd, 6)), direction=d, op="new")

wheel.material("steel-1c45", color="#2b2f34")
wheel.material("aluminum-6061-t6", bodies=["hub", "quick_release", "spoke_l", "spoke_r", "spoke_b"],
               color="#9aa1ab")
wheel.material("abs", bodies=["rim"], color="#101010")
