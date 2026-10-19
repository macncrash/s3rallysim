from steve import Component

body_z = Component("body_z", name="Vertical actuator body")
body_z.box("body", 48, 48, 140, at=(0, 0, 70))
body_z.cylinder("bore", 10, 160, at=(0, 0, -10), direction=(0, 0, 1), op="cut")
body_z.material("aluminum-6061-t6", color="#c5cad1")

