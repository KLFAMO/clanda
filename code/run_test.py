from cmpmaker.runner import run

run(
    # script_path="comparators/UMK_LO-UMK_RLS",
    script_path="comparators/UMK_LO-UMK_Sr1",
    from_mjd=60764.0,
    to_mjd=60764.1,
    plot=True,
    create_cmp_file=False,
)

# for i in range(60751, 60795):
#     print(f"Running test for MJD {i}")
#     run(
#         script_path="get_raw",
#         from_mjd=i,
#         to_mjd=i+0.1,
#     )