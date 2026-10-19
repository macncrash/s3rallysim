from steve import Component
from params import pivot_x, pivot_z

# Heave sleeve on the column, with the lower yoke of the universal joint: two lugs across X that
# carry the roll pin.
heave_car = Component("heave_car", name="Heave sleeve and lower yoke")
z0, z1 = 230, 335
heave_car.box("sleeve", 180, 180, z1 - z0, at=(pivot_x, 0, (z0 + z1) / 2))
heave_car.box("bore", 124, 124, z1 - z0 + 4, at=(pivot_x, 0, (z0 + z1) / 2), op="cut", body="sleeve")
top = pivot_z + 25
for name, dx in (("f", 75), ("b", -75)):
    heave_car.box("lug_" + name, 20, 60, top - z1, at=(pivot_x + dx, 0, (z1 + top) / 2), op="new")
    heave_car.cylinder("lug_" + name + "_bore", 18.5, 30, at=(pivot_x + dx - 15, 0, pivot_z), direction=(1, 0, 0),
                       op="cut", body="lug_" + name)
heave_car.material("steel-s235jr", color="#4a515b")
