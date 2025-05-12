# import path to mytools
import sys
sys.path.insert(1, "../../mytools/")

from FAMO_tools import ( 
    fabsSr1_ml1_vs_aos_range,
)
from rm_data import rm_periods

# d = fabsSr1_ml1_vs_aos_range(60752.75, 60752.95)
# d = fabsSr1_ml1_vs_aos_range(60752.6, 60753.34)
d = fabsSr1_ml1_vs_aos_range(60751.0, 60752.0)
for rmp in rm_periods:
    d.rm_range(rmp[0], rmp[1])
# d.rm_outlayers('ft')
# d.rm_outlayers('fsr')
# d.rm_range(60753.285, 60753.305)
# d.rm_outlayers('ft')
# d.rm_range(60753.318, 60753.33)
# d.rm_range(60752.7, 60752.75)
# d.rm_range(60753.0, 60753.025)
# d.rm_range(60753.199, 60753.203)
# d.rm_range(60751.76, 60751.86)

fsr = d.mts_dict['fsr']
# fsr.sew(grid_s=10)
print(f"mean: {fsr.mean()}")
d.plot()
fsr.plot_allan(atom='88Sr', rate=0.1)

