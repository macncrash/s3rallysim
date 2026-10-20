"""Rotary crank drive: servo motor on a right-angle planetary gearbox, output shaft to the crank.

Sizes from the chosen parts (bought.py): Apex ABR142 50:1 right-angle gearbox and Kollmorgen
AKM2G-51K servo with brake. Built in the drive's own frame for the left side: origin on the crank axis
in the crank arm's plane, the gearbox outboard along +Y with the motor on its right-angle head. Right-
side drives are placed turned half a turn about Z. The ABR142's standard adapter takes the AKM2G's
114 mm flange directly.
"""

from bought import CRANK_GEARBOX, CRANK_SERVO

FRAME = CRANK_GEARBOX["frame_size_mm"]  # 142 square
LENGTH = CRANK_GEARBOX["overall_length_mm"]  # 365, output shaft end to the head's back
SHAFT = 60  # output shaft out of the flange (40 j6), into the crank hub
HUB = 15  # crank hub half-width: the shaft starts at its face
MOTOR = CRANK_SERVO["flange_mm"]  # 114 square
MOTOR_L = CRANK_SERVO["length_mm"]  # 199.8 with brake

BODY_Y0 = HUB + SHAFT
BODY_Y1 = HUB + LENGTH
HEAD_Y = BODY_Y1 - FRAME / 2


def build(c, motor_dir):
    """motor_dir: -1 motor toward -X, +1 toward +X (in the drive's frame)."""
    c.cylinder("shaft", 20, SHAFT, at=(0, HUB, 0), direction=(0, 1, 0))
    c.box("gearbox", FRAME, BODY_Y1 - BODY_Y0, FRAME, at=(0, (BODY_Y0 + BODY_Y1) / 2, 0), op="new")
    c.box("motor", MOTOR_L, MOTOR, MOTOR, at=(motor_dir * (FRAME / 2 + MOTOR_L / 2), HEAD_Y, 0), op="new")
    c.material("aluminum-6061-t6", color="#b7bcc4")
    c.material("steel-1c45", bodies=["shaft"], color="#9aa1ab")
    c.material("aluminum-6061-t6", bodies=["motor"], color="#2b2f34")
