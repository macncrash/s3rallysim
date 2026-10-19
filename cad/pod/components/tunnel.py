from steve import Component

tunnel = Component("tunnel", name="Control template")
# Origin is the dog-box bolt-pattern centre. The plate runs forward to the button box
# and back to the handbrake.
tunnel.box("plate", 460, 116, 12, at=(-20, 0, 6))
for index, (x, y) in enumerate(((-40, -30), (-40, 30), (40, -30), (40, 30))):
    tunnel.cylinder("shift_" + str(index), 3.3, 16, at=(x, y, -2), direction=(0, 0, 1), op="cut")
for index, x in enumerate((-210, -170)):
    tunnel.cylinder("brake_" + str(index), 4.3, 16, at=(x, 0, -2), direction=(0, 0, 1), op="cut")
tunnel.material("aluminum-6061-t6", color="#3c434c")

