from steve import Component
from params import driver_pct
import seat_mounts

mount_driver = Component("mount_driver", name="Driver seat rails")
seat_mounts.build(mount_driver, driver_pct)
