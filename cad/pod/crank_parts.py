"""Crank arm: hub on the drive shaft, arm along +X to the crank pin, pin out to the link's eye.

side +1 for the left (pin toward +Y, outboard), -1 for the right. Origin on the crank axis in the
arm's plane; the link's bottom eye sits LINK_DY outboard of it.
"""

from params import crank_r

LINK_DY = 30
ARM_T = 30


def build(c, side):
    c.cylinder("hub", 35, ARM_T, at=(0, -ARM_T / 2, 0), direction=(0, 1, 0))
    c.box("arm", crank_r, ARM_T, 45, at=(crank_r / 2, 0, 0), op="new")
    c.cylinder("tip", 22, ARM_T, at=(crank_r, -ARM_T / 2, 0), direction=(0, 1, 0), op="new")
    c.cylinder("pin", 10, LINK_DY + 25, at=(crank_r, side * ARM_T / 2 - side * 2, 0), direction=(0, side, 0),
               op="new")
    c.material("steel-34crnimo6", color="#8d939c")
