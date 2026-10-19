from steve import Component
from params import deck_z, deck_t, pivot_x, pivot_z, act_xf, act_xr, act_y
from motion import DECK_BOT, FRAME_H, TOP_PIN_DROP

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

# Universal joint upper yoke: two lugs across Y that carry the pitch pin.
low = pivot_z - 25
for name, s in (("l", 1), ("r", -1)):
    deck.box("yoke_" + name, 60, 20, DECK_BOT - low, at=(pivot_x, s * 75, (DECK_BOT + low) / 2), op="new")
    deck.cylinder("yoke_" + name + "_bore", 18.5, 30, at=(pivot_x, s * 75 - 15, pivot_z), direction=(0, 1, 0),
                  op="cut", body="yoke_" + name)

# Link top clevises: two cheeks either side of the link's top eye, which is a spherical rod end:
# the floor rolls and pitches up to 7 deg about it, so the cheeks stand 8 mm off its faces.
pin_z = DECK_BOT - TOP_PIN_DROP
for name, x, y in (("fl", act_xf, act_y), ("fr", act_xf, -act_y), ("rl", act_xr, act_y), ("rr", act_xr, -act_y)):
    for cheek, dy in (("a", 22), ("b", -22)):
        cid = "clevis_" + name + "_" + cheek
        deck.box(cid, 60, 8, TOP_PIN_DROP + 25, at=(x, y + dy, DECK_BOT - (TOP_PIN_DROP + 25) / 2), op="new")
        deck.cylinder(cid + "_bore", 10.5, 12, at=(x, y + dy - 6, pin_z), direction=(0, 1, 0), op="cut", body=cid)

deck.material("aluminum-6061-t6", color="#4e565f")
deck.material("steel-s235jr", bodies=["yoke_l", "yoke_r"], color="#4a515b")
