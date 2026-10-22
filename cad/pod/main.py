"""S3 Rally Pod. Enclosed two-seat cockpit for rally training, on a four-axis motion floor.

Four axes move the floor, and both seats, both occupants, the wheel, pedals, dash frame and
shifter with it. Surge is fore-aft, roll is about X, pitch is about Y, heave is vertical.
The windscreen and side-window displays, the doors and the shell stay still.

layout 0 is the rally template: LHD, driver on the left, co-driver / instructor on the right
with a telemetry display, both on the intercom. layout 1 is the formula template: one reclined
seat on the centreline, no co-driver.

The occupants are 5th or 95th percentile mannequins in race gear (driver_pct, codriver_pct);
ergo.py places the seats, column and pedals for them. Their mass is a lumped mass at the torso.

The motion platform (motion.py): four rotary crank actuators lift the floor's corners through
upright links; a passive heave guide with a universal joint under the floor's centre of mass takes
the side loads and is the roll and pitch pivot; the lot rides a surge carriage. STEVE doesn't solve
closed loops, so each crank and link is geared to the floor's axes (small-angle ratios); the build
checks every pose of the motion cue against the exact crank geometry and refuses one out of reach.
"""

import math
from steve import Design
from params import (
    layout, surge_mm, roll_deg, pitch_deg, heave_mm, screen_x, screen_z, deck_top, shell_half_w,
    seat_y, driver_pct, codriver_pct,
)
import ergo
import motion
from components.shell import shell, DOOR_X0
from components.door import door
from components.door_r import door_r
from components.display_55 import display_55
from components.monitor_27 import monitor_27
from components.monitor_mirror import monitor_mirror
from components.bezel import bezel
from components.base import base
from components.sled import sled
from components.heave_car import heave_car
from components.ujoint import ujoint
from components.deck import deck
from components.yaw_block import yaw_block
from components.drive_a import drive_a
from components.drive_b import drive_b
from components.crank_l import crank_l
from components.crank_r import crank_r
from components.link import link
from components.seat import seat
from components.mount_driver import mount_driver
from components.mount_codriver import mount_codriver
from components.driver import driver
from components.codriver import codriver
from components.pedals import pedals
from components.footrest import footrest
from components.wheel import wheel
from components.dash import dash
from components.tunnel import tunnel
from components.dogbox import dogbox
from components.dog_cap import dog_cap
from components.lever import lever
from components.knob import knob
from components.handbrake import handbrake
from components.hb_lever import hb_lever
from components.button_box import button_box

design = Design("S3 Rally Pod")
rally = ergo.rally

BEZEL = {
    "process": "fdm",
    "build_direction": "+X",
    "material": "abs",
    "notes": "Lay the frame flat. 4 perimeters, 25% infill.",
}
NYLON = {
    "process": "fdm",
    "build_direction": "+Z",
    "material": "pa6",
    "notes": "5 perimeters. Bearings drop in from the top, then the cap bolts on.",
}

# Shell, doors and fixed displays.
door_y = shell_half_w + 48
design.add(shell)
design.add(door, at=(DOOR_X0, door_y, 0))
design.add(door_r, at=(DOOR_X0, -door_y, 0))
design.add(display_55, name="windscreen", at=((screen_x, 0, screen_z), ("Z", 180)))
side_x, side_y, side_z = 620, shell_half_w - 140, screen_z - 30
design.add(monitor_27, name="window_l", at=((side_x, side_y, side_z), ("Z", -110)))
design.add(monitor_27, name="window_r", at=((side_x, -side_y, side_z), ("Z", 110)))
design.add(bezel, name="bezel_l", at=((side_x - 7, side_y - 19, side_z), ("Z", -110)), print=BEZEL)
design.add(bezel, name="bezel_r", at=((side_x - 7, -side_y + 19, side_z), ("Z", 110)), print=BEZEL)
design.add(monitor_mirror, name="mirror", at=((screen_x - 40, 0, screen_z + 430), ("Z", 180)))

# Motion stack.
design.add(base)
design.add(sled)
design.add(heave_car)
design.add(ujoint)
design.add(deck)
design.add(yaw_block)
DRIVES = {"fl": (drive_a, 0), "rr": (drive_a, 180), "rl": (drive_b, 0), "fr": (drive_b, 180)}
for name, x, y in motion.ACTUATORS:
    side = 1 if y > 0 else -1
    ax = motion.crank_axis(x, y)
    plane = (ax[0], y + side * motion.CRANK_DY, ax[2])
    comp, turn = DRIVES[name]
    design.add(comp, name="drive_" + name, at=(plane, ("Z", turn)))
    design.add(crank_l if side > 0 else crank_r, name="crank_" + name, at=plane)
    design.add(link, name="link_" + name, at=motion.crank_tip(x, y))

