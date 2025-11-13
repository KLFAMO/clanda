# comparator cavity-sr

# the frequency of the laser inside RLS 50/T should be 194,399,987,408,400 Hz. 
# This figure should be accurate to 100 Hz, because 
# (1) it's measured against out maser, which deviates slightly from the Cs fountain and UTC, and 
# (2) our cavity drifts by some 10 Hz per day. 

from timanda.tserie import load_gts
import astropy.time as ast

def MJD2UTC(mjd, strfmt='%Y-%m-%d %H:%M:%S'):
    t = ast.Time(mjd, format='mjd')
    return t.strftime(strfmt)

fname = 'd1.joblib'

mjd = 60764
date_str = MJD2UTC(mjd, strfmt='%Y-%m-%d')

gts = load_gts(fname)
# gts.get_range(60760, 60765)  # get data for a single day
gts.get_range(mjd, mjd+1) 


fth_Sr88 = 429_228_066_418_007.0 # theoretical frequency of clock transition (den) (A)
fth_lo = 194.4e12  # theoretical frequency of the LO laser after NC AOM  (num) (B)
ptb_freq = 194_399_987_408_400 
nc_rls = 168.5e6

gts.math_mts_and_number('multiply', 'comb2_f_avg_counter5', 0, 'zero')  # zero mts

gts.math_mts_and_number('multiply', 'sr1_ml1_f', 4, 'fc_aom') # atoms correction
gts.math_mts_and_number('multiply', 'cor', 1, 'mcor')  # total shift 698
gts.math_mts_and_mts('add', 'fc_aom', 'mcor', 'mfc')  # atoms correction + total shift
gts.math_mts_and_number('add', 'zero', fth_Sr88, 'fth88')  # theoretical frequency of the 698 Sr clock
gts.math_mts_and_mts('add', 'fth88', 'mfc', 'fcav698')  # frequency of the 698 cavity
gts.math_mts_and_number('add', 'fcav698', 84e6, 'fcomb698') # frequency of the 698 laser going to the comb
gts.math_mts_and_number('multiply', 'comb2_f_avg_counter5', -1, 'mbeat698')  # beat of the 698 laser with the comb (minus sign)
gts.math_mts_and_mts('add', 'fcomb698', 'mbeat698', 'fN698')  # frequency of the 698 laser after the comb

N698 = 1_716_959.0
gts.math_mts_and_number('add', 'fN698', -70e6, 'tmp1')  # frequency between N=1 and N698
gts.math_mts_and_number('divide', 'tmp1', N698, 'fr')  # f_rep

# comparison with the AOS
gts.math_mts_and_number('add', 'comb2_f_avg_counter0', 980e6, 'fraostmp')
gts.math_mts_and_number('divide', 'fraostmp', 4, 'fr_aos')  # frequency measured by the AOS
gts.math_mts_and_number('multiply', 'fr', -1, 'mfr')  # negative fr
gts.math_mts_and_mts('add', 'mfr', 'fr_aos', 'diffr')  # diffr = fr - fr_aos
gts.math_mts_and_number('divide', 'diffr', 250e6, 'diffr_rel')  # diffr relative AOS vs Sr88
gts.append_mtserie(
    mts_name='avg',
    mts=gts.mts_dict['diffr_rel'].resample(period_s=600)
)

# calculate 1542 cavity frequency
N1542 = 777_621.0
gts.math_mts_and_number('multiply', 'fr', N1542, 'tmp2') # frequency between N=1 and N1542
gts.math_mts_and_number('add', 'tmp2', 70e6+35e6, 'f1542')  # frequency of the 1542 cavity

# calculate comparator
gts.math_mts_and_number('add', 'f1542', -fth_lo, 'DAB')

# gts.math_mts_and_number('add', 'comb2_f_avg_counter7', nc_rls+ptb_freq-70e6+14e6, 'f_ule15') # <--- added 14 MHz
# N15 = 777_621
# gts.math_mts_and_number('divide', 'f_ule15', N15, 'fr') # f_rep

# N = 1_716_959
# gts.math_mts_and_number('multiply', 'fr', N, 'ft1')



# gts.math_mts_and_number('add', 'zero', ptb_freq+nc_rls, 'f_ule15')

# gts.math_mts_and_number('add', 'ft1', 0, 'ft')
# gts.math_mts_and_mts('add', 'fc', 'comb2_f_avg_counter5', 'ftmp')
# gts.add_mts_to_mts('ftmp', 'ft', 'fsrnc')
# gts.add_mts_to_mts('fsrnc', 'cor', 'fsrc')
# gts.math_mts_and_number('divide', 'fsrc', ptb_freq+nc_rls, 'ratio')

## additional columns
gts.math_mts_and_number('add', 'zero', 1, 'valid')
gts.math_mts_and_number('add', 'zero', 1e-15, 'uncert')


gts.plot(mts_names=[
    'f1542',
    'DAB',
    'diffr_rel',
    'avg',
])


gts.create_comparator_file(
    filename=f'../share_files/UMK_LO-UMK_Sr1/{date_str}_UMK_LO-UMK_Sr1.dat',
    mts_names=['DAB', 'valid', 'uncert'],
    # headers=['ΔA→B', 'flag', 'relative systematic uncertainty'],
    headers=['A->B', 'flag', 'relative systematic uncertainty'],
    formats=['.6f', '.0f', '.4e'],
)