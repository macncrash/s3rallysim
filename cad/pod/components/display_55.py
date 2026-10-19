from steve import Component

# 55 inch windscreen display (1210 x 680 mm image). The image is rendered for the driver's eye
# with an off-axis frustum; the co-driver sees the same picture from the side, like a real screen.
display_55 = Component("display_55", name="55 inch windscreen display")
display_55.box("housing", 40, 1240, 715, at=(0, 0, 0))
display_55.box("glass", 3, 1210, 680, at=(21, 0, 0), op="new")
display_55.material("abs", color="#0c0c0c")
display_55.material("glass-soda-lime", bodies=["glass"], color="#123044")
