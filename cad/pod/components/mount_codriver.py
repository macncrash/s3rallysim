from steve import Component
from params import codriver_pct
import seat_mounts

mount_codriver = Component("mount_codriver", name="Co-driver seat rails")
seat_mounts.build(mount_codriver, codriver_pct)
