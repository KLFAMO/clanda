from timanda.mtserie import MTSerie
from timanda.tserie import TSerie
from timanda.gtserie import GTserie
from rm_data import rm_periods, rm_periods_link, rm_periods_ml

# Correction data for the 698 Sr clock
cor = [
    [60751, 263.798],
    [60753, 263.798],
    [60753.9426, 99.078],
    [60754., 99.078],
    [60755, 99.078],
    [60763.9, 99.078-1.2],
    [60764.5749, 44.566],
    [60765.45, 44.566],
    [60766, 44.566],
    [60788, 360],   # roughly
    [60788.79, 44],  # roughly
    [60790.79, 44],  # roughly
]

cor_mjd = [x[0] for x in cor]
cor_val = [x[1] for x in cor]

cor_val = [x + 21.72 for x in cor_val]  # to get the same offset as in the data files

def get_data(
        included_tables, days=(60751, 60765),
        rm_link_err=False, rm_sr_err=False, rm_ml_err=False,
        mjd_range=None,
        ptb=None,
    ):

    days_range = days[1] - days[0] + 1

    cor_ts =  TSerie(mjd=cor_mjd, val=cor_val)
    cor = MTSerie(tseries=[cor_ts])
    cor, mask = cor.resample2(
        period_s=1, sh_s=0, tol_s=24*60*60,
        start_mjd=days[0],
        stop_mjd=days[0]+days_range,
    )

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

    # add ptb data ------
    if ptb is not None:
        d = MTSerie()
        for day in range(days[0], days[1]+1):
            d.add_mjdf_from_datfile(f'data_files/export_{day}/ptb.dat', delimiter='\t', skiprows=3)
        d, rm_mask = d.resample2(
            period_s=1, sh_s=0.05,
            tol_s=0,
            start_mjd=days[0],
            stop_mjd=days[0]+days_range
        )
        common_rm_mask = common_rm_mask | rm_mask if common_rm_mask is not None else rm_mask
        gts.append_mtserie(mts_name='ptb', mts=d)
    # -------------------
    
    # add correction data for the 698 Sr clock
    gts.append_mtserie(mts_name='cor', mts=cor)

    for table in included_tables:
        gts.mts_dict[table].rm_indexes([common_rm_mask])
    gts.mts_dict['cor'].rm_indexes([common_rm_mask])
    # gts.mts_dict['ptb'].rm_indexes([common_rm_mask])

    if mjd_range is not None:
        gts.get_range(mjd_range[0], mjd_range[1])

    if rm_sr_err:
        for rmr in rm_periods:
            gts.rm_range(rmr[0], rmr[1])

    if rm_link_err:
        for rmr in rm_periods_link:
            gts.rm_range(rmr[0], rmr[1])

    if rm_ml_err:
        for rmr in rm_periods_ml:
            gts.rm_range(rmr[0], rmr[1])

    return gts

    # gts.rm_outlayers('comb2_f_avg_counter7', target=27_732_000, maxdiff=2000)

    # gts.mts_dict['comb2_f_avg_counter7'].plot()

