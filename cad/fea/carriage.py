"""S3 Rally Pod surge carriage as one welded solid, for STEVE structural studies of the centre post's foot.

The carriage's runners and cross tubes (sled.py, main revision 6) with the column plate the centre post
bolts to, held at its four rail blocks. The gearbox outriggers and mounts are left out: they don't carry
the post's load. The numbers are copied from the pod design's parameter and motion files: change them
there first, then here.

Load pads on the column plate (four quadrants) take the post's foot force and moment
(analysis/floor_fea_loads.py, `centre_post`). Supports: the rail block faces under the runners.

Fix, off by default so the baseline is the design as it stands:
  twin_mid = 1   the single mid cross tube under the column becomes two, under the plate's front and rear
                 edges, so the post's fore-aft moment bends two tubes instead of twisting one
"""

from steve import Model

twin_mid = 0  # 1 puts two cross tubes under the column plate
pivot_x = -300  # mm column centre
sled_z0 = 96  # mm carriage frame underside
sled_h = 60  # mm carriage tube depth
wall = 5  # mm tube wall
rail_y = 300  # mm runners from the centreline
block_l = 84  # mm HIWIN HGW25CC block length
block_w = 70  # mm HIWIN HGW25CC block width

model = Model()
X0, X1 = -960, 250
zc = sled_z0 + sled_h / 2
top = sled_z0 + sled_h

model.box("column_plate", 200, 200, 12, at=(pivot_x, 0, top + 6))
tubes = []


def tube(cid, length, width, at, suppressed=False):
    model.box(cid, length, width, sled_h, at=at, op="new", suppressed=suppressed)
    void = (length + 4, width - 2 * wall, sled_h - 2 * wall) if length >= width else (
        length - 2 * wall, width + 4, sled_h - 2 * wall)
    model.box(cid + "_void", *void, at=at, op="cut", body=cid, suppressed=suppressed)
    if not suppressed:
        tubes.append(cid)


for side, s in (("l", 1), ("r", -1)):
    tube("runner_" + side, X1 - X0, 60, ((X0 + X1) / 2, s * rail_y, zc))
for name, x in (("rear", X0 + 30), ("front", X1 - 30)):
    tube("cross_" + name, 60, 2 * rail_y - 60, (x, 0, zc))
tube("cross_mid", 60, 2 * rail_y - 60, (pivot_x, 0, zc), suppressed=bool(twin_mid))
for name, dx in (("f", 70), ("b", -70)):
    tube("cross_mid_" + name, 60, 2 * rail_y - 60, (pivot_x + dx, 0, zc), suppressed=not twin_mid)

pads = []
for name, dx, dy in (("fl", 50, 50), ("fr", 50, -50), ("rl", -50, 50), ("rr", -50, -50)):
    model.box("pad_" + name, 90, 90, 1, at=(pivot_x + dx, dy, top + 12.5), op="new")
    pads.append("pad_" + name)
blocks = []
for name, x in (("rear", X0 + 90), ("front", X1 - 90)):
    for side, s in (("l", 1), ("r", -1)):
        bid = "block_" + name + "_" + side
        model.box(bid, block_l, block_w, 1, at=(x, s * rail_y, sled_z0 - 0.5), op="new")
        blocks.append(bid)

model.combine("weld", "column_plate", tubes + pads + blocks)
model.material("aluminum-6061-t6", color="#3d4450")
result = model.result()
