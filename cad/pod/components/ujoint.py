from steve import Component
from params import pivot_x, pivot_z
from motion import UJ_LUG, UJ_LUG_T, UJ_THRUST_GAP
from bought import UJOINT_BUSHING as BUSH

# Universal joint spider: the pitch pin along Y runs in the crosshead's lug bushings, the roll pin along X in the
# floor's. Its centre is the motion platform's roll and pitch pivot. A boss on each arm reaches out to the flange of
# that lug's bushing, so each pin's thrust (fore-aft on the roll pin, sideways on the pitch pin) has a face to bear
# on (docs/floor-structure.md, fix E).
ujoint = Component("ujoint", name="Universal joint spider")
B = 50  # spider block
ujoint.box("block", B, B, B, at=(pivot_x, 0, pivot_z))
boss_len = UJ_LUG - UJ_LUG_T / 2 - BUSH["flange_thickness_mm"] - UJ_THRUST_GAP - B / 2
for axis, d in (("x", (1, 0, 0)), ("y", (0, 1, 0))):
    ujoint.cylinder("pin_" + axis, BUSH["bore_mm"] / 2, 180, at=(pivot_x - 90 * d[0], -90 * d[1], pivot_z),
                    direction=d, op="new")
    for side, s in (("p", 1), ("n", -1)):
        ujoint.cylinder(f"boss_{axis}{side}", BUSH["flange_diameter_mm"] / 2, boss_len,
                        at=(pivot_x + s * B / 2 * d[0], s * B / 2 * d[1], pivot_z), direction=(s * d[0], s * d[1], 0),
                        op="new")
ujoint.material("steel-34crnimo6", color="#b8bec6")
