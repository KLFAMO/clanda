from shift import get_shift_698, get_shift_b
from timanda.tserie import TSerie, MTSerie, GTserie

gtsc = GTserie("gtsc")

def add_cor_to_gts(t_mjd, t_val, name, fmjd=60752, tmjd=60817):
    cor_ts =  TSerie(mjd=t_mjd, val=t_val)
    cor = MTSerie(TSerie=cor_ts)
    cor, mask = cor.resample2(
        period_s=1, sh_s=0, tol_s=24*60*60,
        start_mjd=fmjd,
        stop_mjd=tmjd,
    )
    gtsc.append_mtserie(mts_name=name, mts=cor)

p_b = [
    [60751, 0.25],
    [60753.9426, 0.15],
    [60788, 0.3],
    [60788.81604, 0.1],
    [60808.45860431, 0.2],
    [60810.452601, 0.2],
    [60816.306, 0.2],
]

sh_b_mjd = [x[0] for x in p_b]
p_b_p = [x[1] for x in p_b]
sh_b_val = [get_shift_b(x) for x in p_b_p]

p_698 = [
    [60751, 8.06], # 0.5],
    [60753.9426, 8.06], # 0.5],
    [60788, 3.47], # 0.4],
    [60788.81604, 3.47], # 0.4],
    [60808.45860431, 8.06], #0.5],
    [60810.452601, 8.06], # 0.5],
    [60816.306, 5.64], # 0.45],
]

sh_698_mjd = [x[0] for x in p_698]
p_698_p = [x[1] for x in p_698]
sh_698_val = [get_shift_698(x) for x in p_698_p]

c_sh = {}
c_sh['813'] = -0.8
c_sh['atoms'] = -0.01
c_sh['bbr'] = -2.21
c_sh['grav'] = 2.33929
c_sh_all = sum(c_sh.values())

add_cor_to_gts(sh_b_mjd, sh_b_val, 'b', 60751, 60817)
add_cor_to_gts(sh_698_mjd, sh_698_val, '698', 60751, 60817)

gtsc.math_mts_and_mts('add', 'b', '698', 'tmp1')
gtsc.math_mts_and_number('add', 'tmp1', c_sh_all, 'sh_total')

gtsc.plot(mts_names=[
    'b',
    '698',
    'sh_total',
])

gtsc.save('d_cor.joblib')
