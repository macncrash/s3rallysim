"""S3 Rally Pod surge carriage with the yaw restraint's post, as one solid, for a STEVE study of the restraint's
sideways stiffness (docs/floor-structure.md, fix I).

The carriage frame (sled.py: runners extended to the tail, the cross tubes, the tail cross tube) with the post, its
strut, the guide rail and the guide block, welded into one solid. The block sits at the top of its travel, where
the post is softest; a side load on its arm pad gives the restraint's stiffness at the floor's tail pin. The numbers
are copied from the pod design's parameter and motion files: change them there first, then here.

Supports as in the platform modal part: the four surge rail blocks (held sideways and vertically) and the surge
ballscrew nut (held fore-aft). One material, set per study: the post and strut are steel, the frame 6061, so the
two moduli bound the truth.
"""

from steve import Model

sled_z0 = 96  # mm carriage frame underside
sled_h = 60  # mm carriage tube depth
wall = 5  # mm carriage tube wall
rail_y = 300  # mm runners from the centreline
x0, x1 = -1060, 250  # mm runners, extended to the tail
block_x_f = 160  # mm front surge blocks
block_x_r = -870  # mm rear surge blocks
pivot_x = -300
pivot_z = 430
post = 80  # mm post square, 6 mm wall
post_x = -1005
post_y = 120
post_top = 530
stroke = 125.3  # mm pin travel each way
drop = 87  # mm block centre below the pin (rod end 77 + half the 20 mm arm)
rail_w = 23
rail_h = 23
block_w = 70
block_h = 13
block_len = 104

model = Model()
zc = sled_z0 + sled_h / 2
top = sled_z0 + sled_h
parts = []


def tube(cid, length, width, at):
    model.box(cid, length, width, sled_h, at=at, op="new")
    void = (length + 4, width - 2 * wall, sled_h - 2 * wall) if length >= width else (
        length - 2 * wall, width + 4, sled_h - 2 * wall)
    model.box(cid + "_void", *void, at=at, op="cut", body=cid)
    parts.append(cid)


model.box("runner_l", x1 - x0, 60, sled_h, at=((x0 + x1) / 2, rail_y, zc))
model.box("runner_l_void", x1 - x0 + 4, 50, sled_h - 2 * wall, at=((x0 + x1) / 2, rail_y, zc), op="cut",
          body="runner_l")
tube("runner_r", x1 - x0, 60, ((x0 + x1) / 2, -rail_y, zc))
for name, x in (("rear", -930), ("mid_b", pivot_x - 70), ("mid_f", pivot_x + 70), ("front", x1 - 30), ("tail", post_x)):
    tube("cross_" + name, 60, 2 * rail_y - 60, (x, 0, zc))

# Post on a foot plate on the tail cross tube, with its strut to the left runner.
model.box("foot", 100, 100, 10, at=(post_x, post_y, top + 5), op="new")
h = post_top - top - 10
model.box("post", post, post, h, at=(post_x, post_y, top + 10 + h / 2), op="new")
model.box("post_void", post - 12, post - 12, h, at=(post_x, post_y, top + 16 + h / 2), op="cut", body="post")
a = (post_x, post_y + post / 2, post_top - 50)
b = (post_x, rail_y, top + 21.2)
length = ((b[1] - a[1]) ** 2 + (b[2] - a[2]) ** 2) ** 0.5
u = (0, (b[1] - a[1]) / length, (b[2] - a[2]) / length)
model.cylinder("strut", 21.2, length, at=a, direction=u, op="new")
model.cylinder("strut_bore", 17.2, length - 40, at=tuple(a[i] + 20 * u[i] for i in range(3)), direction=u, op="cut",
               body="strut")
parts += ["foot", "post", "strut"]

# Rail, and the block at the top of its travel with a load pad where its arm takes the rod end's pull.
r0 = max(top + 10, pivot_z - stroke - drop - block_len / 2)
r1 = pivot_z + stroke - drop + block_len / 2
face = post_y - post / 2 - rail_h
model.box("rail", rail_w, rail_h, r1 - r0, at=(post_x, face + rail_h / 2, (r0 + r1) / 2), op="new")
bz = pivot_z + stroke - drop
model.box("block", block_w, block_h, block_len, at=(post_x, face - block_h / 2, bz), op="new")
model.cylinder("pad", 20, 10, at=(post_x, face - block_h, bz), direction=(0, -1, 0), op="new")
parts += ["rail", "block", "pad"]

# Supports: the surge rail blocks under the runners and the ballscrew nut under the rear mid tube.
for name, x in (("rear", block_x_r), ("front", block_x_f)):
    for side, s in (("l", 1), ("r", -1)):
        bid = "sblock_" + name + "_" + side
        model.box(bid, 84, 70, 1, at=(x, s * rail_y, sled_z0 - 0.5), op="new")
        parts.append(bid)
model.box("nut_bracket", 30, 80, sled_z0 - 20 + 1, at=(pivot_x - 45, 0, (sled_z0 + 1 + 20) / 2), op="new")
model.cylinder("nut", 15, 40, at=(pivot_x - 45 - 20, 0, 35), direction=(1, 0, 0), op="new")
parts += ["nut_bracket", "nut"]

model.combine("weld", "runner_l", parts)
model.material("steel-s235jr", color="#4a515b")
result = model.result()
