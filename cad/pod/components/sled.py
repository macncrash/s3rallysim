from steve import Component
from params import pivot_x, pivot_z
from motion import BASE_H, RAIL_H, RAIL_Y, CAR_H, SLED_Z0, SLED_H, SLED_TOP, ACTUATORS, CRANK_DY, crank_axis
import drive_parts
from bought import SURGE_RAIL, SURGE_BALLSCREW

# Surge carriage: four HIWIN HGW25CC rail blocks (bought.py), two runners and four cross tubes, the heave
# column under the universal joint, the gearbox mounts, and the bracket that takes the surge ballscrew's nut.
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
        sled.box("block_" + name + "_" + side, SURGE_RAIL["block_length_mm"], SURGE_RAIL["block_width_mm"], CAR_H,
                 at=(x, s * RAIL_Y, BASE_H + RAIL_H + CAR_H / 2), op="new")
# Two mid tubes, under the column plate's front and rear edges: the post's fore-aft moment bends them instead
# of twisting a single tube under its centre (docs/floor-structure.md, fix C).
for name, x in (("rear", X0 + 30), ("mid_b", pivot_x - 70), ("mid_f", pivot_x + 70), ("front", X1 - 30)):
    tube("cross_" + name, 60, 2 * RAIL_Y - 60, SLED_H, (x, 0, zc))

# Gearbox mounts: two outrigger beams from each runner, clear of the crank's swing, to a plate the
# gearbox's output flange bolts to. The output shaft passes through the plate to the crank.
for name, x, y in ACTUATORS:
    s = 1 if y > 0 else -1
    ax = crank_axis(x, y)
    plate_y = y + s * (CRANK_DY + drive_parts.BODY_Y0 - 6)
    reach = abs(plate_y) - (RAIL_Y + 30)
    for side_name, dx in (("f", 185), ("b", -185)):
        sled.box("outrigger_" + name + "_" + side_name, 60, reach, SLED_H,
                 at=(ax[0] + dx, s * (RAIL_Y + 30 + reach / 2), zc), op="new")
    sled.box("mount_" + name, 430, 12, drive_parts.FRAME + 40, at=(ax[0], plate_y, ax[2] + 10), op="new")
    sled.cylinder("mount_" + name + "_bore", 25, 20, at=(ax[0], plate_y - 10, ax[2]), direction=(0, 1, 0), op="cut",
                  body="mount_" + name)

# Heave column: a square post the universal-joint sleeve slides on.
sled.box("column_plate", 200, 200, 12, at=(pivot_x, 0, SLED_TOP + 6), op="new")
top = pivot_z - 70  # 40 mm of sleeve engagement left at full heave
sled.box("column", 120, 120, top - SLED_TOP - 12, at=(pivot_x, 0, (SLED_TOP + 12 + top) / 2), op="new")

# Surge nut rod into the ballscrew housing on the base, and its bracket under the rear mid cross tube's
# front edge (any further aft and it meets the surge body at full rear surge).
sled.cylinder("nut_rod", SURGE_BALLSCREW["nominal_diameter_mm"] / 2 - 0.5, 360, at=(-700, 0, 45), direction=(1, 0, 0),
              op="new")
sled.box("nut_bracket", 30, 80, SLED_Z0 + 10 - 20, at=(pivot_x - 45, 0, (SLED_Z0 + 10 + 20) / 2), op="new")

sled.material("aluminum-6061-t6", color="#3d4450")
sled.material("steel-1c45", bodies=["nut_rod", "column"], color="#9aa1ab")
