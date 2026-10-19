from steve import Component

# Mirror of the left door: the co-driver's / instructor's door.
door_r = Component("door_r", name="Right door")
door_r.cylinder("pin", 7, 1060, at=(0, 0, 260), direction=(0, 0, 1), op="new")
door_r.box("skin", 920, 8, 1240, at=(490, -14, 960), op="new")
door_r.box("stripe", 920, 3, 64, at=(490, -21, 1240), op="new")
door_r.material("abs", color="#161616")
door_r.material("abs", bodies=["stripe", "pin"], color="#ff4d00")
