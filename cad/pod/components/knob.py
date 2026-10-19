from steve import Component

knob = Component("knob", name="Shifter knob")
knob.cylinder("grip", 18, 40, at=(0, 0, 0), direction=(0, 0, 1))
knob.material("abs", color="#ff4d00")