# Cockpit on the moving floor.
d_seat = (ergo.seat_x(driver_pct), ergo.DRIVER_Y, ergo.seat_z(driver_pct))
design.add(seat, name="seat_d", at=d_seat)
design.add(mount_driver, at=d_seat)
design.add(driver)
design.add(wheel)
design.add(dash)
design.add(pedals)

design.revolute("door_hinge", "shell", "door", axis=door.face("pin.side"), limits=(0, 105))
design.revolute("door_r_hinge", "shell", "door_r", axis=door_r.face("pin.side"), limits=(-105, 0))
design.slider("surge", "base", "sled", axis="X", limits=(-surge_mm, surge_mm))
design.slider("heave", "sled", "heave_car", axis="Z", limits=(-heave_mm, heave_mm))
# The pitch pin is in the crosshead and the roll pin in the floor, so the floor's roll axis stays on the centreline
# and the yaw restraint behind the floor can hold it sideways (motion.floor_point).
design.revolute("pitch", "heave_car", "ujoint", axis=ujoint.face("pin_y.side"), limits=(-pitch_deg, pitch_deg))
design.revolute("roll", "ujoint", "deck", axis=ujoint.face("pin_x.side"), limits=(-roll_deg, roll_deg))
# The yaw restraint's slider follows its pin: up with heave, and up as pitch raises the floor's tail (small-angle
# gearing, so its range is a fraction of a millimetre past the pin's exact travel, motion.YAW_STROKE).
yaw_gear = (motion.pivot_x - motion.YAW_PIN_X) * math.pi / 180  # mm per degree of pitch
yaw_travel = heave_mm + yaw_gear * pitch_deg
design.slider("yaw_slide", "sled", "yaw_block", axis="Z", limits=(-yaw_travel, yaw_travel))
for name, x, y in motion.ACTUATORS:
    crank = crank_l if y > 0 else crank_r
    design.rigid("drive_" + name + "_on", "sled", "drive_" + name)
    design.revolute("crank_" + name, "drive_" + name, "crank_" + name, axis=crank.face("hub.side"), limits=(-80, 80))
    design.revolute("link_" + name, "crank_" + name, "link_" + name, axis=link.face("eye_lo.side"), limits=(-80, 80))

design.rigid("seat_d_on", "deck", "seat_d")
design.rigid("mount_d_on", "deck", "mount_driver")
design.rigid("driver_in", "seat_d", "driver")
design.rigid("wheel_on", "deck", "wheel")
design.rigid("dash_on", "deck", "dash")
design.rigid("pedals_on", "deck", "pedals")

# Each crank (and its link, kept upright) follows the floor's axes with small-angle ratios.
gears = {"heave_drive": {"heave": 1}, "pitch_drive": {"pitch": 1}, "roll_drive": {"roll": 1}}
gears["heave_drive"]["yaw_slide"] = 1
gears["pitch_drive"]["yaw_slide"] = yaw_gear
for name, x, y in motion.ACTUATORS:
    for (axis, g), ratio in zip(gears.items(), motion.crank_ratios(x, y)):
        g["crank_" + name] = ratio
        g["link_" + name] = -ratio
design.couple("heave_drive", gears["heave_drive"], limits=(-heave_mm, heave_mm))
design.couple("pitch_drive", gears["pitch_drive"], limits=(-pitch_deg, pitch_deg))
design.couple("roll_drive", gears["roll_drive"], limits=(-roll_deg, roll_deg))
design.couple("surge_drive", {"surge": 1}, limits=(-surge_mm, surge_mm))

dp = ergo.posture(driver_pct, "driver")
b = ergo.BODY[driver_pct]
design.lumped_mass("driver_mass", "driver", dp["mass_kg"] * 1000, at=dp["com"],
                   box=(300, 2 * b["shoulder_half"], b["torso"]))
occupants = ["driver"]

