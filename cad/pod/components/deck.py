from steve import Component
from params import deck_z, deck_t, pivot_x, pivot_z, act_xf, act_xr, act_y
from motion import (DECK_BOT, FRAME_H, TOP_PIN_DROP, UJ_LUG, UJ_LUG_T, UJ_TUBE_DX, FRONT_CROSS_X, FRONT_DEEP,
                    FRONT_DEEP_BAR_W, FRONT_DEEP_EDGE_X, YAW_PIN_X)
from bought import UJOINT_BUSHING as BUSH, YAW_ROD_END

# Moving floor: plate on a welded under-frame, the upper yoke of the universal joint, and a clevis
# at each actuator link's top pin.
deck = Component("deck", name="Moving floor")
X0, X1, W = -940, 790, 660  # rear edge clears the rear links through the crank's full swing
deck.box("plate", X1 - X0, 2 * W, deck_t, at=((X0 + X1) / 2, 0, deck_z), op="new")
zc = DECK_BOT - FRAME_H / 2


def tube(cid, length, width, at, wall=4):
    deck.box(cid, length, width, FRAME_H, at=at, op="new")
    void = (length + 4, width - 2 * wall, FRAME_H - 2 * wall) if length >= width else (
        length - 2 * wall, width + 4, FRAME_H - 2 * wall)
    deck.box(cid + "_void", *void, at=at, op="cut", body=cid)


for side, s in (("l", 1), ("r", -1)):
    tube("edge_" + side, X1 - X0, 40, ((X0 + X1) / 2, s * (W - 20), zc))
    tube("runner_" + side, X1 - X0 - 80, 40, ((X0 + X1) / 2, s * 330, zc))
# Actuator-line tubes sit inboard of the link clevises, so the links' top eyes hang free.
for name, x in (("rear", X0 + 20), ("act_r", act_xr + 70), ("act_f", act_xf - 110), ("front", X1 - 20)):
    tube("cross_" + name, 40, 2 * W - 80, (x, 0, zc))
# Under the seat rails' rear bolts (the rails run x -528..92 for every occupant): without it they land on bare
# sheet in a 620 mm bay (docs/floor-structure.md, fix A).
tube("cross_seat", 40, 2 * W - 80, (-512, 0, zc))
# The front overhang (fix G): cross tubes under the dash feet, the rear pedal and footrest pads and the footrest's
# front pads, and extra depth to the front so the overhang ahead of the front links is 100 mm deep: a solid bar under
# each runner's inboard half (clear of the links), a tube under each edge tube (clear of the front gearboxes).
for name, x in zip(("dash", "pedal", "foot"), FRONT_CROSS_X):
    tube("cross_" + name, 40, 2 * W - 80, (x, 0, zc))
zd, xb = DECK_BOT - FRAME_H - FRONT_DEEP / 2, X1 - 40
for side, s in (("l", 1), ("r", -1)):
    xa = act_xf - 90
    deck.box("runner_deep_" + side, xb - xa, FRONT_DEEP_BAR_W, FRONT_DEEP,
             at=((xa + xb) / 2, s * (310 + FRONT_DEEP_BAR_W / 2), zd), op="new")
    xa = FRONT_DEEP_EDGE_X
    deck.box("edge_deep_" + side, xb - xa, 40, FRONT_DEEP, at=((xa + xb) / 2, s * (W - 20), zd), op="new")
    deck.box("edge_deep_" + side + "_void", xb - xa + 4, 32, FRONT_DEEP - 8, at=((xa + xb) / 2, s * (W - 20), zd),
             op="cut", body="edge_deep_" + side)

# Universal joint upper yoke: two lugs across X that carry the roll pin, each with a flanged bushing pressed in
# from the inner face; the flange is the roll pin's thrust face. Each lug reaches along the frame's full depth to a
# cross tube either side of the joint, so the joint's loads go into the frame instead of bending the bare sheet
# (docs/floor-structure.md, fix H).
for name, s in (("yoke_b", -1), ("yoke_f", 1)):
    tube("cross_" + name, 40, 2 * W - 80, (pivot_x + s * UJ_TUBE_DX, 0, zc))
