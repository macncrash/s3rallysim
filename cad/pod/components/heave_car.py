from steve import Component
from params import pivot_x, pivot_z, heave_mm
from motion import GUIDE_Y, GUIDE_COL, GUIDE_TOP, GUIDE_RAIL_H, UJ_LUG, UJ_LUG_T
from bought import HEAVE_GUIDE, UJOINT_BUSHING as BUSH

# Heave crosshead with the lower yoke of the universal joint: two lugs across Y that carry the pitch pin, on a
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
bushes = []
for name, s in (("l", 1), ("r", -1)):
    y = s * UJ_LUG
    heave_car.box("lug_" + name, 60, UJ_LUG_T, top - (pivot_z - 55), at=(pivot_x, y, (pivot_z - 55 + top) / 2),
                  op="new")
    heave_car.cylinder("lug_" + name + "_bore", BUSH["outside_diameter_mm"] / 2, UJ_LUG_T + 10,
                       at=(pivot_x, y - UJ_LUG_T / 2 - 5, pivot_z), direction=(0, 1, 0), op="cut", body="lug_" + name)
    # Flanged bushing pressed in from the inner face; its flange is the pitch pin's thrust face.
    inner = y - s * UJ_LUG_T / 2
    bid = "bush_" + name
    heave_car.cylinder(bid, BUSH["outside_diameter_mm"] / 2, BUSH["width_mm"] - BUSH["flange_thickness_mm"],
                       at=(pivot_x, inner, pivot_z), direction=(0, s, 0), op="new")
    heave_car.cylinder(bid + "_flange", BUSH["flange_diameter_mm"] / 2, BUSH["flange_thickness_mm"],
                       at=(pivot_x, inner, pivot_z), direction=(0, -s, 0), op="join", body=bid)
    heave_car.cylinder(bid + "_bore", BUSH["bore_mm"] / 2, BUSH["width_mm"] + 2,
                       at=(pivot_x, inner - s * (BUSH["flange_thickness_mm"] + 1), pivot_z), direction=(0, s, 0),
                       op="cut", body=bid)
    bushes.append(bid)
heave_car.material("steel-s235jr", color="#4a515b")
heave_car.material("steel-1c45", bodies=["rail_l", "rail_r"], color="#8d939c")
heave_car.material("steel-dc01", bodies=bushes, color="#b08d57")  # steel-backed PTFE composite
