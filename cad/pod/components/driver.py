from steve import Component
from params import driver_pct
import mannequin

driver = Component("driver", name="Driver in race gear")
mannequin.build(driver, driver_pct, "driver", "#c1121f")
