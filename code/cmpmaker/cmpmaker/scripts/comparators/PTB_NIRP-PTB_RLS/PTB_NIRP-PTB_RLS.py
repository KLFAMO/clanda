# comparator link ptb_NIRT-ptb_RLS

# # PTB_NIRP-FAMO_RLS50T -> fixed frequency shift +15 MHz  (od Jochena)
# # schemat  NIRP - FAMO_RLS = 15 MHz

from dataio.dataio import mjd2utc
import numpy as np

def calc(*, from_mjd, to_mjd, **kwargs):

    mjd = from_mjd
    date_str = mjd2utc(mjd, strfmt='%Y-%m-%d')

    start_mjd = mjd
    stop_mjd = mjd+1
    period_mjd = 1/24/60/60  # 1 second
    nm = np.arange(start_mjd, stop_mjd, period_mjd)

    shift = -35e6

    with open(f"../tock_data/PTB_NIRP-PTB_RLS/{date_str}_PTB_NIRP-PTB_RLS.dat", 'w') as f:
        # f.write(f"# MJD\tA-B\tvalidity\n")
        
        for mjd in nm:
            f.write(f"{mjd:.6f}")
            f.write(f"\t{shift:.6f}")
            f.write(f"\t1")
            f.write('\n')
    f.close()