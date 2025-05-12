# import path to mytools
import sys
# sys.path.insert(1, "../../mytools/")
sys.path.insert(1, "../mytools/")

from rm_data import rm_periods
# from ml_data import mlb as m
from ml_data import ml698 as m
from get_data_sr_link import get_data



gts = get_data(
    included_tables={
        "sr1_ml1_f": {'sh_s':0, 'tol_s':5},
        "sr1_ml1_probL": {'sh_s':0, 'tol_s':5},
        "sr1_ml1_atomsL": {'sh_s':0, 'tol_s':5},
        "sr1_ml2_f": {'sh_s':0, 'tol_s':5},
        "sr1_ml2_probL": {'sh_s':0, 'tol_s':5},
        "sr1_ml2_atomsL": {'sh_s':0, 'tol_s':5},
    },
    days=(60751, 60756),
    rm_ml_err=True,
    mjd_range=m[2]['range'],
)

gts.math_mts_and_number('multiply', 'sr1_ml1_f', -1, 'mml1_f')
gts.math_mts_and_mts('add', 'mml1_f', 'sr1_ml2_f', 'diff')

gts.plot(mts_names=[
    'diff',
    'sr1_ml1_f', 
    'sr1_ml2_f', 
    'sr1_ml1_probL', 
    'sr1_ml2_probL',
    'sr1_ml1_atomsL', 
    'sr1_ml2_atomsL',
])

gts.mts_dict['diff'].plot_allan(atom='88Sr', rate=1, allan_method='adev')
print(-gts.mts_dict['diff'].mean()*4)