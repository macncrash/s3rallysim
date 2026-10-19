from steve import Component
from params import codriver_pct
import mannequin

codriver = Component("codriver", name="Co-driver in race gear")
mannequin.build(codriver, codriver_pct, "codriver", "#1d4f91")
