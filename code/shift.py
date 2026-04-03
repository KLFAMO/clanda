import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from ml_data import mlb, ml698, ml813, mlatoms

def parab_model(x, a, b, c):
    return a * x*x + b*x + c

def parab_fit_model(input, a, b):
    x1, x2 = input
    return a * (x2*x2 - x1*x1) + b * (x2 - x1)

def lin_model(x, a):
    return a * x

def lin_fit_model(input, a):
    x1, x2 = input
    return a * (x2 - x1)
    

class Shift:
    def __init__(self, mes):
        self.mes = mes
        self.x1_list = []
        self.x2_list = []
        self.dy_list = []
        self.dy_err_list = []
        self.convert_mes_to_arrays()
    
    def convert_mes_to_arrays(self):
        for entry in self.mes:
            if entry.get('err', 0) > 0 and entry.get('dy', 0) != 0:
                x1, x2 = entry['xs']
                self.x1_list.append(x1)
                self.x2_list.append(x2)
                self.dy_list.append(entry['dy'])
                self.dy_err_list.append(entry['err'])
        self.x1 = np.array(self.x1_list)
        self.x2 = np.array(self.x2_list)
        self.dy = np.array(self.dy_list)
        self.dy_err = np.array(self.dy_err_list)


class Shift_lin(Shift):
    def __init__(self, mes):
        super().__init__(mes)
        self.fit_model = lin_fit_model
        self.model = lin_model
    
    def fit(self):
        popt, pcov = curve_fit(
            self.fit_model, (self.x1, self.x2), self.dy,
            sigma=self.dy_err, absolute_sigma=True
        )
        self.popt = popt
        self.pcov = pcov
        self.sigma_par = np.sqrt(np.diag(pcov))
        self.a = popt[0]
        # print("Fitting results")
        # print("popt: ", popt)
        # print("pcov: ", pcov)
        # print("sigma: ", self.sigma_par)
        # self.xw = -self.b / (2 * self.a)
        # print("xw: ", self.xw)
        # self.yw = self.model(self.xw, *self.popt, 0)
        # self.c = -self.yw
        # print("yw: ", self.yw)
        print("a = ", self.a)
        # print("b = ", self.b)
        print("a err = ", self.sigma_par[0])
        # print("b err = ", self.sigma_par[1])
        a = self.a
        ua = self.sigma_par[0]
        x0 = 8.06
        ux = 0.05
        u = np.sqrt(
            (x0*ua)**2 +
            (a*ux)**2
        )
        print(f'u: {u}')
    
    def plot(self):
        # Generujemy zakres x do wykresu
        x_plot = np.linspace(min(np.min(self.x1), np.min(self.x2)) - 0.15,
                             max(np.max(self.x1), np.max(self.x2)) + 0.15, 500)
        y_plot = self.model(x_plot, self.a)

        plt.plot(x_plot, y_plot, label='dopasowanie')

        for entry in self.mes:
            if entry.get('err', 0) > 0 and entry.get('dy', 0) != 0:
                x1, x2 = entry['xs']
                dy = entry['dy']
                err = entry['err']
                vx1 = self.model(x1, self.a)
                vx2 = self.model(x2, self.a)
                vmean = (vx1 + vx2) / 2
                y1 = vmean - dy / 2
                y2 = vmean + dy / 2
                
                plt.errorbar([x1, x2] , [y1, y2], yerr=err, fmt='o', label='dane', capsize=5)

        plt.xlabel('x')
        plt.ylabel('y')
        plt.grid()
        plt.title('Dopasowanie paraboli')
        plt.legend()
        plt.show()
    
    def get_shift(self, x):
        return self.model(x, self.a)


class Shift_sqr(Shift):
    fit_model = parab_fit_model
    model = parab_model

    def __init__(self, mes):
        super().__init__(mes)
        self.fit_model = parab_fit_model
        self.model = parab_model
        
    
    def fit(self):
        popt, pcov = curve_fit(
            self.fit_model, (self.x1, self.x2), self.dy,
            sigma=self.dy_err, absolute_sigma=True
        )
        self.popt = popt
        self.pcov = pcov
        self.sigma_par = np.sqrt(np.diag(pcov))
        self.a = popt[0]
        self.b = popt[1]
        self.xw = -self.b / (2 * self.a)
        print("xw: ", self.xw)
        self.yw = self.model(self.xw, *self.popt, 0)
        self.c = -self.yw
        print("yw: ", self.yw)
        print("a = ", self.a)
        print("b = ", self.b)
        print("a err = ", self.sigma_par[0])
        print("b err = ", self.sigma_par[1])
        a = self.a
        b = self.b
        ua = self.sigma_par[0]
        ub = self.sigma_par[1]
        x0 = 0.15
        ux = 0.5e-3
        # p1 = (2*x*a*ua + b*ux)**2
        # p2 = (x*x*ua + x*ub)**2
        u = np.sqrt(
            (x0**4) * ua**2 +
            (x0**2) * ub**2 +
            ((2 * a * x0 + b)**2) * ux**2
        )
        print(f'u = {u}')
    
    def plot(self):
        # Generujemy zakres x do wykresu
        x_plot = np.linspace(min(np.min(self.x1), np.min(self.x2)) - 0.15,
                             max(np.max(self.x1), np.max(self.x2)) + 0.15, 500)
        y_plot = self.model(x_plot, self.a, self.b, self.c)

        plt.plot(x_plot, y_plot, label='dopasowanie')

        for entry in self.mes:
            if entry.get('err', 0) > 0 and entry.get('dy', 0) != 0:
                x1, x2 = entry['xs']
                dy = entry['dy']
                err = entry['err']
                vx1 = self.model(x1, self.a, self.b, self.c)
                vx2 = self.model(x2, self.a, self.b, self.c)
                vmean = (vx1 + vx2) / 2
                y1 = vmean - dy / 2
                y2 = vmean + dy / 2
                
                plt.errorbar([x1, x2] , [y1, y2], yerr=err, fmt='o', label='dane', capsize=5)

        plt.xlabel('x')
        plt.ylabel('y')
        plt.grid()
        plt.title('Dopasowanie paraboli')
        plt.legend()
        plt.show()
    
    def get_shift(self, x):
        return self.model(x, *self.popt, self.c)
        
def get_shift_b(x):
    s = Shift_sqr(mes=mlb)
    s.fit()
    return s.get_shift(x)

def get_shift_698(x):
    s = Shift_lin(mes=ml698)
    s.fit()
    return s.get_shift(x)


if __name__ == "__main__":
    m = mlb
    # m = ml698
    # m = ml813
    # m = mlatoms

    s = Shift_sqr(mes=m)
    # s = Shift_lin(mes=m)
    s.fit()
    print(s.get_shift(0.15))
    # print(s.get_shift(8.06))
    s.plot()