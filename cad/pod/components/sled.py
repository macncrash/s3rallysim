from steve import Component
from params import pivot_x
from motion import (BASE_H, RAIL_H, RAIL_Y, CAR_H, SLED_Z0, SLED_H, SLED_TOP, ACTUATORS, CRANK_DY, crank_axis,
                    GUIDE_Y, GUIDE_COL, GUIDE_TOP, GUIDE_RAIL_H, STRUT_Z, STRUT_R, STRUT_T)
import drive_parts
from bought import SURGE_RAIL, SURGE_BALLSCREW, HEAVE_GUIDE

# Surge carriage: four HIWIN HGW25CC rail blocks (bought.py), two runners and four cross tubes, the heave guide
# columns either side of the universal joint, the gearbox mounts, and the bracket that takes the surge ballscrew's nut.
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

# Heave guide: a steel column each side of the universal joint on a foot plate across the twin mid tubes, with two
# guide blocks on its inner face for the crosshead's rail (heave_car.py). Two struts brace each column straight down
# to the surge rail blocks, so the joint's side and fore-aft loads reach the rails without bending the runners.
block_len = HEAVE_GUIDE["block_length_mm"]
block_h = HEAVE_GUIDE["total_height_mm"] - GUIDE_RAIL_H
guide_z0 = GUIDE_TOP - 2 * block_len
foot_t = 15
col_h = GUIDE_TOP - SLED_TOP - foot_t
steel = []
for side, s in (("l", 1), ("r", -1)):
    y = s * GUIDE_Y
    sled.box("foot_" + side, 200, 120, foot_t, at=(pivot_x, y, SLED_TOP + foot_t / 2), op="new")
    sled.box("column_" + side, GUIDE_COL, GUIDE_COL, col_h, at=(pivot_x, y, SLED_TOP + foot_t + col_h / 2), op="new")
    sled.box("column_" + side + "_void", GUIDE_COL - 16, GUIDE_COL - 16, col_h,
             at=(pivot_x, y, SLED_TOP + foot_t + col_h / 2 + 8), op="cut", body="column_" + side)
    steel += ["foot_" + side, "column_" + side]
    for k in (0, 1):
        sled.box(f"guide_block_{side}{k}", HEAVE_GUIDE["block_width_mm"], block_h, block_len,
                 at=(pivot_x, s * (GUIDE_Y - GUIDE_COL / 2 - block_h / 2), guide_z0 + block_len * (k + 0.5)), op="new")
        steel.append(f"guide_block_{side}{k}")
    for end, bx in (("f", X1 - 90), ("b", X0 + 90)):
        a = (pivot_x, y, STRUT_Z)
        d = (bx - pivot_x, s * RAIL_Y - y, SLED_TOP + STRUT_R - STRUT_Z)
        length = sum(v * v for v in d) ** 0.5
        u = tuple(v / length for v in d)
        sid = "strut_" + side + end
        sled.cylinder(sid, STRUT_R, length, at=a, direction=u, op="new")
        sled.cylinder(sid + "_bore", STRUT_R - STRUT_T, length - 60, at=tuple(a[i] + 30 * u[i] for i in range(3)),
                      direction=u, op="cut", body=sid)
        sled.box("strut_" + side + end + "_foot", 120, 60, 10, at=(bx, s * RAIL_Y, SLED_TOP + 5), op="new")
        steel += [sid, "strut_" + side + end + "_foot"]

# Surge nut rod into the ballscrew housing on the base, and its bracket under the rear mid cross tube's
# front edge (any further aft and it meets the surge body at full rear surge).
sled.cylinder("nut_rod", SURGE_BALLSCREW["nominal_diameter_mm"] / 2 - 0.5, 360, at=(-700, 0, 45), direction=(1, 0, 0),
              op="new")
sled.box("nut_bracket", 30, 80, SLED_Z0 + 10 - 20, at=(pivot_x - 45, 0, (SLED_Z0 + 10 + 20) / 2), op="new")

sled.material("aluminum-6061-t6", color="#3d4450")
sled.material("steel-1c45", bodies=["nut_rod"], color="#9aa1ab")
sled.material("steel-s235jr", bodies=steel, color="#4a515b")
