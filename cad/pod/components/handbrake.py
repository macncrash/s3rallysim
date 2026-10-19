from steve import Component

handbrake = Component("handbrake", name="Handbrake mount")
handbrake.box("base", 70, 36, 10, at=(0, 0, 5))
handbrake.cylinder("hole_a", 4.3, 14, at=(-20, 0, -2), direction=(0, 0, 1), op="cut")
handbrake.cylinder("hole_b", 4.3, 14, at=(20, 0, -2), direction=(0, 0, 1), op="cut")
handbrake.box("cheek_l", 28, 8, 40, at=(0, 16, 28), op="new")
handbrake.box("cheek_r", 28, 8, 40, at=(0, -16, 28), op="new")
handbrake.cylinder("bore_l", 4.3, 14, at=(0, 10, 40), direction=(0, 1, 0), op="cut", body="cheek_l")
handbrake.cylinder("bore_r", 4.3, 14, at=(0, -24, 40), direction=(0, 1, 0), op="cut", body="cheek_r")
handbrake.material("aluminum-6061-t6", color="#3a414c")

