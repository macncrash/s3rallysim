from steve import Component

rod_z = Component("rod_z", name="Actuator rod")
rod_z.cylinder("shaft", 8, 146, at=(0, 0, 0), direction=(0, 0, 1))
rod_z.cylinder("eye", 11, 16, at=(0, -8, 140), direction=(0, 1, 0), op="join")
rod_z.material("steel-1c45", color="#d5d8de")

