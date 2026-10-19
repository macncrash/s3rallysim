from steve import Component

monitor_27 = Component("monitor_27", name="27 inch monitor")
monitor_27.box("housing", 22, 630, 372, at=(0, 0, 0))
monitor_27.box("glass", 3, 598, 336, at=(12, 0, 0), op="new")
monitor_27.material("abs", color="#0c0c0c")
monitor_27.material("glass-soda-lime", bodies=["glass"], color="#123044")

