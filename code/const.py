from decimal import Decimal, getcontext

getcontext().prec = 30

f_th_88sr = Decimal('429_228_066_418_007.01')
f_th_87sr = Decimal('429_228_004_229_873')
f_th_87sr_vs_88sr = f_th_87sr / f_th_88sr # 0.999999855116338199940509637816
