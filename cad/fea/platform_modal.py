"""S3 Rally Pod moving floor, universal joint, heave guide and surge carriage as one solid, for a STEVE modal study.

STEVE's modal studies solve one solid, so this joins three models: the floor (floor_frame.py with fixes A and B),
the heave tower (heave_tower.py, fixes C, D and F) and, between them, the universal joint. The numbers are copied
from the pod design's parameter and motion files: change them there first, then here.

Idealisations:
- One material, set per study. The masses are made right with the payload blocks, not the material: run every
  study at steel's density and bound the stiffness with steel's and 6061's modulus, as for the static studies.
- The joint's four pins are short rods (`pin_r`, `pin_len`) from the spider's bosses into the lugs. They take force
  in every direction (the bushings and their flanges) but twist easily about their own axis, so the floor still
  rolls and pitches freely on the crosshead. The spider holds yaw, as the real joint does.
- The floor's roll, pitch and heave are held by the four links: in the study, the link clevis bores are held in Z
  only. Fore-aft, sideways and yaw the floor is held by the joint alone.
- The carriage runs on its rail blocks (held in Y and Z) and is held fore-aft by the surge ballscrew's nut (held in
  X), taken as rigid.
- The cockpit (seats, crew, wheel, dash, pedals) is two steel payload blocks on posts over the seat rails' bolt
  pads, sized so that everything the links carry weighs `floor_mass` (platform_loads.json, crew 95 + 95). They are
  rigid; seat and body compliance is not modelled.
- The guide blocks are welded in, so rigid: their own give is allowed for by hand (docs/floor-structure.md).
- Fix H (the yoke mount) is in by default; `yoke_tube_dx = 0` gives main revision 10's bare-sheet mount.
- Heave at `heave` (default the +40 mm top stop, where the joint is highest above the guide blocks).
"""

from steve import Model

heave = 40  # mm platform heave
floor_mass = 400.5  # kg everything the links carry: 391.5 (platform_loads.json) plus fix H in steel and 6061
payload_kg = 79.4  # kg each payload block: floor_mass less the floor, crosshead and spider as modelled in steel
payload_z = 850  # mm payload blocks' centre at rest
pin_r = 8  # mm joint pin rods
pin_len = 8  # mm free length of each pin rod
# Floor (floor_frame.py)
deck_z = 509
deck_t = 4
frame_h = 60
wall = 4
pivot_x = -300
pivot_z = 430
act_xf = 170
act_xr = -770
act_y = 390
pin_drop = 45
# Heave tower (heave_tower.py)
sled_z0 = 96
sled_h = 60
sled_wall = 5
rail_y = 300
block_x_f = 160
block_x_r = -870
guide_y = 215
col = 100
col_wall = 8
col_top = 415
strut_z = 360
strut_r = 30.15
strut_t = 5
guide_z0 = 207
block_len = 104
block_w = 70
block_h = 13
rail_w = 23
rail_h = 23
lug = 75  # joint lug centres from the pivot
lug_t = 20
yoke_tube_dx = 140  # fix H: yoke cross tubes' centres fore and aft of the pivot (0 = none, the bare-sheet mount)

model = Model()
pz = pivot_z + heave
parts = []

# ---- Floor, raised by `heave`.
FX0, FX1, W = -940, 790, 660
bot = deck_z + heave - deck_t / 2
top = bot + deck_t
fzc = bot - frame_h / 2
model.box("plate", FX1 - FX0, 2 * W, deck_t, at=((FX0 + FX1) / 2, 0, bot + deck_t / 2))


def tube(cid, length, width, height, at, t):
    model.box(cid, length, width, height, at=at, op="new")
    void = (length + 4, width - 2 * t, height - 2 * t) if length >= width else (length - 2 * t, width + 4, height - 2 * t)
    model.box(cid + "_void", *void, at=at, op="cut", body=cid)
    parts.append(cid)


for side, s in (("l", 1), ("r", -1)):
    tube("edge_" + side, FX1 - FX0, 40, frame_h, ((FX0 + FX1) / 2, s * (W - 20), fzc), wall)
    tube("frunner_" + side, FX1 - FX0 - 80, 40, frame_h, ((FX0 + FX1) / 2, s * 330, fzc), wall)
