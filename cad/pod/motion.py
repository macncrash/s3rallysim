"""Motion platform geometry, shared by the platform components, main.py and the analysis scripts.

Four rotary crank actuators lift the moving floor at its corners through vertical links with rod
ends; a passive heave guide carries a universal joint under the floor's centre of mass, which takes the
side and fore-aft loads and sets the roll and pitch pivot. The whole stack rides
a surge carriage on profile rails, driven by a ballscrew.

Bought parts (servo, gearbox, rod ends, rails) come from bought.py. Millimetres and degrees, design frame, floor at rest. Each crank arm points +X at rest (horizontal),
so a crank turns through about asin(dz / crank_r) for a floor point that moves dz.
"""

import math

from params import pivot_x, pivot_z, act_xf, act_xr, act_y, crank_r, link_len, deck_z, deck_t

DECK_BOT = deck_z - deck_t / 2  # floor plate underside
FRAME_H = 60  # floor under-frame depth
TOP_PIN_DROP = 45  # link top pin below the plate: the eye clears it at full lean
STROKE = 113  # mm floor travel per actuator, crank at +-65 deg

# Base and surge carriage heights.
BASE_H = 60  # base beams 0..60
RAIL_H = 23  # surge rails on the base beams
CAR_H = 13  # surge rail blocks above the rail: HIWIN HGW25CC total height 36 mm (bought.SURGE_RAIL)
SLED_Z0 = BASE_H + RAIL_H + CAR_H  # surge carriage frame underside
SLED_H = 60
SLED_TOP = SLED_Z0 + SLED_H
RAIL_Y = 300  # surge rails from the centreline
CRANK_DY = 30  # crank arm plane outboard of its link; the gearbox sits outboard of the crank

# Heave guide (docs/floor-structure.md, fixes D and F): two fixed steel columns either side of the universal joint,
# each braced by two struts down to the surge rail blocks. The crosshead carrying the joint's lower yoke runs on one
# guide rail per side, in two blocks fixed on each column (bought.HEAVE_GUIDE).
GUIDE_Y = 215  # column centres from the centreline
GUIDE_COL = 100  # column square section, 8 mm wall
GUIDE_TOP = 415  # column top: clears the floor plate at -40 mm heave with full roll and pitch
GUIDE_RAIL_H = 23  # guide rail height, as RAIL_H; the block's total height comes from bought.HEAVE_GUIDE
STRUT_Z = 360  # where the struts meet the column axis
STRUT_R = 30.15  # struts: CHS 60.3 x 5
STRUT_T = 5

# Universal joint: both yokes' lugs, each with a flanged bushing (bought.UJOINT_BUSHING) whose flange faces the spider
# and takes the pin's thrust (docs/floor-structure.md, fix E).
UJ_LUG = 75  # lug centres from the pivot, along the pin
UJ_LUG_T = 20  # lug thickness
UJ_THRUST_GAP = 0.5  # spider boss to flange, each side, as drawn; shimmed to 0.05-0.1 mm in all on assembly
# The floor's yoke mount (fix H): a cross tube each side of the joint, clear of the crosshead's lugs through full roll
# and pitch, with each yoke lug carried on a bar along the frame's full depth between them.
UJ_TUBE_DX = 140  # yoke cross tubes' centres fore and aft of the pivot
# The floor's front overhang (fix G): cross tubes under the dash feet, the rear pedal and footrest pads and the
# footrest's front pads, and extra depth under each runner and edge tube to the front. Under the runners it is a solid
# bar on their inboard half, from the front actuator tube, clear of the front links; under the edge tubes a tube from
# x 270, clear of the front gearboxes.
FRONT_CROSS_X = (272, 440, 600)
FRONT_DEEP = 40  # extra frame depth ahead of the front actuators
FRONT_DEEP_BAR_W = 20  # solid bar under each runner's inboard half
FRONT_DEEP_EDGE_X = 270  # where the edge tubes' extra depth starts

# Actuators: name, x, y. Front pair, rear pair.
ACTUATORS = (
    ("fl", act_xf, act_y), ("fr", act_xf, -act_y),
    ("rl", act_xr, act_y), ("rr", act_xr, -act_y),
)


def top_pin(x, y):
    return (x, y, DECK_BOT - TOP_PIN_DROP)


def crank_tip(x, y):
    p = top_pin(x, y)
    return (p[0], p[1], p[2] - link_len)


def crank_axis(x, y):
    t = crank_tip(x, y)
    return (t[0] - crank_r, t[1], t[2])


CRANK_Z = crank_tip(act_xf, act_y)[2]

# Small-angle gearing from the floor's axes to each crank (and back to its link, which stays upright).
# A floor point at (x, y) rises dz = heave - (x - pivot_x) * pitch_rad + y * roll_rad, and the crank
# (axis +Y, so a positive turn lowers its tip) turns -dz / crank_r rad.
DEG = 180 / math.pi


def crank_ratios(x, y):
    """Crank degrees per mm of heave, per degree of pitch, per degree of roll."""
    return (-DEG / crank_r, (x - pivot_x) / crank_r, -y / crank_r)


def floor_point(point, heave, pitch_deg, roll_deg):
    """Where a point on the floor goes (relative to the surge carriage) for a floor pose."""
    p, r = math.radians(pitch_deg), math.radians(roll_deg)
    # Pitch (about Y) inside roll (about X), both about the universal joint, then heave.
    dx, dy, dz = point[0] - pivot_x, point[1], point[2] - pivot_z
    x1 = dx * math.cos(p) + dz * math.sin(p)
    z1 = -dx * math.sin(p) + dz * math.cos(p)
    y2 = dy * math.cos(r) - z1 * math.sin(r)
    z2 = dy * math.sin(r) + z1 * math.cos(r)
    return (x1 + pivot_x, y2, z2 + pivot_z + heave)


def crank_angle(x, y, heave, pitch_deg, roll_deg):
    """Exact crank angle (deg) for a floor pose, or None if it is beyond the crank's reach."""
    pin = floor_point(top_pin(x, y), heave, pitch_deg, roll_deg)
    ax = crank_axis(x, y)
    # Crank tip on a circle round the axis; link of fixed length up to the pin (planar, in X-Z).
    ddx, ddz = pin[0] - ax[0], pin[2] - ax[2]
    d = math.hypot(ddx, ddz)
    if d > crank_r + link_len or d < abs(link_len - crank_r):
        return None
    a = math.atan2(ddz, ddx)
    b = math.acos((crank_r ** 2 + d * d - link_len ** 2) / (2 * crank_r * d))
    # The branch with the link above the crank: tip below the pin line.
    return -math.degrees(a - b)