low = pivot_z - 25
reach = UJ_TUBE_DX - 20 - (UJ_LUG - UJ_LUG_T / 2)  # lug inner face to the tube
bushes = []
for name, s in (("f", 1), ("b", -1)):
    x = pivot_x + s * UJ_LUG
    deck.box("yoke_" + name, UJ_LUG_T, 60, DECK_BOT - low, at=(x, 0, (DECK_BOT + low) / 2), op="new")
    deck.box("yoke_" + name + "_reach", reach, 60, FRAME_H, at=(x - s * UJ_LUG_T / 2 + s * reach / 2, 0, zc),
             op="join", body="yoke_" + name)
    deck.cylinder("yoke_" + name + "_bore", BUSH["outside_diameter_mm"] / 2, UJ_LUG_T + 10,
                  at=(x - UJ_LUG_T / 2 - 5, 0, pivot_z), direction=(1, 0, 0), op="cut", body="yoke_" + name)
    inner = x - s * UJ_LUG_T / 2
    bid = "bush_" + name
    deck.cylinder(bid, BUSH["outside_diameter_mm"] / 2, BUSH["width_mm"] - BUSH["flange_thickness_mm"],
                  at=(inner, 0, pivot_z), direction=(s, 0, 0), op="new")
    deck.cylinder(bid + "_flange", BUSH["flange_diameter_mm"] / 2, BUSH["flange_thickness_mm"],
                  at=(inner, 0, pivot_z), direction=(-s, 0, 0), op="join", body=bid)
    deck.cylinder(bid + "_bore", BUSH["bore_mm"] / 2, BUSH["width_mm"] + 2,
                  at=(inner - s * (BUSH["flange_thickness_mm"] + 1), 0, pivot_z), direction=(s, 0, 0), op="cut",
                  body=bid)
    bushes.append(bid)

# Yaw restraint tail (fix I): a beam from the rear cross tube back to a clevis whose pin lies on the roll axis, for
# the restraint's rod end (yaw_block.py). The ball sits 2 mm off the front cheek: pitch draws the tail up to about
# 5 mm toward the joint, sliding the pin through the ball.
ball = YAW_ROD_END["ball_width_mm"]
cheek_f, cheek_b = YAW_PIN_X + ball / 2 + 2, YAW_PIN_X - ball / 2 - 8  # cheeks' inner faces
tail_z0 = pivot_z + 35  # clear of the rod end's eye (radius 25.5) as the floor pitches about it
deck.box("yaw_tail", X0 - (cheek_b - 10), 60, 40, at=((X0 + cheek_b - 10) / 2, 0, tail_z0 + 20), op="new")
for name, xf, s in (("f", cheek_f, 1), ("b", cheek_b, -1)):
    deck.box("yaw_cheek_" + name, 10, 60, tail_z0 - (pivot_z - 30), at=(xf + s * 5, 0, (tail_z0 + pivot_z - 30) / 2),
             op="new")
deck.cylinder("yaw_pin", YAW_ROD_END["bore_mm"] / 2, cheek_f - cheek_b + 20, at=(cheek_b - 10, 0, pivot_z),
              direction=(1, 0, 0), op="new")
yaw = ["yaw_tail", "yaw_cheek_f", "yaw_cheek_b", "yaw_pin"]

# Link top clevises: two cheeks either side of the link's top eye, which is a spherical rod end:
# the floor rolls and pitches up to 7 deg about it, so the cheeks stand 8 mm off its faces. Each cheek runs
# back to the actuator-line tube and a 6 mm web ties the inner one to the runner, so the link's tension
# goes into the frame, not the sheet (docs/floor-structure.md, fix B).
pin_z = DECK_BOT - TOP_PIN_DROP
cheek_h = TOP_PIN_DROP + 25
for name, x, y in (("fl", act_xf, act_y), ("fr", act_xf, -act_y), ("rl", act_xr, act_y), ("rr", act_xr, -act_y)):
    s = 1 if y > 0 else -1
    # Far end 30 past the pin; near end on the actuator-line tube's face.
    x_a, x_b = (x + 30, act_xf - 90) if x == act_xf else (x - 30, act_xr + 50)
    cx, cl = (x_a + x_b) / 2, abs(x_a - x_b)
    for cheek, dy in (("a", 22), ("b", -22)):
        cid = "clevis_" + name + "_" + cheek
        deck.box(cid, cl, 8, cheek_h, at=(cx, y + dy, DECK_BOT - cheek_h / 2), op="new")
        deck.cylinder(cid + "_bore", 10.5, 12, at=(x, y + dy - 6, pin_z), direction=(0, 1, 0), op="cut", body=cid)
    inner = s * (abs(y) - 26)  # inner cheek's inboard face
    deck.box("web_" + name, cl, abs(inner - s * 350), 6, at=(cx, (inner + s * 350) / 2, DECK_BOT - 3), op="new")

deck.material("aluminum-6061-t6", color="#4e565f")
deck.material("steel-s235jr", bodies=["yoke_f", "yoke_b"] + yaw[:3], color="#4a515b")
deck.material("steel-1c45", bodies=["yaw_pin"], color="#9aa1ab")
deck.material("steel-dc01", bodies=bushes, color="#b08d57")  # steel-backed PTFE composite
