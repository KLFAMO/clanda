from get_data_sr_link import get_data

gts = get_data(
    included_tables={
        "sr1_ml1_f": {'sh_s':0, 'tol_s':5},
        "sr1_ml1_probL": {'sh_s':0, 'tol_s':5},
        # "sr1_ml1_atomsL": {'sh_s':0, 'tol_s':5},
        # "sr1_698_PD_ampl": {'sh_s':0, 'tol_s':5},
        # "comb2_f_avg_counter0": {'sh_s':0.05, 'tol_s':0},
        "comb2_f_avg_counter5": {'sh_s':0.05, 'tol_s':0},
        "comb2_f_avg_counter6": {'sh_s':0.05, 'tol_s':0},
        # "comb2_f_avg_counter7": {'sh_s':0.05, 'tol_s':0},
    },
    # days=(60754, 60756),
    # days=(60761, 60762),
    # days=(60763, 60764),
    # days=(60788, 60791),
    days=(60764, 60765),
    rm_link_err=False,
    rm_sr_err=False,
)

# gts.get_range(60764.902, 60764.918)
# gts.get_range(60755.05, 60755.1)
# gts.get_range(60761.85, 60761.9)
gts.get_range(60764.2275, 60764.245)

# d = gts.mts_dict['sr1_ml1_probL']
# d.hist(bins=100, orientation='horizontal')

gts.plot(mts_names=[
    # 'sr1_ml1_atomsL',
    "sr1_ml1_f",
    'sr1_ml1_probL',
    "comb2_f_avg_counter5",
    # "comb2_f_avg_counter7",
    # "comb2_f_avg_counter6",
    # 'difc56',
    # 'rfsr',
    # # 'rpd',
    # 'fsr',
    # 'sr1_698_PD_ampl',
    # 'cor',
], time_unit='s')