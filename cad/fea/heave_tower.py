"""S3 Rally Pod heave guide tower on the surge carriage, as one welded solid, for STEVE structural studies.

Fixes D and F together (docs/floor-structure.md): the single centre post with its sliding sleeve is replaced by two
fixed steel columns either side of the universal joint, each braced by two struts straight down to the surge rail
blocks, and a crosshead that carries the joint's lower yoke and runs on one HIWIN HGW25CC guide rail per column
(two blocks each, fixed to the column). The numbers are copied from the pod design's parameter and motion files:
change them there first, then here.

Idealisations: everything welded into one solid, so the guide blocks are rigid (their own rigidity is a vendor
value, checked by hand in docs/floor-structure.md) and steel and aluminium parts share one material, set per study.
The crosshead sits at `heave` (default the +40 mm top stop, where the joint is highest above the blocks).
Supports: the rail block faces under the runners. Loads: the joint's force on the two lower-yoke lug bores.
"""

from steve import Model

heave = 40  # mm crosshead position (+40 top stop)
pivot_x = -300  # mm universal joint
pivot_z = 430  # mm universal joint centre at rest
sled_z0 = 96  # mm carriage frame underside
sled_h = 60  # mm carriage tube depth
wall = 5  # mm carriage tube wall
rail_y = 300  # mm surge rails from the centreline
block_x_f = 160  # mm front surge blocks
block_x_r = -870  # mm rear surge blocks
guide_y = 215  # mm column centres from the centreline
col = 100  # mm column square
col_wall = 8  # mm column wall
col_top = 415  # mm column top
strut_z = 360  # mm strut node on the column
strut_r = 30.15  # mm CHS 60.3 x 5
strut_t = 5  # mm strut wall
guide_z0 = 207  # mm lower guide block bottom
block_len = 104  # mm HGW25CC + E2 block length
block_w = 70  # mm block width
block_h = 13  # mm block above the rail
rail_w = 23  # mm guide rail width
rail_h = 23  # mm guide rail height

model = Model()
X0, X1 = -960, 250
zc = sled_z0 + sled_h / 2
top = sled_z0 + sled_h
pz = pivot_z + heave

# Carriage: runners, end cross tubes and the twin mid tubes (fix C).
model.box("runner_l", X1 - X0, 60, sled_h, at=((X0 + X1) / 2, rail_y, zc))
parts = []


def tube(cid, length, width, at):
    model.box(cid, length, width, sled_h, at=at, op="new")
    void = (length + 4, width - 2 * wall, sled_h - 2 * wall) if length >= width else (
        length - 2 * wall, width + 4, sled_h - 2 * wall)
    model.box(cid + "_void", *void, at=at, op="cut", body=cid)
    parts.append(cid)


model.box("runner_l_void", X1 - X0 + 4, 50, sled_h - 2 * wall, at=((X0 + X1) / 2, rail_y, zc), op="cut",
          body="runner_l")
tube("runner_r", X1 - X0, 60, ((X0 + X1) / 2, -rail_y, zc))
for name, x in (("rear", X0 + 30), ("mid_b", pivot_x - 70), ("mid_f", pivot_x + 70), ("front", X1 - 30)):
    tube("cross_" + name, 60, 2 * rail_y - 60, (x, 0, zc))

ci = guide_y - col / 2  # column inner face
foot_t = 15
for side, s in (("l", 1), ("r", -1)):
    y = s * guide_y
    # Column on a foot plate spanning the twin tubes.
    model.box("foot_" + side, 200, 120, foot_t, at=(pivot_x, y, top + foot_t / 2), op="new")
    h = col_top - top - foot_t
    model.box("col_" + side, col, col, h, at=(pivot_x, y, top + foot_t + h / 2), op="new")
    model.box("col_" + side + "_void", col - 2 * col_wall, col - 2 * col_wall, h, at=(pivot_x, y, top + foot_t + h / 2 + 4),
              op="cut", body="col_" + side)
    parts += ["foot_" + side, "col_" + side]
    # Guide blocks on the column's inner face, rail and ear on the crosshead.
    for k in (0, 1):
        bid = f"gblock_{side}{k}"
        model.box(bid, block_w, block_h, block_len, at=(pivot_x, s * (ci - block_h / 2), guide_z0 + block_len * (k + 0.5)),
                  op="new")
        parts.append(bid)
    r0, r1 = pz - 263, pz + 25
    model.box("grail_" + side, rail_w, rail_h, r1 - r0, at=(pivot_x, s * (ci - block_h - rail_h / 2), (r0 + r1) / 2),
              op="new")
    e_in = ci - block_h - rail_h - 20
    model.box("ear_" + side, 40, 20, 300, at=(pivot_x, s * (e_in + 10), pz - 120), op="new")
    parts += ["grail_" + side, "ear_" + side]
    # Struts to the surge rail blocks, landing on a plate on the runner.
    for end, bx in (("f", block_x_f), ("b", block_x_r)):
        a = (pivot_x, y, strut_z)
        b = (bx, s * rail_y, top + strut_r)
        d = tuple(b[i] - a[i] for i in range(3))
        length = sum(v * v for v in d) ** 0.5
        u = tuple(v / length for v in d)
        sid = f"strut_{side}{end}"
        model.cylinder(sid, strut_r, length, at=a, direction=u, op="new")
        model.cylinder(sid + "_bore", strut_r - strut_t, length - 60, at=tuple(a[i] + 30 * u[i] for i in range(3)),
                       direction=u, op="cut", body=sid)
        model.box(f"land_{side}{end}", 120, 60, 10, at=(bx, s * rail_y, top + 5), op="new")
        parts += [sid, f"land_{side}{end}"]

# Crosshead: a bridge between the ears, with the lower yoke's two lugs (the roll pin runs along X through them).
model.box("bridge", 180, 2 * (e_in + 10), 30, at=(pivot_x, 0, pz - 70), op="new")
parts.append("bridge")
for name, dx in (("f", 75), ("b", -75)):
    model.box("lug_" + name, 20, 60, 80, at=(pivot_x + dx, 0, pz - 15), op="new")
    model.cylinder("lug_" + name + "_bore", 18.5, 30, at=(pivot_x + dx - 15, 0, pz), direction=(1, 0, 0), op="cut",
                   body="lug_" + name)
    parts.append("lug_" + name)

# Support faces: the surge rail blocks under the runners.
for name, x in (("rear", block_x_r), ("front", block_x_f)):
    for side, s in (("l", 1), ("r", -1)):
        bid = "sblock_" + name + "_" + side
        model.box(bid, 84, 70, 1, at=(x, s * rail_y, sled_z0 - 0.5), op="new")
        parts.append(bid)

model.combine("weld", "runner_l", parts)
model.material("steel-s235jr", color="#4a515b")
result = model.result()
