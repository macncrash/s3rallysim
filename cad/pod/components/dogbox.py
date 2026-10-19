from steve import Component

dogbox = Component("dogbox", name="Dog box housing")
dogbox.box("base", 108, 88, 8, at=(0, 0, 4))
for index, (x, y) in enumerate(((-40, -30), (-40, 30), (40, -30), (40, 30))):
    dogbox.cylinder("bolt_" + str(index), 3.3, 14, at=(x, y, -2), direction=(0, 0, 1), op="cut")
dogbox.box("cheek_l", 58, 10, 72, at=(0, 32, 44), op="new")
dogbox.box("cheek_r", 58, 10, 72, at=(0, -32, 44), op="new")
# 608 bearing seat, open through the top so the bearing drops in. Cap bolts on after.
# Cradle centre is 11 mm below the cheek top so a 608 sits flush under the cap.
dogbox.cylinder("cradle_l", 11.15, 18, at=(0, 22, 69), direction=(0, 1, 0), op="cut", body="cheek_l")
dogbox.box("slot_l", 24, 16, 40, at=(0, 32, 89), op="cut", body="cheek_l")
dogbox.cylinder("cradle_r", 11.15, 18, at=(0, -40, 69), direction=(0, 1, 0), op="cut", body="cheek_r")
dogbox.box("slot_r", 24, 16, 40, at=(0, -32, 89), op="cut", body="cheek_r")
dogbox.cylinder("brg_l", 11, 7, at=(0, 28.5, 69), direction=(0, 1, 0), op="new")
dogbox.cylinder("brg_l_bore", 4.2, 12, at=(0, 26, 69), direction=(0, 1, 0), op="cut", body="brg_l")
dogbox.cylinder("brg_r", 11, 7, at=(0, -35.5, 69), direction=(0, 1, 0), op="new")
dogbox.cylinder("brg_r_bore", 4.2, 12, at=(0, -38, 69), direction=(0, 1, 0), op="cut", body="brg_r")
dogbox.box("sw_f", 12, 8, 16, at=(30, 0, 20), op="new")
dogbox.box("sw_b", 12, 8, 16, at=(-30, 0, 20), op="new")
dogbox.material("pa6", color="#24282e")
dogbox.material("steel-1c45", bodies=["brg_l", "brg_r"], color="#b8bec6")
dogbox.material("abs", bodies=["sw_f", "sw_b"], color="#e6e6e6")

