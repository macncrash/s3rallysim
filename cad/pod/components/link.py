from steve import Component
from params import link_len

# Connecting link: rod-end eyes at both pins, upright at rest. Origin on the bottom pin.
link = Component("link", name="Actuator link")
link.cylinder("eye_lo", 20, 20, at=(0, -10, 0), direction=(0, 1, 0))
link.cylinder("bore_lo", 10.5, 24, at=(0, -12, 0), direction=(0, 1, 0), op="cut", body="eye_lo")
link.cylinder("rod", 13, link_len - 40, at=(0, 0, 20), direction=(0, 0, 1), op="new")
link.cylinder("eye_hi", 20, 20, at=(0, -10, link_len), direction=(0, 1, 0), op="new")
link.cylinder("bore_hi", 10.5, 24, at=(0, -12, link_len), direction=(0, 1, 0), op="cut", body="eye_hi")
link.material("steel-1c45", color="#d5d8de")
