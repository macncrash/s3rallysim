from steve import Component
import drive_parts

# Crank drive, motor pointing -X: front left, and rear right turned half a turn.
drive_a = Component("drive_a", name="Crank drive (motor aft)")
drive_parts.build(drive_a, -1)
