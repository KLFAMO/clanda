# import path to mytools
import sys
# sys.path.insert(1, "../../mytools/")
sys.path.insert(1, "../mytools/")

# from FAMO_tools import fabsSr1_ml1_vs_aos_range
from famo_config import fth698_Sr88
from rm_data import rm_periods
from get_data_from_files import gts


gts.math_mts_and_number('add', 'comb2_f_avg_counter0', 980e6, 'frtmp')
gts.math_mts_and_number('divide', 'frtmp', 4, 'fr')
gts.math_mts_and_number('multiply', 'sr1_ml1_f', -4, 'fc')
N = 1_716_959.
gts.math_mts_and_number('multiply', 'fr', N, 'ft1')
gts.math_mts_and_number('add', 'ft1', -14e6-fth698_Sr88, 'ft')
gts.math_mts_and_mts('add', 'fc', 'comb2_f_avg_counter5', 'ftmp')
gts.add_mts_to_mts('ftmp', 'ft', 'fsr')
# calc tr.osc - clean beat
gts.math_mts_and_number('multiply', 'comb2_f_avg_counter6', -1, 'mc6')
gts.math_mts_and_mts('add', 'mc6', 'comb2_f_avg_counter5', 'difc56')

gts.rm_outlayers('sr1_ml1_atomsL', target=5700, maxdiff=2200)
# gts.rm_outlayers('fsr')
# gts.rm_outlayers('fsr')
# gts.rm_outlayers('fsr')
gts.rm_outlayers('difc56', target=0, maxdiff=0.02)
gts.append_mtserie(
    mts_name='rfsr',
    mts=gts.mts_dict['fsr'].resample(period_s=300)
)

# gts.rm_range(60751.98, 60754.05)
# gts.rm_range(60754.28, 60755.88)

gts.plot(mts_names=[
    'sr1_ml1_atomsL',
    'sr1_ml1_probL',
    # 'wm_813_f',
    'fc',
    'fsr',
    'difc56',
    'rfsr'
])
gts.mts_dict['fsr'].plot_allan(atom='88Sr', rate=1, allan_method='adev')

# gts.mts_dict['fsr'].resample(period_s=600).plot()