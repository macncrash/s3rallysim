from steve import Component
from params import pivot_x, pivot_z

# Universal joint spider: the roll pin along X sits in the heave sleeve's lugs, the pitch pin along
# Y in the floor's lugs. Its centre is the motion platform's roll and pitch pivot.
ujoint = Component("ujoint", name="Universal joint spider")
ujoint.box("block", 50, 50, 50, at=(pivot_x, 0, pivot_z))
ujoint.cylinder("pin_x", 18, 180, at=(pivot_x - 90, 0, pivot_z), direction=(1, 0, 0), op="new")
ujoint.cylinder("pin_y", 18, 180, at=(pivot_x, -90, pivot_z), direction=(0, 1, 0), op="new")
ujoint.material("steel-34crnimo6", color="#b8bec6")
