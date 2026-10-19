"""Rotary crank drive: servo motor on a right-angle planetary gearbox, output shaft to the crank.

Built in the drive's own frame for the left side: origin on the crank axis in the crank arm's
plane, output shaft toward -Y (the gearbox sits inboard). Right-side drives are placed turned half a
turn about Z. Sized from analysis/platform_loads.py: about 2 kW servo, 50:1 gearbox, 800 Nm peak.
"""

GEAR = (150, 120, 150)  # gearbox x, y, z
GEAR_Y = -100  # gearbox centre from the crank plane, inboard
MOTOR_R, MOTOR_L = 60, 240


def build(c, motor_dir):
    """motor_dir: -1 motor toward -X, +1 toward +X (in the drive's frame)."""
    c.box("gearbox", *GEAR, at=(0, GEAR_Y, 0))
    c.cylinder("shaft", 20, -GEAR_Y - GEAR[1] / 2 - 15, at=(0, GEAR_Y + GEAR[1] / 2, 0), direction=(0, 1, 0),
               op="new")
    c.cylinder("motor", MOTOR_R, MOTOR_L, at=(motor_dir * GEAR[0] / 2, GEAR_Y, 0), direction=(motor_dir, 0, 0),
               op="new")
    c.box("encoder", 60, 80, 80, at=(motor_dir * (GEAR[0] / 2 + MOTOR_L + 30), GEAR_Y, 0), op="new")
    c.material("aluminum-6061-t6", color="#b7bcc4")
    c.material("steel-1c45", bodies=["shaft"], color="#9aa1ab")
    c.material("abs", bodies=["encoder"], color="#1a1a1a")
