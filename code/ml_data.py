"""
In this file, we define the data for the multi-lock measurements.
It is used by the other scripts to calculate the shifts and uncertainties
in the frequency of a clock.
"""

mlb = (
    {
        'range': (60751.3643, 60751.678696), 'param': 'B', 'xs': [0.25, 0.3],
        'err': 1e-14*429e12, 'dy': -120.815,
    }, # 0  słaby - skacze pomiedzy liniami
    {
        'range': (60751.6823054, 60751.88), 'param': 'B', 'xs': [0.25, 0.2],
        'err': 8e-16*429e12, 'dy': 97.6268,
    }, # 1
    {
        'range': (60751.8864, 60752.078), 'param': 'B', 'xs': [0.25, 0.15],
        'err': 8e-17*429e12, 'dy': 173.51878,
    }, # 2
    {
        'range': (60752.93375, 60753.0035), 'param': 'B', 'xs': [0.25, 0.1],
        'err': 8e-16*429e12, 'dy': 226.037,
    }, # 3
    {
        'range': (60752.828, 60752.93188), 'param': 'B', 'xs': [0.25, 0.4],
        'err': 0, 'dy': 0,
        # 'err': 2e-15*429e12, 'dy': -454.766,
    }, # 4  to skakał pomiędzy liniami
    {
        'range': (60753.3385, 60753.408), 'param': 'B', 'xs': [0.25, 0.1],
        'err': 1.1e-15*429e12, 'dy': 227.338,
    }, # 5   nie ogarnięte jeszcze
    {
        'range': (60753.55, 60753.741), 'param': 'B', 'xs': [0.25, 0.15],
        'err': 0, 'dy': 0,
        # 'err': 3e-16*429e12, 'dy': 128.038,
    }, # 6  to skakał pomiędzy liniami
    {
        'range': (60753.75217, 60753.774), 'param': 'B', 'xs': [0.25, 0.05],
        'err': 2e-15*429e12, 'dy': 265.25,
    }, # 7
    {
        'range': (60753.841, 60753.9355), 'param': 'B', 'xs': [0.25, 0.6],
        'err': 8e-16*429e12, 'dy': -1284.176,
    }, # 8
    
    # {
    #     'range': (60756.755, 60756.798), 'param': 'B', 'xs': [0.5, 0.025],
    #     'err': 5e-16*429e12, 'dy': 94.9685,
    # }, # 6  tu są jakies zle parametry B - sprawdzic
    # {
    #     'range': (60756.44296, 60756.52), 'param': 'B', 'xs': [0.5, 0.02],
    #     'err': 3e-16*429e12, 'dy': 95.8519,
    # }, # 7  tu są jakies zle parametry B - sprawdzic
    

)

ml698 = (
    {
        'range': (60755.5027, 60755.575), 'param': '698ampl', 'xs': [8.06, 3.47],  # [0.5, 0.4]
        'err': 1.5e-16*429e12, 'dy': 12.5016,
    }, # 0   
    {
        'range': (60755.633, 60755.7739), 'param': '698ampl', 'xs': [8.06, 1.82],  # [0.5, 0.35]
        'err': 1e-16*429e12, 'dy': 16.771,
    }, # 1
    {
        'range': (60755.7785, 60756.234), 'param': '698ampl', 'xs': [8.06, 12.62],  # [0.5, 0.6]
        'err': 5e-16*429e12, 'dy': -12.43,
    }, # 2
)