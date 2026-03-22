
from dataio.mts import get_data_single_mjd, mjd2utc, get_gts_single_mjd
from timanda.gtserie import GTserie


def calc(*, from_mjd, to_mjd, create_cmp_file: bool = False, plot: bool = False, **kwargs):
    mjd = int(from_mjd)
    date_str = mjd2utc(from_mjd, strfmt='%Y-%m-%d')

    # gts = GTserie('comp2')
    # gts.append_mtserie("comb_hydro_698", get_data_single_mjd("comb_hydro_698", from_mjd))
    # gts.append_mtserie("sr1_aom_cor", get_data_single_mjd("sr1_aom_cor", from_mjd))
    # gts.get_range(mjd, mjd+1) 

    gts = get_gts_single_mjd(datasets=["comb_hydro_698", "sr1_aom_cor"], mjd=mjd, allowed_flag=1)
    
    ptb_freq = 194_399_987_408_400 
    nc_rls = 168.5e6
    gts.math_mts_and_number('multiply', 'comb_hydro_698', 0, 'zero')
    gts.math_mts_and_number('add', 'zero', ptb_freq+nc_rls, 'f_ule15')
    N15 = 777_621
    gts.math_mts_and_number('divide', 'f_ule15', N15, 'fr')
    gts.math_mts_and_number('multiply', 'sr1_aom_cor', -4, 'fc')
    N = 1_716_959.
    gts.math_mts_and_number('multiply', 'fr', N, 'ft1')  # <----
    gts.math_mts_and_number('add', 'ft1', 0, 'ft')
    gts.math_mts_and_mts('add', 'fc', 'comb_hydro_698', 'ftmp')
    gts.add_mts_to_mts('ftmp', 'ft', 'fsrnc')
    # gts.add_mts_to_mts('fsrnc', 'cor', 'fsrc')
    gts.math_mts_and_number('add', 'fsrnc', 0, 'fsrc')
    gts.math_mts_and_number('divide', 'fsrc', ptb_freq+nc_rls, 'ratio')

    gts.math_mts_and_number('add', 'zero', 1, 'valid')
    gts.math_mts_and_number('add', 'zero', 1e-15, 'uncert')

    if plot:
        gts.plot(mts_names=[
            'comb_hydro_698',
            'sr1_aom_cor',
            'ratio',
            ], 
            # save_filename='plot.png',
            show=1)

    if create_cmp_file:
        gts.create_comparator_file(
            # filename=f'../share_files/UMK_LO-UMK_RLS/{date_str}_UMK_LO-UMK_RLS.dat',
            filename=f'{date_str}_UMK_LO-UMK_RLS.dat',
            mts_names=['comp2', 'valid', 'uncert'],
            headers=['A->B', 'flag', 'relative systematic uncertainty'],
            formats=['.6f', '.0f', '.4e'],
        )