"""Seat rails and lift spacer under one seat, built into a Component in its seat's frame."""

from params import deck_top, seat_travel
from ergo import SEAT_X_REAR, seat_x, seat_z

RAIL_H = 30


def build(c, pct):
    """Rails fixed to the floor along the whole travel; spacer and slider move with the seat."""
    sx = seat_x(pct)
    lift = seat_z(pct) - deck_top - RAIL_H
    rail_len = seat_travel + 420
    rail_x = SEAT_X_REAR + seat_travel / 2 - sx
    for name, y in (("l", 170), ("r", -170)):
        c.box("rail_" + name, rail_len, 34, RAIL_H, at=(rail_x, y, -lift - RAIL_H / 2), op="new")
        c.box("spacer_" + name, 380, 30, lift, at=(0, y, -lift / 2), op="new")
    c.material("aluminum-6061-t6", color="#3a414c")
    c.material("steel-1c45", bodies=["rail_l", "rail_r"], color="#8d939c")
    return sx, seat_z(pct)
