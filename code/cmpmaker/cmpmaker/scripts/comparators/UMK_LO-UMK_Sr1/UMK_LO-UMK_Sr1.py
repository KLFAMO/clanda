
from dataio.mts import get_data_single_mjd, mjd2utc, get_gts_single_mjd
# from timanda.gtserie import GTserie
from cmpmaker.scripts.sr1_budget import budget


def calc(*, from_mjd, to_mjd, create_cmp_file: bool = False, plot: bool = False, result_file=None, **kwargs):
    # print(f"Inside script Calculating UMK_LO-UMK_Sr1 from MJD {from_mjd} to {to_mjd}")
    mjd = int(from_mjd)
    date_str = mjd2utc(from_mjd, strfmt='%Y-%m-%d')

    # gts = GTserie('comp2')
    # gts.append_mtserie("comb_hydro_698", get_data_single_mjd("comb_hydro_698", from_mjd))
    # gts.append_mtserie("sr1_aom_cor", get_data_single_mjd("sr1_aom_cor", from_mjd))
    # gts.get_range(mjd, mjd+1) 

    gts = get_gts_single_mjd(
        datasets=["comb_hydro_698", 
                  "sr1_aom_cor",
                #   "intensity_698_PD"
                  ], 
        mjd=mjd, allowed_flag=1,
        from_mjd=from_mjd,
        to_mjd=to_mjd,
    )
    gts, cmm = gts.align_all_to_grid_zoh_and_drop_missing(start_mjd=mjd, stop_mjd=mjd+1)
    
    fth_Sr88 = 429_228_066_418_007.0 # theoretical frequency of clock transition (den) (A)
    fth_lo = 194.4e12  # theoretical frequency of the LO laser after NC AOM  (num) (B)
    ptb_freq = 194_399_987_408_400 
    nc_rls = 168.5e6

    gts.math_mts_and_number('multiply', 'comb_hydro_698', 0, 'zero')  # zero mts

    gts.math_mts_and_number('multiply', 'sr1_aom_cor', 4, 'fc_aom') # atoms correction
    # gts.math_mts_and_number('multiply', 'cor', 1, 'mcor')  # total shift 698
    # gts.math_mts_and_mts('add', 'fc_aom', 'mcor', 'mfc')  # atoms correction + total shift
    # lightshift
    # gts.math_mts_and_number('multiply', 'intensity_698_PD', -0.0382, 'lscor')  # light shift correction
    # gts.math_mts_and_mts('add', 'fc_aom', 'lscor', 'lsfc_aom')  # atoms correction + light shift correction

    # gts.math_mts_and_number('add', 'fc_aom', -44.84, 'mfc')  # atoms correction + total shift  temporary, without total shift
    gts.math_mts_and_number('add', 'fc_aom', budget(), 'mfc')  # atoms correction + total shift  temporary, without total shift
    gts.math_mts_and_number('add', 'zero', fth_Sr88, 'fth88')  # theoretical frequency of the 698 Sr clock
    gts.math_mts_and_mts('add', 'fth88', 'mfc', 'fcav698')  # frequency of the 698 cavity
    gts.math_mts_and_number('add', 'fcav698', 84e6, 'fcomb698') # frequency of the 698 laser going to the comb
    gts.math_mts_and_number('multiply', 'comb_hydro_698', -1, 'mbeat698')  # beat of the 698 laser with the comb (minus sign)
    gts.math_mts_and_mts('add', 'fcomb698', 'mbeat698', 'fN698')  # frequency of the 698 laser after the comb

    N698 = 1_716_959.0
    gts.math_mts_and_number('add', 'fN698', -70e6, 'tmp1')  # frequency between N=1 and N698
    gts.math_mts_and_number('divide', 'tmp1', N698, 'fr')  # f_rep

    # # comparison with the AOS
    # gts.math_mts_and_number('add', 'comb_frep_dm', 980e6, 'fraostmp')
    # gts.math_mts_and_number('divide', 'fraostmp', 4, 'fr_aos')  # frequency measured by the AOS
    # gts.math_mts_and_number('multiply', 'fr', -1, 'mfr')  # negative fr
    # gts.math_mts_and_mts('add', 'mfr', 'fr_aos', 'diffr')  # diffr = fr - fr_aos
    # gts.math_mts_and_number('divide', 'diffr', 250e6, 'diffr_rel')  # diffr relative AOS vs Sr88
    # gts.append_mtserie(
    #     mts_name='avg',
    #     mts=gts.mts_dict['diffr_rel'].resample(period_s=600)
    # )

    # calculate 1542 cavity frequency
    N1542 = 777_621.0
    gts.math_mts_and_number('multiply', 'fr', N1542, 'tmp2') # frequency between N=1 and N1542
    gts.math_mts_and_number('add', 'tmp2', 35e6+35e6, 'f1542')  # frequency of the 1542 cavity

    # calculate comparator
    gts.math_mts_and_number('add', 'f1542', -fth_lo, 'DAB')

    ## additional columns
    gts.math_mts_and_number('add', 'zero', 1, 'valid')
    gts.math_mts_and_number('add', 'zero', 2e-15, 'uncert')

    # gts.rm_outlayers('DAB', target=197641414)


    if plot:
        gts.plot(mts_names=[
            'comb_hydro_698',
            'sr1_aom_cor',
            'DAB',
            ], 
            # save_filename='plot.png',
            show=1)

    # if create_cmp_file:
    #     gts.create_comparator_file(
    #         filename=f'../tock_data/UMK_LO-UMK_Sr1/{date_str}_UMK_LO-UMK_Sr1.dat',
    #         # filename=f'{date_str}_UMK_LO-UMK_Sr1.dat',
    #         mts_names=['DAB', 'valid', 'uncert'],
    #         headers=['A->B', 'flag', 'relative systematic uncertainty'],
    #         formats=['.6f', '.0f', '.4e'],
    #     )
    if result_file is not None:
        gts.dump_npz(result_file)