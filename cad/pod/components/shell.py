from steve import Component
from params import shell_h, shell_front, shell_rear, shell_half_w, screen_x, screen_z

shell = Component("shell", name="Enclosure frame")

POST = 40
W = shell_half_w
DOOR_X0 = -400  # door hinge (rear edge of the opening)
DOOR_X1 = 540  # front edge of the opening
LENGTH = shell_front - shell_rear
MID_X = (shell_front + shell_rear) / 2


def tube(cid, length, width, height, at):
    shell.box(cid, length, width, height, at=at, op="new")
    if length >= width and length >= height:
        void = (length + 4, width - 12, height - 12)
    elif width >= length and width >= height:
        void = (length - 12, width + 4, height - 12)
    else:
        void = (length - 12, width - 12, height + 4)
    shell.box(cid + "_void", void[0], void[1], void[2], at=at, op="cut", body=cid)


z0 = 16
height = shell_h - z0
zc = z0 + height / 2
for name, x, y in (("fl", shell_front, W), ("fr", shell_front, -W), ("bl", shell_rear, W), ("br", shell_rear, -W)):
    tube("post_" + name, POST, POST, height, (x, y, zc))

# Floor and roof rings. Ends stop on the post faces so the corners do not stack.
side_len = LENGTH - POST
end_len = 2 * W - POST
roof_z = shell_h - 20
for level, z in (("rail", 36), ("roof", roof_z)):
    tube(level + "_l", side_len, POST, POST, (MID_X, W, z))
    tube(level + "_r", side_len, POST, POST, (MID_X, -W, z))
    tube(level + "_b", POST, end_len, POST, (shell_rear + POST / 2, 0, z))
    tube(level + "_f", POST, end_len, POST, (shell_front - POST / 2, 0, z))

# Door frames on both sides. Header and jambs meet the rails on a face.
jamb_h = shell_h - 360
jamb_z = 56 + jamb_h / 2
header_z = 56 + jamb_h + POST / 2
for side, s in (("l", 1), ("r", -1)):
    tube("jamb_a_" + side, POST, POST, jamb_h, (DOOR_X0 + 60, s * W, jamb_z))
    tube("jamb_b_" + side, POST, POST, jamb_h, (DOOR_X1, s * W, jamb_z))
    tube("header_" + side, DOOR_X1 - DOOR_X0 - 20, POST, POST, ((DOOR_X0 + DOOR_X1) / 2 + 30, s * W, header_z))
    for knuckle, z in (("lo", 300), ("hi", 1250)):
        kid = "knuckle_" + knuckle + "_" + side
        shell.box(kid, 36, 36, 56, at=(DOOR_X0, s * (W + 48), z), op="new")
        shell.cylinder(kid + "_bore", 8.5, 70, at=(DOOR_X0, s * (W + 48), z - 28), direction=(0, 0, 1), op="cut",
                       body=kid)
    # Side skins: below and above the door, and solid ahead of and behind it.
    wall_y = s * (W - 27)
    shell.box("wall_low_" + side, LENGTH - 80, 6, 130, at=(MID_X, wall_y, 115), op="new")
    top_h = shell_h - 48 - header_z
    shell.box("wall_high_" + side, LENGTH - 80, 6, top_h, at=(MID_X, wall_y, header_z + top_h / 2), op="new")
    mid_h = header_z - 180
    rear_len = DOOR_X0 + 40 - (shell_rear + 40)
    shell.box("wall_rear_" + side, rear_len, 6, mid_h, at=(shell_rear + 40 + rear_len / 2, wall_y, 180 + mid_h / 2),
              op="new")
    front_len = shell_front - 40 - (DOOR_X1 + 20)
    shell.box("wall_front_" + side, front_len, 6, mid_h, at=(DOOR_X1 + 20 + front_len / 2, wall_y, 180 + mid_h / 2),
              op="new")
    shell.box("step_low_" + side, 460, 240, 180, at=(70, s * (W + 300), 90), op="new")
    shell.box("step_high_" + side, 460, 200, 150, at=(70, s * (W + 180), 255), op="new")

shell.box("floor", LENGTH - 60, 2 * W - 40, 12, at=(MID_X, 0, 6), op="new")
# Pit for the motion base, cranks and the moving floor's travel.
shell.box("pit", 1980, 1400, 28, at=(-125, 0, 10), op="cut", body="floor")
shell.box("wall_b", 6, 2 * W - 80, shell_h - 120, at=(shell_rear + 27, 0, shell_h / 2), op="new")
shell.box("roof", LENGTH - 80, 2 * W - 80, 6, at=(MID_X, 0, shell_h - 48), op="new")
shell.box("valance", 50, 2 * W - 140, 70, at=(shell_front - 80, 0, shell_h - 125), op="new")

# Display mount: two beams between the front posts and brackets to the display's back.
for name, z in (("beam_lo", screen_z - 300), ("beam_hi", screen_z + 300)):
    shell.box(name, 40, 2 * W - 40, 60, at=(shell_front - 40, 0, z), op="new")
    for bname, y in (("_l", 400), ("_r", -400)):
        length = shell_front - 60 - (screen_x + 40)
        shell.box(name + bname, length, 40, 40, at=(screen_x + 40 + length / 2, y, z), op="new")

shell.cylinder("estop_base", 16, 22, at=(DOOR_X1 + 120, -W + 30, 1100), direction=(0, 1, 0), op="new")
shell.cylinder("estop_cap", 22, 12, at=(DOOR_X1 + 120, -W + 52, 1100), direction=(0, 1, 0), op="new")

panels = ["floor", "wall_b", "roof"] + [
    p + "_" + s for p in ("wall_low", "wall_high", "wall_rear", "wall_front", "step_low", "step_high") for s in "lr"
]
shell.material("aluminum-6061-t6", finish="powder-coated", color="#1c1f24")
shell.material("abs", bodies=panels, color="#141414")
shell.material("abs", bodies=["estop_base", "estop_cap"], color="#d00000")
shell.material("aluminum-6061-t6", bodies=["valance"], color="#2a2e33")
