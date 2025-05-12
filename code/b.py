import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# Twoje dane
m = (
    {'range': (60751.3643, 60751.678696), 'param': 'B', 'x': [0.25, 0.3]},
    {'range': (60751.6823054, 60751.88), 'param': 'B', 'x': [0.25, 0.2], 'err': 8e-16, 'y': 97.6268},
    {'range': (60751.8864, 60752.078), 'param': 'B', 'x': [0.25, 0.15], 'err': 8e-17, 'y': 173.51878},
    {'range': (60752.782769, 60752.93188), 'param': 'B', 'x': [0.25, 0.4], 'err': 0, 'y': 0},
    {'range': (60752.93375, 60753.0035), 'param': 'B', 'x': [0.25, 0.1], 'err': 8e-16, 'y': 226.037},
    # {'range': (60753.3385, 60753.8), 'param': 'B', 'x': [0.25, 0.1], 'err': 0, 'y': 0},
)

# Teoretyczna wartość dla przeskalowania niepewności względnej
val_theor = 429e12 

# Przygotowanie danych
x1_list, x2_list, dy_list, dy_err_list = [], [], [], []
for entry in m:
    if entry.get('err', 0) > 0 and entry.get('f2_vs_f1_hz', 0) != 0:
        x1, x2 = entry['vals']
        dy = entry['f2_vs_f1_hz']
        rel_err = entry['err']
        abs_err = rel_err * val_theor  # niepewność bezwzględna

        x1_list.append(x1)
        x2_list.append(x2)
        dy_list.append(dy)
        dy_err_list.append(abs_err)

# Konwersja do arrayów
x1 = np.array(x1_list)
x2 = np.array(x2_list)
dy = np.array(dy_list)
dy_err = np.array(dy_err_list)

# Model: dy = a(x2² - x1²) + b(x2 - x1)
def model(inputs, a, b):
    x1, x2 = inputs
    return a * (x2**2 - x1**2) + b * (x2 - x1)

# Dopasowanie
popt, pcov = curve_fit(
    model, (x1, x2), dy,
    sigma=dy_err, absolute_sigma=True
)

a, b = popt
a_err, b_err = np.sqrt(np.diag(pcov))

print(f"a = {a:.5e} ± {a_err:.1e}")
print(f"b = {b:.5e} ± {b_err:.1e}")

# -------------------------------------
# RYSOWANIE
# -------------------------------------

# Generujemy zakres x do wykresu
x_plot = np.linspace(min(np.min(x1), np.min(x2)) - 0.15,
                     max(np.max(x1), np.max(x2)) + 0.15, 500)
y_plot = a * x_plot**2 + b * x_plot

plt.figure(figsize=(8, 5))
plt.plot(x_plot, y_plot, label='dopasowana krzywa: $y = ax^2 + bx$')

# Dodaj pomiary jako strzałki / odcinki
for xi1, xi2, dyi in zip(x1, x2, dy):
    y1_est = a * xi1**2 + b * xi1
    y2_est = y1_est + dyi
    plt.plot([xi1, xi2], [y1_est, y2_est], 'ro-')
    plt.text((xi1 + xi2)/2, (y1_est + y2_est)/2, f"{dyi:.1f} Hz", ha='center', va='bottom', fontsize=8)

plt.xlabel("x (parametr B)")
plt.ylabel("y (wartość funkcji)")
plt.title("Dopasowanie funkcji kwadratowej do różnicowych pomiarów")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
