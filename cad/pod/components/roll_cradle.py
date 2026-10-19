from steve import Component
from params import roll_z, pitch_z

roll_cradle = Component("roll_cradle", name="Roll cradle")
roll_cradle.cylinder("shaft", 10, 520, at=(-260, 0, roll_z), direction=(1, 0, 0), op="new")
mid = (roll_z + pitch_z) / 2
for name, y, bore_y in (("l", 150, 128), ("r", -150, -168)):
    roll_cradle.box("lug_" + name, 40, 24, 72, at=(0, y, mid), op="new")
    roll_cradle.cylinder(
        "bore_" + name, 10.3, 40, at=(0, bore_y, pitch_z), direction=(0, 1, 0), op="cut", body="lug_" + name
    )
    roll_cradle.box("web_" + name, 22, 110, 16, at=(0, y / 2, roll_z), op="new")
roll_cradle.box("motor", 150, 46, 46, at=(-40, 210, roll_z), op="new")
roll_cradle.material("steel-1c45", bodies=["shaft"], color="#9aa1ab")
roll_cradle.material("aluminum-6061-t6", color="#3a414c")
roll_cradle.material("aluminum-6061-t6", bodies=["motor"], color="#b7bcc4")

