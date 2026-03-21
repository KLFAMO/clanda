from dataio.mts import get_data_single_mjd, get_data_names, mk_clean_single_mjd
# print(get_data_names())
d = get_data_single_mjd("rls_hydro_cavity_beat", 60760)
# mk_clean_single_mjd("rls_hydro_cavity_beat", 60760)
d.set_flags_in_range(60760.8382, 60760.8935, 0)

d.plotf()