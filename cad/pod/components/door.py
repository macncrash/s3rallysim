from steve import Component

door = Component("door", name="Left door")
door.cylinder("pin", 7, 1060, at=(0, 0, 260), direction=(0, 0, 1), op="new")
door.box("skin", 920, 8, 1240, at=(490, 14, 960), op="new")
door.box("stripe", 920, 3, 64, at=(490, 21, 1240), op="new")
door.material("abs", color="#161616")
door.material("abs", bodies=["stripe", "pin"], color="#ff4d00")
