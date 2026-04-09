# import path to mytools
# import sys
# sys.path.insert(1, "../../mytools/")
# # sys.path.insert(1, "../mytools/")

# from FAMO_tools import fabsSr1_ml1_vs_aos_range
from famo_config import fth698_Sr88
from rm_data import rm_periods
from get_data_sr_link import get_data

gts = get_data(
    included_tables={
        "sr1_ml1_f": {'sh_s':0, 'tol_s':5},
        "sr1_ml1_probL": {'sh_s':0, 'tol_s':5},
        "sr1_ml1_atomsL": {'sh_s':0, 'tol_s':5},
        "sr1_698_PD_ampl": {'sh_s':0, 'tol_s':5},
        "comb2_f_avg_counter0": {'sh_s':0.05, 'tol_s':0},
        "comb2_f_avg_counter5": {'sh_s':0.05, 'tol_s':0},
        "comb2_f_avg_counter6": {'sh_s':0.05, 'tol_s':0},
    },
    days=(60761, 60762),
    rm_link_err=False,
    rm_sr_err=True,
)

ptb_freq = 194_399_987_408_400 
nc_rls = 168.5e6

gts.math_mts_and_number('add', 'comb2_f_avg_counter0', 980e6, 'frtmp')
gts.math_mts_and_number('divide', 'frtmp', 4, 'fr')
gts.math_mts_and_number('multiply', 'sr1_ml1_f', -4, 'fc')
N = 1_716_959.
gts.math_mts_and_number('multiply', 'fr', N, 'ft1')  # <----
gts.math_mts_and_number('add', 'ft1', -14e6-fth698_Sr88, 'ft')
gts.math_mts_and_mts('add', 'fc', 'comb2_f_avg_counter5', 'ftmp')
gts.add_mts_to_mts('ftmp', 'ft', 'fsrnc')
gts.add_mts_to_mts('fsrnc', 'cor', 'fsr')
# calc tr.osc - clean beat
gts.math_mts_and_number('multiply', 'comb2_f_avg_counter6', -1, 'mc6')
gts.math_mts_and_mts('add', 'mc6', 'comb2_f_avg_counter5', 'difc56')

# gts.rm_outlayers('sr1_ml1_atomsL', target=6000, maxdiff=2300)
gts.rm_outlayers('difc56', target=0, maxdiff=0.02)
gts.rm_outlayers('sr1_ml1_probL', target=0, maxdiff=2)

# gts.mts_dict['fsr'].rm_drift()
# gts.rm_outlayers('fsr')
gts.append_mtserie(
    mts_name='rfsr',
    mts=gts.mts_dict['fsr'].resample(period_s=600)
)
gts.append_mtserie(
    mts_name='rpd',
    mts=gts.mts_dict['sr1_698_PD_ampl'].resample(period_s=600)
)

# gts.append_mtserie(
#     mts_name='rfr',
#     mts=gts.mts_dict['fr'].resample(period_s=600)
# )

gts.plot(mts_names=[
    'sr1_ml1_atomsL',
    'sr1_ml1_probL',
    'difc56',
    'rfsr',
    'rpd',
    'fsr',
    # 'sr1_698_PD_ampl',
    # 'cor',
])
# gts.mts_dict['fsr'].rm_drift()
# gts.mts_dict['rfsr'].rm_drift()
# gts.mts_dict['rfsr'].plot()
gts.mts_dict['fsr'].plot_allan(atom='88Sr', rate=1, allan_method='adev')
# print(gts.mts_dict['fsr'].mean())
