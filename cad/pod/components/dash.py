from steve import Component
from params import deck_top, seat_y
from ergo import rally, DASH, DRIVER_Y, WHEEL_FACE, HEEL, add, mul

# Dash frame on the moving floor: a crossbar on three uprights, outboard of each seat and in the
# tunnel, so both footwells stay open. It carries the steering column clamp, the driver's dash
# display, the co-driver's telemetry display, the intercom and the co-driver grab handle.
dash = Component("dash", name="Dash frame")
bx, bz = DASH[0], DASH[2]
span = (seat_y + 300) if rally else 300
posts = ((span - 10, "l"), (0, "c"), (-(span - 10), "r")) if rally else ((span - 10, "l"), (-(span - 10), "r"))
dash.cylinder("crossbar", 25, 2 * span, at=(bx, -span, bz), direction=(0, 1, 0), op="new")
for y, name in posts:
    dash.cylinder("upright_" + name, 22, bz - deck_top, at=(bx, y, deck_top), direction=(0, 0, 1), op="new")
    dash.box("foot_" + name, 110, 90, 10, at=(bx, y, deck_top + 5), op="new")
dash.box("clamp", 80, 70, 70, at=(bx, DRIVER_Y, bz), op="new")

# Driver dash display (7 inch) above the column, facing the driver.
dash.box("dash_display", 24, 180, 110, at=(bx + 40, DRIVER_Y, bz + 120), op="new")
dash.move("dash_display_tilt", ["dash_display"], rotate=(((bx + 40, DRIVER_Y, bz + 120), (0, 1, 0)), -15))

# Toe board ahead of each footwell.
toe_x = HEEL[0] + 290
for name, y in (("toe_d", DRIVER_Y),) + ((("toe_c", -seat_y),) if rally else ()):
    dash.box(name, 12, 420, 260, at=(toe_x, y, deck_top + 130), op="new")

if rally:
    # Co-driver: 10 inch telemetry and coaching display, grab handle, intercom on the tunnel post.
    dash.box("codriver_display", 24, 250, 165, at=(bx + 30, -seat_y, bz + 140), op="new")
    dash.move("codriver_display_tilt", ["codriver_display"],
              rotate=(((bx + 30, -seat_y, bz + 140), (0, 1, 0)), -20))
    dash.cylinder("grab_handle", 14, 260, at=(bx - 40, -seat_y - 130, bz + 40), direction=(0, 1, 0), op="new")
    dash.box("intercom", 120, 90, 50, at=(bx, 0, bz + 55), op="new")
    for name, y in (("jack_d", 30), ("jack_c", -30)):
        dash.cylinder(name, 7, 16, at=(bx - 60, y, bz + 55), direction=(-1, 0, 0), op="new")

dash.material("steel-1c45", finish="powder-coated", color="#24282e")
glass = ["dash_display"] + (["codriver_display"] if rally else [])
dash.material("glass-soda-lime", bodies=glass, color="#123044")
if rally:
    dash.material("abs", bodies=["intercom"], color="#e0b000")
    dash.material("steel-1c45", bodies=["jack_d", "jack_c"], color="#b8bec6")
    dash.material("abs", bodies=["grab_handle"], color="#c1121f")
dash.material("aluminum-6061-t6", bodies=["toe_d"] + (["toe_c"] if rally else []), color="#3a414c")
