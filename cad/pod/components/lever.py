from steve import Component

lever = Component("lever", name="Dog box lever")
lever.cylinder("pivot", 4, 78, at=(0, -39, 0), direction=(0, 1, 0), op="new")
lever.cylinder("stick", 5, 200, at=(0, 0, 6), direction=(0, 0, 1), op="new")
lever.box("paddle", 28, 10, 8, at=(0, 0, -49), op="new")
lever.material("steel-1c45", color="#cfd3d8")

