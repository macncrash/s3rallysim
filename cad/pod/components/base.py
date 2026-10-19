from steve import Component
from params import pivot_x
from motion import BASE_H, RAIL_H, RAIL_Y

# Ground frame of the motion platform: two longitudinal beams carrying the surge rails, three cross
# beams, levelling feet, and the surge ballscrew actuator on the centreline.
base = Component("base", name="Motion base")
X0, X1 = -1110, 430
LENGTH = X1 - X0
MID = (X0 + X1) / 2


def tube(cid, length, width, height, at, wall=5):
    base.box(cid, length, width, height, at=at, op="new")
    if length >= width and length >= height:
        void = (length + 4, width - 2 * wall, height - 2 * wall)
    else:
        void = (length - 2 * wall, width + 4, height - 2 * wall)
    base.box(cid + "_void", *void, at=at, op="cut", body=cid)


for name, s in (("l", 1), ("r", -1)):
    tube("beam_" + name, LENGTH, 60, BASE_H, (MID, s * RAIL_Y, BASE_H / 2))
    # Size 25 profile rails for the surge carriage.
    base.box("rail_" + name, LENGTH - 60, 23, RAIL_H, at=(MID, s * RAIL_Y, BASE_H + RAIL_H / 2), op="new")
# The mid beam sits ahead of the surge nut bracket's travel.
for name, x in (("rear", X0 + 30), ("mid", pivot_x + 100), ("front", X1 - 30)):
    tube("cross_" + name, 60, 2 * RAIL_Y - 60, BASE_H, (x, 0, BASE_H / 2))
    for side, s in (("l", 1), ("r", -1)):
        base.cylinder("foot_" + name + "_" + side, 30, 12, at=(x, s * (RAIL_Y + 60), 0), direction=(0, 0, 1), op="new")

# Surge actuator: servo and ballscrew in a housing; the screw's nut rod is fixed to the carriage.
base.box("surge_body", 460, 110, 90, at=(-650, 0, 50), op="new")
base.cylinder("surge_bore", 15, 470, at=(-885, 0, 50), direction=(1, 0, 0), op="cut", body="surge_body")
base.cylinder("surge_motor", 55, 200, at=(-880, 0, 50), direction=(-1, 0, 0), op="new")

base.material("steel-s235jr", finish="powder-coated", color="#2c3138")
base.material("steel-1c45", bodies=["rail_l", "rail_r"], color="#8d939c")
base.material("aluminum-6061-t6", bodies=["surge_body", "surge_motor"], color="#c5cad1")
