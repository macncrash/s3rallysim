from steve import Component

button_box = Component("button_box", name="Rally button box")
button_box.box("shell", 96, 62, 26, at=(0, 0, 13))
spots = ((-26, -14), (0, -14), (26, -14), (-26, 14), (0, 14), (26, 14))
for index, (x, y) in enumerate(spots):
    button_box.cylinder("btn_" + str(index), 7, 8, at=(x, y, 26), direction=(0, 0, 1), op="new")
button_box.material("abs", color="#1a1a1a")
button_box.material("abs", bodies=["btn_0", "btn_3"], color="#ff4d00")
button_box.material("abs", bodies=["btn_1", "btn_2", "btn_4", "btn_5"], color="#d0d0d0")

