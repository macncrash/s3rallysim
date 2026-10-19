from steve import Component

bezel = Component("bezel", name="27 inch bezel")
bezel.box("frame", 14, 668, 410, at=(0, 0, 0))
bezel.box("window", 20, 608, 346, at=(0, 0, 0), op="cut")
bezel.material("abs", color="#1a1a1a")