if rally:
    c_seat = (ergo.seat_x(codriver_pct), -seat_y, ergo.seat_z(codriver_pct))
    design.add(seat, name="seat_c", at=c_seat)
    design.add(mount_codriver, at=c_seat)
    design.add(codriver)
    design.add(footrest)
    design.rigid("seat_c_on", "deck", "seat_c")
    design.rigid("mount_c_on", "deck", "mount_codriver")
    design.rigid("codriver_in", "seat_c", "codriver")
    design.rigid("footrest_on", "deck", "footrest")
    cp = ergo.posture(codriver_pct, "codriver")
    cb = ergo.BODY[codriver_pct]
    design.lumped_mass("codriver_mass", "codriver", cp["mass_kg"] * 1000, at=cp["com"],
                       box=(300, 2 * cb["shoulder_half"], cb["torso"]))
    occupants.append("codriver")

    # Centre console between the seats: sequential stick, hydraulic handbrake, button box.
    cy = 50
    design.add(tunnel, at=(-40, cy, deck_top))
    design.add(dogbox, at=(-40, cy, deck_top + 12), print=NYLON)
    design.add(
        dog_cap, at=(-40, cy, deck_top + 92),
        print={
            "process": "fdm", "build_direction": "+Z", "material": "pa6",
            "notes": "Bolt on after the 608 bearings are seated. 5 perimeters.",
        },
    )
    design.add(lever, at=(-40, cy, deck_top + 81))
    design.add(
        knob, at=(-40, cy, deck_top + 307),
        print={
            "process": "fdm", "build_direction": "+Z", "material": "abs",
            "notes": "Pin or press onto the 8 mm steel stick.",
        },
    )
    design.add(handbrake, at=(-230, cy, deck_top + 12))
    design.add(
        hb_lever, at=(-230, cy, deck_top + 36),
        print={
            "process": "fdm", "build_direction": "+Y", "material": "pa6",
            "notes": "Print with the pivot hole vertical. Pivot is a bought M8 bolt.",
        },
    )
    design.add(
        button_box, at=(120, cy, deck_top + 12),
        print={
            "process": "fdm", "build_direction": "+Z", "material": "abs",
            "notes": "Six bought 12 mm buttons. 4 perimeters.",
        },
    )
    design.rigid("tunnel_on", "deck", "tunnel")
    design.rigid("box_on", "deck", "dogbox")
    design.rigid("cap_on", "dogbox", "dog_cap")
    design.revolute("shift", "dogbox", "lever", axis=lever.face("pivot.side"), limits=(-8, 8))
    design.rigid("knob_on", "lever", "knob")
    design.rigid("hb_on", "deck", "handbrake")
    design.revolute("hand_brake", "handbrake", "hb_lever", axis=handbrake.face("bore_l.side"), limits=(0, 30))
    design.rigid("buttons_on", "deck", "button_box")

CUE = {
    "rest": dict(heave_drive=0, surge_drive=0, roll_drive=0, pitch_drive=0),
    "bump": dict(heave_drive=22, pitch_drive=2, surge_drive=-8, roll_drive=0),
    "jump": dict(heave_drive=32, pitch_drive=7, surge_drive=18, roll_drive=1),
    "air": dict(heave_drive=8, pitch_drive=4, surge_drive=40, roll_drive=-1),
    "land": dict(heave_drive=-40, pitch_drive=-7, surge_drive=-30, roll_drive=-2),
    "corner": dict(roll_drive=-7, heave_drive=12, pitch_drive=-1, surge_drive=6),
}
# The motion cue must stay inside the cranks' reach (+-65 deg): checked on the exact geometry.
for pose, v in CUE.items():
    for name, x, y in motion.ACTUATORS:
        a = motion.crank_angle(x, y, v["heave_drive"], v["pitch_drive"], v["roll_drive"])
        if a is None or abs(a) > 65:
            raise ValueError(f"pose {pose!r} is out of reach for actuator {name}: crank {a}")
for pose, v in CUE.items():
    design.pose(pose, **v, **({"door_hinge": 0, "door_r_hinge": 0} if pose == "rest" else {}))
design.pose("entry", door_hinge=100, door_r_hinge=-100)
# Cabin envelope: every axis at its stop at once. Beyond the actuators' reach on purpose: a
# conservative superset of the motion for the occupants' clearance check only.
design.pose("env_fl", surge_drive=surge_mm, pitch_drive=pitch_deg, roll_drive=roll_deg, heave_drive=heave_mm)
design.pose("env_fr", surge_drive=surge_mm, pitch_drive=pitch_deg, roll_drive=-roll_deg, heave_drive=heave_mm)
design.pose("env_bl", surge_drive=-surge_mm, pitch_drive=-pitch_deg, roll_drive=roll_deg, heave_drive=heave_mm)
design.pose("env_br", surge_drive=-surge_mm, pitch_drive=-pitch_deg, roll_drive=-roll_deg, heave_drive=heave_mm)

