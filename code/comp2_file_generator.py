# comparator UMK_LO-UMK_RLS

from timanda.tserie import load_gts
import astropy.time as ast

def MJD2UTC(mjd, strfmt='%Y-%m-%d %H:%M:%S'):
    t = ast.Time(mjd, format='mjd')
    return t.strftime(strfmt)

fname = 'd1.joblib'

mjd = 60760
date_str = MJD2UTC(mjd, strfmt='%Y-%m-%d')

gts = load_gts(fname)
# gts.get_range(60760, 60765)  # get data for a single day
gts.get_range(mjd, mjd+1) 

gts.math_mts_and_number('add', 'comb2_f_avg_counter7', 168.5e6, 'comp2')
# gts.math_mts_and_number('multiply', 'comp2p', -1, 'comp2')
gts.math_mts_and_number('multiply', 'comb2_f_avg_counter7', 0, 'zero')
gts.math_mts_and_number('add', 'zero', 1, 'valid')
gts.math_mts_and_number('add', 'zero', 1e-17, 'uncert')

gts.plot(mts_names=[
    'comb2_f_avg_counter7',
    'comp2',
])

gts.create_comparator_file(
    filename=f'../share_files/UMK_LO-UMK_RLS/{date_str}_UMK_LO-UMK_RLS.dat',
    mts_names=['comp2', 'valid', 'uncert'],
    headers=['A->B', 'flag', 'relative systematic uncertainty'],
    formats=['.6f', '.0f', '.4e'],
)