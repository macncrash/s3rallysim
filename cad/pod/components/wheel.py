import math
import cadquery as cq
from steve import Component
from params import driver_pct, column_len
from ergo import DRIVER_Y, WHEEL_Z, WHEEL_R, WHEEL_FACE, WHEEL_UP, WHEEL_X_HOME, DASH, wheel_x, add, sub, mul, unit, norm
from bought import WHEELBASE

# Steering wheel on a Simucube 2 Pro direct-drive base (bought.py), in the design frame. The base
# rides a reach-adjust slide on a bracket hanging from the dash crossbar; nothing reaches down into the
# footwell.
wheel = Component("wheel", name="Steering wheel on " + WHEELBASE["model"])
centre = (wheel_x(driver_pct), DRIVER_Y, WHEEL_Z)
fwd = mul(WHEEL_FACE, -1.0)  # from the wheel toward the dash

# The wheelbase: a 130 mm square body along the wheel axis, 270 mm long with its quick release; a
# bracket from its back to the crossbar clamp takes the reach adjustment.
qr_at = add(centre, mul(fwd, 60))
BASE_W = WHEELBASE["diameter_or_width_mm"]
BASE_L = WHEELBASE["length_mm"] - 60  # body behind the quick release
body_c = add(qr_at, mul(fwd, BASE_L / 2))
wheel.box("base", BASE_L, BASE_W, BASE_W, at=body_c, op="new")
wheel.move("base_tilt", ["base"], rotate=((body_c, (0, 1, 0)), math.degrees(math.atan2(-fwd[2], fwd[0]))))  # along the column
back = add(qr_at, mul(fwd, BASE_L))
run = sub(DASH, back)
wheel.cylinder("bracket", 20, max(norm(run), 1), at=back, direction=unit(run) if norm(run) > 1 else fwd, op="new")
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
wheel.material("aluminum-6061-t6", bodies=["base", "hub", "quick_release", "spoke_l", "spoke_r", "spoke_b"],
               color="#9aa1ab")
wheel.material("abs", bodies=["rim"], color="#101010")
