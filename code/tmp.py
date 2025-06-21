"""
This script calculates the frequency of a laser system based on given constants and parameters.
It is not used in the main codebase but is provided for reference or testing purposes.
"""

rls = 194_399_987_408_400 + 14e6
nc_rls = 168.5e6
beat_ptb = 27.729e6
N15 = 777_621

f_LO = rls + nc_rls + beat_ptb

fr = (f_LO - 70e6) / N15
frdm = 4*fr - 980e6
mfrdm = 19_973_651.11

f_NKT = f_LO - 160e6

print(f"{rls:_}")
print(fr)
print(frdm)
print(mfrdm)
print(frdm - mfrdm)
print(f"{f_NKT:_}")