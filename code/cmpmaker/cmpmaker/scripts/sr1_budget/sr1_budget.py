from cmpmaker.scripts.sr1_shift698 import shift698
from cmpmaker.scripts.sr1_shift_zeeman import shift_zeeman
from cmpmaker.scripts.sr1_shift_others import shift_others

def budget():
    out = shift_zeeman() + shift698() + shift_others()
    return out