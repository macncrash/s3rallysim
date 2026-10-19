from steve import Component

dog_cap = Component("dog_cap", name="Dog box cap")
dog_cap.box("cap", 58, 86, 8, at=(0, 0, 4))
dog_cap.cylinder("hole_l", 2.8, 12, at=(0, 32, -2), direction=(0, 0, 1), op="cut")
dog_cap.cylinder("hole_r", 2.8, 12, at=(0, -32, -2), direction=(0, 0, 1), op="cut")
# Gate for the stick: it swings fore-aft through the cap.
dog_cap.box("gate", 50, 14, 20, at=(0, 0, 4), op="cut")
dog_cap.material("pa6", color="#24282e")

