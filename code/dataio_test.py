from dataio.mts import get_data_single_mjd, get_data_names, set_flags_in_range
from rm_data import rm_periods_link, rm_periods

dataset = "rls_hydro_cavity_beat"

for rm_period in rm_periods_link:
    print(f"Setting flags for MJD {rm_period[0]} - {rm_period[1]}")
    set_flags_in_range(
        dataset=dataset,
        from_mjd=rm_period[0],
        to_mjd=rm_period[1],
        flag_value=0
    )

get_data_single_mjd(dataset, 60760).plotf()

get_data_single_mjd(dataset, 60761).plotf()

get_data_single_mjd(dataset, 60762).plotf()

get_data_single_mjd(dataset, 60763).plotf()

get_data_single_mjd(dataset, 60764).plotf()
