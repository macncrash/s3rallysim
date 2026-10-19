from steve import Component
import drive_parts

# Crank drive, motor pointing +X: rear left, and front right turned half a turn.
drive_b = Component("drive_b", name="Crank drive (motor forward)")
drive_parts.build(drive_b, 1)
