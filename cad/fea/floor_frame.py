"""S3 Rally Pod moving floor as one welded solid, for STEVE structural studies.

STEVE's static studies solve one solid, so this rebuilds the design's `deck` component (main revision 6,
cad/pod/components/deck.py) with every tube, cheek and yoke joined to the plate. The numbers are copied
from the pod design's parameter and motion files: change them there first, then here.

Idealisations: the floor sheet is welded (or bonded) to the frame along every tube; the steel
universal-joint yokes are modelled as 6061-T6 like the rest; 1 mm load pads on the sheet mark where the
seat rails, dash feet, pedal box, footrest and tunnel bolt down (their study loads come from
analysis/floor_fea_loads.py).

Fixes, off by default so the baseline is the design as it stands:
  clevis_box = 1   each link clevis becomes a welded box tied to the runner and the actuator-line tube
  seat_cross = 1   a cross tube under the seat rails' rear bolts
  yoke_mount = 1   fix H: the yoke lugs on bars between two cross tubes 140 mm either side of the joint
  front_cross = 1  fix G: cross tubes under the dash feet (x 272), the rear pedal and footrest pads (x 440) and the
                   footrest's front pads (x 600)
  front_deep = 40  fix G: extra frame depth ahead of the front links: a solid 20 mm bar under each runner's inboard
                   half (clear of the links) and a 40 mm tube under each edge tube ahead of x 270 (clear of the front
                   gearboxes)
"""

from steve import Model

clevis_box = 0  # 1 adds the clevis boxes
seat_cross = 0  # 1 adds the seat-rail cross tube
yoke_mount = 0  # 1 adds the yoke cross tubes and bars (fix H)
front_cross = 0  # 1 adds the front-bay cross tubes (fix G)
front_deep = 0  # mm extra frame depth ahead of the front actuators (fix G); 0 = none
deck_z = 509  # mm floor sheet centre
deck_t = 4  # mm floor sheet
frame_h = 60  # mm under-frame depth
wall = 4  # mm tube wall
pivot_x = -300  # mm universal joint
pivot_z = 430  # mm universal joint centre
act_xf = 170  # mm front actuator line
act_xr = -770  # mm rear actuator line
act_y = 390  # mm links from the centreline
pin_drop = 45  # mm link top pin below the sheet

model = Model()
X0, X1, W = -940, 790, 660
bot = deck_z - deck_t / 2
top = deck_z + deck_t / 2
zc = bot - frame_h / 2
pin_z = bot - pin_drop

model.box("plate", X1 - X0, 2 * W, deck_t, at=((X0 + X1) / 2, 0, deck_z))

tubes = []


def tube(cid, length, width, at, suppressed=False):
    model.box(cid, length, width, frame_h, at=at, op="new", suppressed=suppressed)
    void = (length + 4, width - 2 * wall, frame_h - 2 * wall) if length >= width else (
        length - 2 * wall, width + 4, frame_h - 2 * wall)
    model.box(cid + "_void", *void, at=at, op="cut", body=cid, suppressed=suppressed)
    if not suppressed:
        tubes.append(cid)


for side, s in (("l", 1), ("r", -1)):
    tube("edge_" + side, X1 - X0, 40, ((X0 + X1) / 2, s * (W - 20), zc))
    tube("runner_" + side, X1 - X0 - 80, 40, ((X0 + X1) / 2, s * 330, zc))
for name, x in (("rear", X0 + 20), ("act_r", act_xr + 70), ("act_f", act_xf - 110), ("front", X1 - 20)):
    tube("cross_" + name, 40, 2 * W - 80, (x, 0, zc))
# Fix: cross tube under the seat rails' rear bolts (rails run x -528..92 for every occupant).
tube("cross_seat", 40, 2 * W - 80, (-512, 0, zc), suppressed=not seat_cross)
# Fix H: cross tubes either side of the joint, and a bar along the frame's depth carrying each yoke lug.
for name, s in (("yoke_b", -1), ("yoke_f", 1)):
    tube("cross_" + name, 40, 2 * W - 80, (pivot_x + s * 140, 0, zc), suppressed=not yoke_mount)
# Fix G: cross tubes in the front bay, under the dash feet and under the rear pedal and footrest pads.
for name, x in (("dash", 272), ("pedal", 440), ("foot", 600)):
    tube("cross_" + name, 40, 2 * W - 80, (x, 0, zc), suppressed=not front_cross)
