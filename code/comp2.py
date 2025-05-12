# comparator UMK_LO-UMK_RLS

from get_data_sr_link import get_data
import astropy.time as ast

def MJD2UTC(mjd, strfmt='%Y-%m-%d %H:%M:%S'):
    t = ast.Time(mjd, format='mjd')
    return t.strftime(strfmt)

mjd = 60759
date_str = MJD2UTC(mjd, strfmt='%Y-%m-%d')

gts = get_data(
    included_tables={
        "comb2_f_avg_counter7": {'sh_s':0.05, 'tol_s':0},
    },
    days=(mjd, mjd),
    rm_link_err=True,
    rm_sr_err=True,
)

gts.math_mts_and_number('add', 'comb2_f_avg_counter7', 168.5e6, 'comp2p')
gts.math_mts_and_number('multiply', 'comp2p', -1, 'comp2')
gts.math_mts_and_number('multiply', 'comb2_f_avg_counter7', 0, 'zero')
gts.math_mts_and_number('add', 'zero', 1, 'valid')
gts.math_mts_and_number('add', 'zero', 1e-17, 'uncert')

gts.create_comparator_file(
    filename=f'share_files/UMK_LO-UMK_RLS/{date_str}_UMK_LO-UMK_RLS.dat',
    mts_names=['comp2', 'valid', 'uncert'],
    headers=['ΔA→B', 'flag', 'relative systematic uncertainty'],
    formats=['.6f', '.0f', '.4e'],
)