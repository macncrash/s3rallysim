"""S3 Rally Pod centre post as one solid, for STEVE structural studies.

The heave column (sled.py), the heave sleeve and its lower universal-joint yoke (heave_car.py), at the
heave given below, with the sleeve bonded to the column over their engagement (the sleeve's 2 mm
running clearance is closed, as a bushing or bearing pads would close it). The numbers are copied from
the pod design's parameter and motion files (main revision 6): change them there first, then here.

Idealisations: one material for all of it (S235JR, the weaker of the column's 1C45 and the sleeve's
S235JR); the column is held at its foot, where it bolts to the surge carriage's column plate.
"""

from steve import Model

heave = 40  # mm sleeve position: +40 is the top stop, the shortest engagement
pivot_x = -300  # mm universal joint
pivot_z = 430  # mm universal joint centre at rest
column_w = 120  # mm square column
column_z0 = 168  # mm column foot (carriage top plus its 12 mm column plate)
column_z1 = 360  # mm column top
sleeve_w = 180  # mm sleeve outside

model = Model()
pz = pivot_z + heave
z0, z1 = pz - 150, pz - 45
model.box("column", column_w, column_w, column_z1 - column_z0, at=(pivot_x, 0, (column_z0 + column_z1) / 2))
model.box("sleeve", sleeve_w, sleeve_w, z1 - z0, at=(pivot_x, 0, (z0 + z1) / 2), op="new")
# Bored through at the column's size, so joining the column bonds them over the engagement only.
model.box("bore", column_w, column_w, z1 - z0 + 2, at=(pivot_x, 0, (z0 + z1) / 2), op="cut", body="sleeve")
top = pz + 25
lugs = []
for name, dx in (("f", 75), ("b", -75)):
    model.box("lug_" + name, 20, 60, top - z1, at=(pivot_x + dx, 0, (z1 + top) / 2), op="new")
    model.cylinder("lug_" + name + "_bore", 18.5, 30, at=(pivot_x + dx - 15, 0, pz), direction=(1, 0, 0), op="cut",
                   body="lug_" + name)
    lugs.append("lug_" + name)
model.combine("weld", "column", ["sleeve"] + lugs)
model.material("steel-s235jr", color="#4a515b")
result = model.result()
