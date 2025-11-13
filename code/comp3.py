# comparator cavity-sr

# the frequency of the laser inside RLS 50/T should be 194,399,987,408,400 Hz. 
# This figure should be accurate to 100 Hz, because 
# (1) it's measured against out maser, which deviates slightly from the Cs fountain and UTC, and 
# (2) our cavity drifts by some 10 Hz per day. 

import sys
sys.path.insert(1, "../mytools/")

from get_data_sr_link import get_data
import astropy.time as ast
from famo_config import fth698_Sr88

def MJD2UTC(mjd, strfmt='%Y-%m-%d %H:%M:%S'):
    t = ast.Time(mjd, format='mjd')
    return t.strftime(strfmt)

mjd = 60764
date_str = MJD2UTC(mjd, strfmt='%Y-%m-%d')

# gts = get_data(
#     included_tables={
#         "sr1_ml1_f": {'sh_s':0, 'tol_s':5},
#         "comb2_f_avg_counter5": {'sh_s':0.05, 'tol_s':0},
#         "comb2_f_avg_counter6": {'sh_s':0.05, 'tol_s':0},
#     },
#     days=(mjd, mjd),
#     rm_link_err=True,
#     rm_sr_err=True,
# )



ptb_freq = 194_399_987_408_400 
nc_rls = 168.5e6
gts.math_mts_and_number('multiply', 'comb2_f_avg_counter5', 0, 'zero')
gts.math_mts_and_number('add', 'zero', ptb_freq+nc_rls, 'f_ule15')
N15 = 777_621
gts.math_mts_and_number('divide', 'f_ule15', N15, 'fr')
gts.math_mts_and_number('multiply', 'sr1_ml1_f', -4, 'fc')
N = 1_716_959.
gts.math_mts_and_number('multiply', 'fr', N, 'ft1')  # <----
gts.math_mts_and_number('add', 'ft1', 0, 'ft')
gts.math_mts_and_mts('add', 'fc', 'comb2_f_avg_counter5', 'ftmp')
gts.add_mts_to_mts('ftmp', 'ft', 'fsrnc')
gts.add_mts_to_mts('fsrnc', 'cor', 'fsrc')
gts.math_mts_and_number('divide', 'fsrc', ptb_freq+nc_rls, 'ratio')

gts.math_mts_and_number('add', 'zero', 1, 'valid')
gts.math_mts_and_number('add', 'zero', 1e-15, 'uncert')

# gts.plot(mts_names=[
#     'fsrc',
#     'ratio',
# ])

# gts.create_comparator_file(
#     filename=f'share_files/UMK_LO-UMK_Sr1/{date_str}_UMK_LO-UMK_Sr1.dat',
#     mts_names=['ratio', 'valid', 'uncert'],
#     headers=['ΔA→B', 'flag', 'relative systematic uncertainty'],
#     formats=['.16f', '.0f', '.4e'],
# )