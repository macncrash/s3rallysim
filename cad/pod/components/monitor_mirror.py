from steve import Component

monitor_mirror = Component("monitor_mirror", name="Rear-view monitor")
monitor_mirror.box("housing", 14, 220, 70, at=(0, 0, 0))
monitor_mirror.box("glass", 2, 200, 52, at=(8, 0, 0), op="new")
monitor_mirror.material("abs", color="#0c0c0c")
monitor_mirror.material("glass-soda-lime", bodies=["glass"], color="#123044")

