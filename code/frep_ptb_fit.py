# import sqldata as sqd

# fr1 = sqd.getdata("comb2_f_rep", from_mjd=60747.4846, to_mjd=60747.4865).mean()
# fr2 = sqd.getdata("comb2_f_rep", from_mjd=60747.498, to_mjd=60747.505).mean()
# fr3 = sqd.getdata("comb2_f_rep", from_mjd=60747.524, to_mjd=60747.534).mean()
# fr4 = sqd.getdata("comb2_f_rep", from_mjd=60747.521, to_mjd=60747.5224).mean()

fr1 = 249_994_055.75913298
fr2 = 249_993_734.2717929
fr3 = 249_993_412.78654367
fr4 = 249_993_091.30205187

dmfr1 = 19_976_223.036
dmfr2 = 19_974_937.094
dmfr3 = 19_973_651.143
dmfr4 = 19_972_365.207

fr1r = 249_994_055.7593     # n
fr2r = 249_993_734.273      # n+1
fr3r = 249_993_412.7865     # n+2
fr4r = 249_993_091.302      # n+3

# n3 = 

fadd = -302e6
fth = 194.400e12 - 70e6 + fadd
n = 777618

print(f"n: {n}")
print(f"fadd: {fadd:_}")

n1 = n-2
n2 = n-1
n3 = n
n4 = n+1

cfr1 = fth/n1
cfr2 = fth/n2
cfr3 = fth/n3
cfr4 = fth/n4

e = (
    (fr1-cfr1)*(fr1-cfr1) +
    (fr2-cfr2)*(fr2-cfr2) +
    (fr3-cfr3)*(fr3-cfr3) +
    (fr4-cfr4)*(fr4-cfr4)
)

print(f"e: {e:_}")