for name, x in (("rear", FX0 + 20), ("act_r", act_xr + 70), ("act_f", act_xf - 110), ("front", FX1 - 20),
                ("seat", -512)):
    tube("fcross_" + name, 40, 2 * W - 80, frame_h, (x, 0, fzc), wall)
if yoke_tube_dx:
    for name, s in (("yoke_b", -1), ("yoke_f", 1)):
        tube("fcross_" + name, 40, 2 * W - 80, frame_h, (pivot_x + s * yoke_tube_dx, 0, fzc), wall)

# Upper yoke: lugs across Y, solid where the pitch pin rods enter; with fix H each hangs from a bar along the
# frame's depth between the yoke cross tubes.
for name, s in (("l", 1), ("r", -1)):
    low = pz - 25
    model.box("yoke_" + name, 60, lug_t, bot - low, at=(pivot_x, s * lug, (bot + low) / 2), op="new")
    parts.append("yoke_" + name)
    if yoke_tube_dx:
        model.box("yoke_" + name + "_bar", 2 * yoke_tube_dx - 40, lug_t, frame_h, at=(pivot_x, s * lug, fzc), op="new")
        parts.append("yoke_" + name + "_bar")

# Link clevises (fix B): cheeks back to the actuator-line tube, web to the runner. Their bores are the Z supports.
pin_zc = bot - pin_drop
for name, x, y, toward in (("fl", act_xf, act_y, -1), ("fr", act_xf, -act_y, -1),
                           ("rl", act_xr, act_y, 1), ("rr", act_xr, -act_y, 1)):
    s = 1 if y > 0 else -1
    cx = x + toward * 30
    for cheek, dy in (("a", 22), ("b", -22)):
        cid = "clevis_" + name + "_" + cheek
        model.box(cid, 120, 8, pin_drop + 25, at=(cx, y + dy, bot - (pin_drop + 25) / 2), op="new")
        model.cylinder(cid + "_bore", 10.5, 12, at=(x, y + dy - 6, pin_zc), direction=(0, 1, 0), op="cut", body=cid)
        parts.append(cid)
    inner = s * (act_y - 26)
    model.box("web_" + name, 120, abs(inner - s * 350), 6, at=(cx, (inner + s * 350) / 2, bot - 3), op="new")
    parts.append("web_" + name)

# Payload: one block per seat on four posts at the seat rails' bolt pads.
for side, s in (("d", 1), ("c", -1)):
    bx, by = (-512.7 + 77.3) / 2, s * 330
    bw, bd = 640, 380
    bh = payload_kg / 7850 / (bw * bd) * 1e9
    zb = payload_z + heave
    model.box("payload_" + side, bw, bd, bh, at=(bx, by, zb), op="new")
    parts.append("payload_" + side)
    for i, (px, py) in enumerate(((-512.7, 160), (-512.7, 500), (77.3, 160), (77.3, 500))):
        pid = f"post_{side}{i}"
        h = zb - bh / 2 - top
        model.box(pid, 50, 50, h + 1, at=(px, s * py, top + h / 2), op="new")
        parts.append(pid)

# ---- Universal joint: spider block, a boss on each arm, and a short pin rod from each boss into its lug.
B = 50
model.box("spider", B, B, B, at=(pivot_x, 0, pz), op="new")
parts.append("spider")
boss_end = lug - lug_t / 2 - pin_len
for axis, d in (("x", (1, 0, 0)), ("y", (0, 1, 0))):
    for side, s in (("p", 1), ("n", -1)):
        u = (s * d[0], s * d[1], 0)
        model.cylinder(f"boss_{axis}{side}", 21, boss_end - B / 2,
                       at=(pivot_x + u[0] * B / 2, u[1] * B / 2, pz), direction=u, op="new")
        model.cylinder(f"pin_{axis}{side}", pin_r, pin_len + 1,
                       at=(pivot_x + u[0] * boss_end, u[1] * boss_end, pz), direction=u, op="new")
        parts += [f"boss_{axis}{side}", f"pin_{axis}{side}"]

