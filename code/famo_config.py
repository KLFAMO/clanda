# This file contains the configuration for the FAMO experiment.

# aom
aom_nc_698_sr1_to_hydro = 84e6
aom_cor_698_sr1 = -4 * 101.046865e6 # correction AOM, double pass and doubled RF freq

aom_nc_1542_ule_to_comb2 = 79.0e6  # nc + dedrift
aom_pdh_1542_ule = 80.0e6 # aom after nkt laser for pdh

# theoretical frequencies
fth698_Sr88 = 429_228_066_418_007.0 # theoretical frequency of clock transition
fth698_Sr88_to_comb2 = ( # frequency of 698 comming to comb2
    fth698_Sr88 
    - aom_cor_698_sr1
    + aom_nc_698_sr1_to_hydro
)
fth689_Sr88_to_comb2 = 434_828_909_312_334.0 # frequency of 689 comming to comb2
fth1542_hydro = 194_399.99e9
fth1542_hydro_to_comb2 = (
    fth1542_hydro
    + aom_nc_1542_ule_to_comb2
    - aom_pdh_1542_ule
    # -64.6e6 + 0* 249993412.7884
)
