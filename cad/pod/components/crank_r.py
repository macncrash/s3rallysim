from steve import Component
import crank_parts

crank_r = Component("crank_r", name="Crank arm, right")
crank_parts.build(crank_r, -1)
