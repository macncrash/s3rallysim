from steve import Component
from params import roll_z

sled = Component("sled", name="Surge sled")
sled.box("plate", 680, 480, 10, at=(20, 0, 72), op="new")
for name, x, y in (("fl", 200, 210), ("bl", -160, 210), ("fr", 200, -210), ("br", -160, -210)):
    sled.box("car_" + name, 56, 30, 12, at=(x, y, 60.5), op="new")
for name, x in (("f", 240), ("b", -200)):
    sled.box("pill_" + name, 56, 44, 62, at=(x, 0, 108), op="new")
    sled.cylinder(
        "bore_" + name, 10.3, 70, at=(x - 35, 0, roll_z), direction=(1, 0, 0), op="cut", body="pill_" + name
    )
sled.box("tab", 12, 80, 14, at=(-78, -270, 58), op="new")
sled.material("aluminum-6061-t6", color="#3d4450")
sled.material("aluminum-6061-t6", bodies=["pill_f", "pill_b"], color="#6a717c")