design.animation(
    "rally_stage",
    [
        ("rest", 0),
        ("bump", 1.2),
        ("rest", 2.0),
        ("jump", 3.2),
        ("air", 4.2),
        ("land", 5.0),
        ("rest", 6.4),
        ("corner", 8.0),
        ("rest", 9.6),
    ],
    loop=True,
)

# Ergonomic fit: occupants against everything they could hit, at rest, through each axis and
# at the envelope corners. Occupants sit in their seats, gloves hold the rim, boots rest on the
# pedals and the footrest: those are the only designed contacts.
cabin = ["shell", "door", "door_r", "windscreen", "window_l", "window_r", "bezel_l", "bezel_r", "mirror"]
cockpit = ["wheel", "dash", "pedals", "seat_d"] + (["seat_c", "footrest", "tunnel", "dogbox", "lever", "knob",
                                                    "handbrake", "hb_lever", "button_box"] if rally else [])
design.contact("driver", "seat_d", kind="seated", max_overlap_mm3=4_000_000)
design.contact("driver", "wheel", kind="seated", max_overlap_mm3=400_000)
design.contact("driver", "pedals", kind="seated", max_overlap_mm3=300_000)
design.contact("wheel", "dash", kind="seated", max_overlap_mm3=80_000)  # column clamp on the crossbar
pairs = {}
for who in occupants:
    for other in cabin:
        pairs[(who, other)] = 50
    pairs[(who, "dash")] = 25
if rally:
    design.contact("codriver", "seat_c", kind="seated", max_overlap_mm3=4_000_000)
    design.contact("codriver", "footrest", kind="seated", max_overlap_mm3=600_000)
    pairs[("driver", "codriver")] = 20
    pairs[("driver", "lever")] = 15
    pairs[("driver", "knob")] = 15
design.clearance(0, pairs=pairs)
design.fit_check(
    "occupants",
    instances=occupants + cabin + cockpit,
    poses=["rest", "jump", "land", "corner", "env_fl", "env_fr", "env_bl", "env_br"],
)

# Platform fit: the mechanism against itself, the floor's under-frame and the shell, through the
# motion cue (reachable poses) and each axis. Pins in their eyes, blocks on rails (surge and heave
# guides, yaw restraint) and the drives on the carriage are the designed contacts.
mech = ["base", "sled", "heave_car", "ujoint", "deck", "yaw_block"] + [
    p + "_" + n for n, _x, _y in motion.ACTUATORS for p in ("drive", "crank", "link")]
design.contact("sled", "base", kind="seated", max_overlap_mm3=1_000)
design.contact("heave_car", "sled", kind="seated", max_overlap_mm3=1_000)
design.contact("ujoint", "heave_car", kind="seated", max_overlap_mm3=2_000)
design.contact("ujoint", "deck", kind="seated", max_overlap_mm3=2_000)
design.contact("yaw_block", "sled", kind="seated", max_overlap_mm3=1_000)
design.contact("yaw_block", "deck", kind="seated", max_overlap_mm3=2_000)
for n, _x, _y in motion.ACTUATORS:
    design.contact("drive_" + n, "sled", kind="seated", max_overlap_mm3=1_000)
    design.contact("crank_" + n, "drive_" + n, kind="seated", max_overlap_mm3=2_000)
    design.contact("link_" + n, "crank_" + n, kind="seated", max_overlap_mm3=2_000)
    design.contact("link_" + n, "deck", kind="seated", max_overlap_mm3=2_000)
design.fit_check("platform", instances=mech + ["shell", "mount_driver", "mount_codriver"] if rally else
                 mech + ["shell", "mount_driver"], poses=list(CUE))

design.explode(
    "major",
    [
        {"move": ["door", "door_r"], "along": "+Z", "distance": 400},
        {"move": ["window_l", "bezel_l"], "along": "+Y", "distance": 280},
        {"move": ["window_r", "bezel_r"], "along": "-Y", "distance": 280},
        {"move": occupants, "along": "+Z", "distance": 900},
    ],
)

result = design.result()
