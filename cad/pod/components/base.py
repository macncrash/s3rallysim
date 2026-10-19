from steve import Component

base = Component("base", name="Motion base")


def tube(cid, length, width, height, at):
    base.box(cid, length, width, height, at=at, op="new")
    if length >= width and length >= height:
        void = (length + 4, max(width - 12, 8), max(height - 12, 8))
    elif width >= length and width >= height:
        void = (max(length - 12, 8), width + 4, max(height - 12, 8))
    else:
        void = (max(length - 12, 8), max(width - 12, 8), height + 4)
    base.box(cid + "_void", void[0], void[1], void[2], at=at, op="cut", body=cid)


tube("extr_l", 900, 40, 40, (20, 210, 20))
tube("extr_r", 900, 40, 40, (20, -210, 20))
tube("extr_b", 40, 380, 40, (-400, 0, 20))
tube("extr_f", 40, 380, 40, (440, 0, 20))
# MGN15-size rails. The cylinder axis is the surge joint.
base.cylinder("rail_l", 7, 760, at=(-360, 210, 47), direction=(1, 0, 0), op="new")
base.cylinder("rail_r", 7, 760, at=(-360, -210, 47), direction=(1, 0, 0), op="new")
base.box("stop_f", 14, 36, 18, at=(412, 210, 63), op="new")
base.box("stop_b", 14, 36, 18, at=(-372, 210, 63), op="new")
base.material("aluminum-6061-t6", finish="powder-coated", color="#2c3138")
base.material("steel-1c45", bodies=["rail_l", "rail_r"], color="#8d939c")
base.material("abs", bodies=["stop_f", "stop_b"], color="#c45500")

