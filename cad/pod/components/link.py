from steve import Component
from params import link_len
from bought import LINK_ROD_END

# Connecting link with an SKF SIKB 20 F maintenance-free rod end at each pin (bought.py). Upright at
# rest; origin on the bottom pin.
link = Component("link", name="Actuator link")
R = LINK_ROD_END["eye_diameter_mm"] / 2
W = LINK_ROD_END["eye_width_mm"]
BORE = LINK_ROD_END["bore_mm"] / 2 + 0.5
link.cylinder("eye_lo", R, W, at=(0, -W / 2, 0), direction=(0, 1, 0))
link.cylinder("bore_lo", BORE, W + 4, at=(0, -W / 2 - 2, 0), direction=(0, 1, 0), op="cut", body="eye_lo")
link.cylinder("rod", 13, link_len - 2 * R, at=(0, 0, R), direction=(0, 0, 1), op="new")
link.cylinder("eye_hi", R, W, at=(0, -W / 2, link_len), direction=(0, 1, 0), op="new")
link.cylinder("bore_hi", BORE, W + 4, at=(0, -W / 2 - 2, link_len), direction=(0, 1, 0), op="cut", body="eye_hi")
link.material("steel-1c45", color="#d5d8de")