# ---- Heave crosshead: ears, rails, bridge and the lower yoke's lugs across X (solid where the roll pin rods enter).
ci = guide_y - col / 2
e_in = ci - block_h - rail_h - 20
for side, s in (("l", 1), ("r", -1)):
    r0, r1 = pz - 263, pz + 25
    model.box("grail_" + side, rail_w, rail_h, r1 - r0, at=(pivot_x, s * (ci - block_h - rail_h / 2), (r0 + r1) / 2),
              op="new")
    model.box("ear_" + side, 40, 20, 300, at=(pivot_x, s * (e_in + 10), pz - 120), op="new")
    parts += ["grail_" + side, "ear_" + side]
model.box("bridge", 180, 2 * (e_in + 10), 30, at=(pivot_x, 0, pz - 70), op="new")
parts.append("bridge")
for name, s in (("f", 1), ("b", -1)):
    model.box("lug_" + name, lug_t, 60, 80, at=(pivot_x + s * lug, 0, pz - 15), op="new")
    parts.append("lug_" + name)

# ---- Surge carriage and heave guide columns (heave_tower.py).
SX0, SX1 = -960, 250
szc = sled_z0 + sled_h / 2
stop = sled_z0 + sled_h
for side, s in (("l", 1), ("r", -1)):
    tube("runner_" + side, SX1 - SX0, 60, sled_h, ((SX0 + SX1) / 2, s * rail_y, szc), sled_wall)
for name, x in (("rear", SX0 + 30), ("mid_b", pivot_x - 70), ("mid_f", pivot_x + 70), ("front", SX1 - 30)):
    tube("cross_" + name, 60, 2 * rail_y - 60, sled_h, (x, 0, szc), sled_wall)
foot_t = 15
for side, s in (("l", 1), ("r", -1)):
    y = s * guide_y
    model.box("foot_" + side, 200, 120, foot_t, at=(pivot_x, y, stop + foot_t / 2), op="new")
    h = col_top - stop - foot_t
    model.box("col_" + side, col, col, h, at=(pivot_x, y, stop + foot_t + h / 2), op="new")
    model.box("col_" + side + "_void", col - 2 * col_wall, col - 2 * col_wall, h,
              at=(pivot_x, y, stop + foot_t + h / 2 + 4), op="cut", body="col_" + side)
    parts += ["foot_" + side, "col_" + side]
    for k in (0, 1):
        bid = f"gblock_{side}{k}"
        model.box(bid, block_w, block_h, block_len,
                  at=(pivot_x, s * (ci - block_h / 2), guide_z0 + block_len * (k + 0.5)), op="new")
        parts.append(bid)
    for end, bx in (("f", block_x_f), ("b", block_x_r)):
        a = (pivot_x, y, strut_z)
        b = (bx, s * rail_y, stop + strut_r)
        dv = tuple(b[i] - a[i] for i in range(3))
        length = sum(v * v for v in dv) ** 0.5
        u = tuple(v / length for v in dv)
        sid = f"strut_{side}{end}"
        model.cylinder(sid, strut_r, length, at=a, direction=u, op="new")
        model.cylinder(sid + "_bore", strut_r - strut_t, length - 60, at=tuple(a[i] + 30 * u[i] for i in range(3)),
                       direction=u, op="cut", body=sid)
        model.box(f"land_{side}{end}", 120, 60, 10, at=(bx, s * rail_y, stop + 5), op="new")
        parts += [sid, f"land_{side}{end}"]

# Supports: the surge rail blocks under the runners (Y, Z) and the ballscrew nut under the rear mid tube (X).
for name, x in (("rear", block_x_r), ("front", block_x_f)):
    for side, s in (("l", 1), ("r", -1)):
        bid = "sblock_" + name + "_" + side
        model.box(bid, 84, 70, 1, at=(x, s * rail_y, sled_z0 - 0.5), op="new")
        parts.append(bid)
model.box("nut_bracket", 30, 80, sled_z0 - 20 + 1, at=(pivot_x - 45, 0, (sled_z0 + 1 + 20) / 2), op="new")
model.cylinder("nut", 15, 40, at=(pivot_x - 45 - 20, 0, 35), direction=(1, 0, 0), op="new")
parts += ["nut_bracket", "nut"]

model.combine("weld", "plate", parts)
model.material("steel-s235jr", color="#4a515b")
result = model.result()
