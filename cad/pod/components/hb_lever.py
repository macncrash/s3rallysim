from steve import Component

hb_lever = Component("hb_lever", name="Handbrake lever")
hb_lever.box("arm", 22, 8, 230, at=(0, 0, 120))
hb_lever.cylinder("bore", 4.2, 14, at=(0, -7, 16), direction=(0, 1, 0), op="cut")
hb_lever.cylinder("grip", 14, 28, at=(0, -14, 250), direction=(0, 1, 0), op="new")
hb_lever.material("pa6", color="#1e2228")
hb_lever.material("abs", bodies=["grip"], color="#ff4d00")

