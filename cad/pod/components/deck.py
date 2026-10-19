from steve import Component
from params import deck_z

# Moving floor for two seats. The motion stack under it is still the one-seat stack: its sizing
# for the two-occupant payload is the next step.
deck = Component("deck", name="Moving floor")
deck.box("plate", 1440, 1320, 12, at=(70, 0, deck_z), op="new")
deck.box("lightening", 340, 180, 20, at=(0, 0, deck_z), op="cut", body="plate")
for name, x, y in (("fl", 300, 190), ("fr", 300, -190), ("bl", -300, 190), ("br", -300, -190)):
    # Linear bearing housings hang under the floor so the guide posts never come through it.
    deck.cylinder("brg_" + name, 14, 126, at=(x, y, deck_z - 120), direction=(0, 0, 1), op="join", body="plate")
    deck.cylinder(
        "bore_" + name, 8.25, 126, at=(x, y, deck_z - 130), direction=(0, 0, 1), op="cut", body="plate"
    )
deck.material("aluminum-6061-t6", color="#4e565f")
