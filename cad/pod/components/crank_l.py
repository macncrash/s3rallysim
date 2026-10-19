from steve import Component
import crank_parts

crank_l = Component("crank_l", name="Crank arm, left")
crank_parts.build(crank_l, 1)
