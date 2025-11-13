from timanda.tserie import load_gts
from rm_data import rm_periods, rm_periods_link

fname = 'd1.joblib'

gts = load_gts(fname)

for rmr in rm_periods:
    gts.rm_range(rmr[0], rmr[1])

for rmr in rm_periods_link:
    gts.rm_range(rmr[0], rmr[1])

    # calc tr.osc - clean beat
# gts.math_mts_and_number('multiply', 'comb2_f_avg_counter6', -1, 'mc6')
# gts.math_mts_and_mts('add', 'mc6', 'comb2_f_avg_counter5', 'difc56')

# gts.rm_outlayers('comb2_f_avg_counter5', target=44_587_500.02, maxdiff=0.4)
# gts.rm_outlayers('comb2_f_avg_counter5', target=44_587_500.02, maxdiff=0.04)

# gts.rm_outlayers('difc56', target=0, maxdiff=0.1)



gts.plot(mts_names=[
    'sr1_ml1_atomsL',
    'sr1_ml1_probL',
    'difc56',
    'comb2_f_avg_counter5',
    # 'sr1_ml1_f',
    # 'fc',
    # 'f_ule15',
    # 'rfr',
    # 'fr_ule',
    # 'comb2_f_avg_counter7',
    # 'difc56',
    # 'rfsr',
    # 'fsr',
    # 'ptb3',
])

gts.save(fname)