# Fix G: deeper front frame: a solid bar under each runner's inboard half, a tube under each edge tube.
fd = front_deep or 40
zd, xb = bot - frame_h - fd / 2, X1 - 40
for side, s in (("l", 1), ("r", -1)):
    model.box("runner_deep_" + side, xb - (act_xf - 90), 20, fd, at=((act_xf - 90 + xb) / 2, s * 320, zd), op="new",
              suppressed=not front_deep)
    model.box("edge_deep_" + side, xb - 270, 40, fd, at=((270 + xb) / 2, s * (W - 20), zd), op="new",
              suppressed=not front_deep)
    model.box("edge_deep_" + side + "_void", xb - 270 + 4, 40 - 2 * wall, fd - 2 * wall,
              at=((270 + xb) / 2, s * (W - 20), zd), op="cut", body="edge_deep_" + side, suppressed=not front_deep)
    if front_deep:
        tubes += ["runner_deep_" + side, "edge_deep_" + side]

# Universal joint upper yoke.
low = pivot_z - 25
yokes = []
for name, s in (("l", 1), ("r", -1)):
    model.box("yoke_" + name, 60, 20, bot - low, at=(pivot_x, s * 75, (bot + low) / 2), op="new")
    model.box("yoke_" + name + "_bar", 240, 20, frame_h, at=(pivot_x, s * 75, zc), op="join", body="yoke_" + name,
              suppressed=not yoke_mount)
    model.cylinder("yoke_" + name + "_bore", 18.5, 30, at=(pivot_x, s * 75 - 15, pivot_z), direction=(0, 1, 0),
                   op="cut", body="yoke_" + name)
    yokes.append("yoke_" + name)

# Link top clevises. As designed: two 8 mm cheeks hanging from the sheet alone. With clevis_box the
# cheeks run back to the actuator-line tube and a 6 mm web ties their inner cheek to the runner.
cheeks = []
cl = 60 + (60 if clevis_box else 0)
for name, x, y, toward in (("fl", act_xf, act_y, -1), ("fr", act_xf, -act_y, -1),
                           ("rl", act_xr, act_y, 1), ("rr", act_xr, -act_y, 1)):
    s = 1 if y > 0 else -1
    cx = x + toward * (cl - 60) / 2
    for cheek, dy in (("a", 22), ("b", -22)):
        cid = "clevis_" + name + "_" + cheek
        model.box(cid, cl, 8, pin_drop + 25, at=(cx, y + dy, bot - (pin_drop + 25) / 2), op="new")
        model.cylinder(cid + "_bore", 10.5, 12, at=(x, y + dy - 6, pin_z), direction=(0, 1, 0), op="cut", body=cid)
        cheeks.append(cid)
    web = "web_" + name
    inner = s * (act_y - 26)  # inner cheek's inboard face
    model.box(web, cl, abs(inner - s * 350), 6, at=(cx, (inner + s * 350) / 2, bot - 3), op="new",
              suppressed=not clevis_box)
    if clevis_box:
        cheeks.append(web)

# Load pads: where the cockpit bolts to the sheet (analysis/floor_fea_loads.py names the same ids).
PADS = (
    ("sd_ir", -512.7, 160, 30, 34), ("sd_if", 77.3, 160, 30, 34), ("sd_or", -512.7, 500, 30, 34),
    ("sd_of", 77.3, 500, 30, 34),
    ("sc_ir", -512.7, -160, 30, 34), ("sc_if", 77.3, -160, 30, 34), ("sc_or", -512.7, -500, 30, 34),
    ("sc_of", 77.3, -500, 30, 34),
    ("dash_lf", 301.7, 615, 50, 90), ("dash_lb", 241.7, 615, 50, 90), ("dash_cf", 301.7, 0, 50, 90),
    ("dash_cb", 241.7, 0, 50, 90), ("dash_rf", 301.7, -615, 50, 90), ("dash_rb", 241.7, -615, 50, 90),
    ("ped_fl", 710, 440, 80, 80), ("ped_fr", 710, 220, 80, 80), ("ped_rl", 430, 440, 80, 80),
    ("ped_rr", 430, 220, 80, 80),
    ("foot_fl", 590, -180, 40, 40), ("foot_fr", 590, -480, 40, 40), ("foot_rl", 450, -180, 40, 40),
    ("foot_rr", 450, -480, 40, 40),
    ("tunnel", -60, 50, 120, 60),
)
pads = []
for pid, x, y, lx, ly in PADS:
    model.box("pad_" + pid, lx, ly, 1, at=(x, y, top + 0.5), op="new")
    pads.append("pad_" + pid)

model.combine("weld", "plate", tubes + yokes + cheeks + pads)
model.material("aluminum-6061-t6", color="#4e565f")
result = model.result()
