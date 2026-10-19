from steve import Component
from params import pivot_x
from motion import BASE_H, RAIL_H, RAIL_Y, CAR_H, SLED_Z0, SLED_H, SLED_TOP

# Surge carriage: four rail blocks, two runners and three cross tubes, the heave column under the
# universal joint, and the bracket that takes the surge ballscrew's nut rod.
sled = Component("sled", name="Surge carriage")
X0, X1 = -960, 250
zc = SLED_Z0 + SLED_H / 2


def tube(cid, length, width, height, at, wall=5):
    sled.box(cid, length, width, height, at=at, op="new")
    if length >= width:
        void = (length + 4, width - 2 * wall, height - 2 * wall)
    else:
        void = (length - 2 * wall, width + 4, height - 2 * wall)
    sled.box(cid + "_void", *void, at=at, op="cut", body=cid)


for side, s in (("l", 1), ("r", -1)):
    tube("runner_" + side, X1 - X0, 60, SLED_H, ((X0 + X1) / 2, s * RAIL_Y, zc))
    for name, x in (("rear", X0 + 90), ("front", X1 - 90)):
        sled.box("block_" + name + "_" + side, 100, 48, CAR_H, at=(x, s * RAIL_Y, BASE_H + RAIL_H + CAR_H / 2),
                 op="new")
for name, x in (("rear", X0 + 30), ("mid", pivot_x), ("front", X1 - 30)):
    tube("cross_" + name, 60, 2 * RAIL_Y - 60, SLED_H, (x, 0, zc))

# Heave column: a square post the universal-joint sleeve slides on.
sled.box("column_plate", 200, 200, 12, at=(pivot_x, 0, SLED_TOP + 6), op="new")
sled.box("column", 120, 120, 310 - SLED_TOP - 12, at=(pivot_x, 0, (SLED_TOP + 12 + 310) / 2), op="new")

# Surge nut rod into the ballscrew housing on the base, and its bracket under the mid cross tube.
sled.cylinder("nut_rod", 12, 360, at=(-700, 0, 50), direction=(1, 0, 0), op="new")
sled.box("nut_bracket", 30, 80, SLED_Z0 + 10 - 20, at=(pivot_x - 45, 0, (SLED_Z0 + 10 + 20) / 2), op="new")

sled.material("aluminum-6061-t6", color="#3d4450")
sled.material("steel-1c45", bodies=["nut_rod", "column"], color="#9aa1ab")
