from steve import Component
from params import pitch_z, post_z0, post_h

pitch_cradle = Component("pitch_cradle", name="Pitch cradle")
pitch_cradle.cylinder("shaft", 10, 400, at=(0, -200, pitch_z), direction=(0, 1, 0), op="new")
pitch_cradle.box("beam_l", 500, 24, 24, at=(0, 150, 214), op="new")
pitch_cradle.box("beam_r", 500, 24, 24, at=(0, -150, 214), op="new")
pitch_cradle.box("beam_f", 24, 276, 24, at=(274, 0, 214), op="new")
pitch_cradle.box("beam_b", 24, 276, 24, at=(-274, 0, 214), op="new")
for name, x, y in (("fl", 300, 190), ("fr", 300, -190), ("bl", -300, 190), ("br", -300, -190)):
    pitch_cradle.cylinder("post_" + name, 8, post_h, at=(x, y, post_z0), direction=(0, 0, 1), op="new")
pitch_cradle.box("motor", 46, 150, 46, at=(230, 0, pitch_z), op="new")
pitch_cradle.material("steel-1c45", bodies=["shaft", "post_fl", "post_fr", "post_bl", "post_br"], color="#9aa1ab")
pitch_cradle.material("aluminum-6061-t6", color="#3a414c")
pitch_cradle.material("aluminum-6061-t6", bodies=["motor"], color="#b7bcc4")

