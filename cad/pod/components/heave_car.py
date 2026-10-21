from steve import Component
from params import pivot_x, pivot_z, heave_mm
from motion import GUIDE_Y, GUIDE_COL, GUIDE_TOP, GUIDE_RAIL_H
from bought import HEAVE_GUIDE

# Heave crosshead with the lower yoke of the universal joint: two lugs across X that carry the roll pin, on a
# bridge between two ears. Each ear carries a guide rail running in two blocks fixed on a column of the carriage
# (sled.py), so the joint's side and fore-aft loads go straight into the braced columns.
heave_car = Component("heave_car", name="Heave crosshead and lower yoke")
block_len = HEAVE_GUIDE["block_length_mm"]
block_h = HEAVE_GUIDE["total_height_mm"] - GUIDE_RAIL_H
guide_z0 = GUIDE_TOP - 2 * block_len
# The rail covers both blocks over the whole heave stroke.
r0, r1 = guide_z0 - heave_mm, GUIDE_TOP + heave_mm
ear_in = GUIDE_Y - GUIDE_COL / 2 - block_h - GUIDE_RAIL_H - 20  # ear inner face: clear of the floor's yoke lugs
for name, s in (("l", 1), ("r", -1)):
    heave_car.box("rail_" + name, HEAVE_GUIDE["rail_width_mm"], GUIDE_RAIL_H, r1 - r0,
                  at=(pivot_x, s * (ear_in + 20 + GUIDE_RAIL_H / 2), (r0 + r1) / 2), op="new")
    heave_car.box("ear_" + name, 40, 20, r1 - r0 + 12, at=(pivot_x, s * (ear_in + 10), (r0 + r1) / 2 - 1), op="new")
# The bridge stays 20 mm under the floor's yoke lugs at full roll.
heave_car.box("bridge", 180, 2 * (ear_in + 10), 30, at=(pivot_x, 0, pivot_z - 70), op="new")
top = pivot_z + 25
for name, dx in (("f", 75), ("b", -75)):
    heave_car.box("lug_" + name, 20, 60, top - (pivot_z - 55), at=(pivot_x + dx, 0, (pivot_z - 55 + top) / 2),
                  op="new")
    heave_car.cylinder("lug_" + name + "_bore", 18.5, 30, at=(pivot_x + dx - 15, 0, pivot_z), direction=(1, 0, 0),
                       op="cut", body="lug_" + name)
heave_car.material("steel-s235jr", color="#4a515b")
heave_car.material("steel-1c45", bodies=["rail_l", "rail_r"], color="#8d939c")
