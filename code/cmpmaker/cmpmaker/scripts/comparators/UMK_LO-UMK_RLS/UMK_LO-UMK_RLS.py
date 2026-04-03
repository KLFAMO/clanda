
from dataio.mts import get_data_single_mjd, mjd2utc
from timanda.gtserie import GTserie


def calc(*, from_mjd, to_mjd, **kwargs):
    mjd = int(from_mjd)
    date_str = mjd2utc(from_mjd, strfmt='%Y-%m-%d')
    d = get_data_single_mjd("rls_hydro_cavity_beat", from_mjd)
    gts = GTserie('comp2')
    gts.append_mtserie("rls_hydro_cavity_beat", d)
    gts.get_range(mjd, mjd+1) 
    
    gts.math_mts_and_number('add', 'rls_hydro_cavity_beat', 168.5e6, 'comp2')
    gts.math_mts_and_number('multiply', 'rls_hydro_cavity_beat', 0, 'zero')
    gts.math_mts_and_number('add', 'zero', 1, 'valid')
    gts.math_mts_and_number('add', 'zero', 1e-17, 'uncert')

    gts.plot(mts_names=[
        'rls_hydro_cavity_beat',
        'comp2',
    ])

    gts.create_comparator_file(
        filename=f'../tock_data/UMK_LO-UMK_RLS/{date_str}_UMK_LO-UMK_RLS.dat',
        # filename=f'{date_str}_UMK_LO-UMK_RLS.dat',
        mts_names=['comp2', 'valid', 'uncert'],
        headers=['A->B', 'flag', 'relative systematic uncertainty'],
        formats=['.6f', '.0f', '.4e'],
    )