from timanda.tserie import TSerie, MTSerie, GTserie, load_gts
from rm_data import rm_periods, rm_periods_link, rm_periods_ml

# Correction data for the 698 Sr clock
# cor = [
#     [60751, 263.798],
#     [60753, 263.798],
#     [60753.9426, 99.078],
#     [60754., 99.078],
#     [60755, 99.078],
#     [60763.9, 99.078-1.2],
#     [60764.5749, 44.566],
#     [60765.45, 44.566],
#     [60766, 44.566],
#     [60788, 360],   # roughly
#     [60788.79, 44],  # roughly
#     [60790.79, 44],  # roughly
# ]

# cor_mjd = [x[0] for x in cor]
# cor_val = [x[1] for x in cor]

# cor_val = [x + 21.72 for x in cor_val]  # to get the same offset as in the data files

def get_data(
        included_tables, days=(60751, 60765),
        rm_link_err=False, rm_sr_err=False, rm_ml_err=False,
        mjd_range=None
    ):

    if mjd_range is not None:
        days = (int(mjd_range[0]), int(mjd_range[1])+1)
    print("Days:", days)

    days_range = days[1] - days[0] + 1

    # cor_ts =  TSerie(mjd=cor_mjd, val=cor_val)
    # cor = MTSerie(TSerie=cor_ts)
    # cor, mask = cor.resample2(
    #     period_s=1, sh_s=0, tol_s=24*60*60,
    #     start_mjd=days[0],
    #     stop_mjd=days[0]+days_range,
    # )
    gtsc = load_gts('d_cor.joblib')
    cor = gtsc.mts_dict['sh_total']
    print('cor get range ...')
    cor.getrange(days[0], days[0]+days_range)
    print('done')

    # create grid of all data
    gts = GTserie("d")
    common_rm_mask = None
    for table in included_tables:
        # TODO: this import and resampling should be done once and saved to pickle file
        d = MTSerie()
        # import data from files for all days for the given table
        for day in range(days[0], days[1]+1):
            d.add_mjdf_from_datfile(f'../data_files/export_{day}/{table}.csv', delimiter=',', skiprows=1)
        # resample data to 1 second period
        d, rm_mask = d.resample2(
            period_s=1, sh_s=included_tables[table]['sh_s'],
            tol_s=included_tables[table]['tol_s'],
            start_mjd=days[0],
            stop_mjd=days[0]+days_range
        )
        common_rm_mask = common_rm_mask | rm_mask if common_rm_mask is not None else rm_mask
        gts.append_mtserie(mts_name=table, mts=d)

    # # add ptb data ------
    # d = MTSerie()
    # for day in range(days[0], days[1]+1):
    #     d.add_mjdf_from_datfile(f'data_files/export_{day}/ptb.dat', delimiter='\t', skiprows=3)
    # d, rm_mask = d.resample2(
    #     period_s=1, sh_s=0.05,
    #     tol_s=0,
    #     start_mjd=days[0],
    #     stop_mjd=days[0]+days_range
    # )
    # common_rm_mask = common_rm_mask | rm_mask if common_rm_mask is not None else rm_mask
    # gts.append_mtserie(mts_name='ptb', mts=d)
    # # -------------------
    
    # add correction data for the 698 Sr clock ------
    cor, rm_mask = cor.resample2(
        period_s=1, sh_s=0,
        tol_s=5,
        start_mjd=days[0],
        stop_mjd=days[0]+days_range
    )
    common_rm_mask = common_rm_mask | rm_mask if common_rm_mask is not None else rm_mask
    gts.append_mtserie(mts_name='cor', mts=cor)

    # -------------------------------------------

    # allign gaps ------------------------
    print("Allign gaps ...")
    for table in included_tables:
        gts.mts_dict[table].rm_indexes([common_rm_mask])
    print("Done")
    
    
    gts.mts_dict['cor'].rm_indexes([common_rm_mask])
    # # gts.mts_dict['ptb'].rm_indexes([common_rm_mask])
    # -------------------------------------------

    print("Get gts range ...")
    if mjd_range is not None:
        gts.get_range(mjd_range[0], mjd_range[1])
    print("Done")

    print("Rm sr errors ...")
    if rm_sr_err:
        for rmr in rm_periods:
            gts.rm_range(rmr[0], rmr[1])
    print("Done")

    if rm_link_err:
        for rmr in rm_periods_link:
            gts.rm_range(rmr[0], rmr[1])

    if rm_ml_err:
        for rmr in rm_periods_ml:
            gts.rm_range(rmr[0], rmr[1])

    return gts

if __name__ == "__main__":
    gts = get_data(
        included_tables={
            "sr1_ml1_f": {'sh_s':0, 'tol_s':5},
            "sr1_ml1_probL": {'sh_s':0, 'tol_s':5},
            "sr1_ml1_atomsL": {'sh_s':0, 'tol_s':5},
            "sr1_698_PD_ampl": {'sh_s':0, 'tol_s':5},
            "comb2_f_avg_counter0": {'sh_s':0.05, 'tol_s':0},
            "comb2_f_avg_counter5": {'sh_s':0.05, 'tol_s':0},
            "comb2_f_avg_counter6": {'sh_s':0.05, 'tol_s':0},
            "comb2_f_avg_counter7": {'sh_s':0.05, 'tol_s':0},
        },
        # days=(60760, 60765),
        # days=(60760, 60765),
        days=(60787, 60795),
        rm_link_err=True,
        rm_sr_err=True,
    )   
    gts.plot(mts_names=[
        'sr1_ml1_atomsL',
        'sr1_ml1_probL',
        'sr1_ml1_f',
        'cor',
    ])
    gts.save('d2.joblib')

