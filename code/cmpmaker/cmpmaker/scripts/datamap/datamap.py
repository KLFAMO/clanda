
DATAMAP = {
    "comb_hydro_698": {
        "description": "Beat note of the 698 nm laser with the comb",
        "source":{
            "type": "famo_database",
            "table": "comb2_f_avg_counter5",
        },
        "unit": "Hz",
    },
    "rls_hydro_cavity_beat": {
        "description": "Beat note of rls with the cavity_hydro",
        "source":{
            "type": "famo_database",
            "table": "comb2_f_avg_counter7",
        },
        "unit": "Hz",
    },
    "sr1_aom_cor": {
        "description": "DDS value sent to Sr1 AOM to correct the clock laser frequency",
        "source":{
            "type": "famo_database",
            "table": "sr1_ml1_f",
        },
        "unit": "Hz",
    },
}
