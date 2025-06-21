"""
In this fiele, we create a budget of shifts.
This budget is used to calculate the total shift and uncertainty
in the frequency of a clock.
"""

from math import sqrt

class Shift:
    """Class to represent a single shift in the budget."""

    def __init__(self, name, shift=0, u=0):
        self.name = name
        self.shift = shift
        self.u = u
        self.tot_shift = 0
        self.tot_u = 0
    
    def __str__(self):
        return f'{self.name:<16}{self.shift:>8.3f} (sys: {self.u})'


class Budget:
    """Class to represent a budget of shifts."""

    def __init__(self):
        self.shifts = []
    
    def __str__(self):
        s=''
        for i in self.shifts:
            s = s + i.__str__() + '\n'
        s += '-------------------------------\n'
        s += f'{'total':<16}{self.tot_shift:>8.3f} (sys: {self.tot_u}) Hz'
        return s

    def add_shift(self, name, shift=0, u=0):
        self.shifts.append(Shift(name, shift, u))
    
    def calc(self):
        ash = 0
        au = 0
        for i in self.shifts:
            ash += i.shift
            au += i.u*i.u
        self.tot_shift = ash
        self.tot_u = sqrt(au)
        
if __name__ == "__main__":
    b = Budget()
    b.add_shift('Zeeman', -99.078150556, 0.67)
    b.add_shift('Light 698', -21.723053684, 0.14)
    b.add_shift('Light 813', -0.34, 0.47)
    b.add_shift('Collisions', 0.35, 0.52)
    b.add_shift('BBR', -2.21, 0.075)
    b.add_shift('Gravit', 2.34, 0.1)
    b.add_shift('UTC(AOS)-UTC', -0.4, 0.43)
    b.add_shift('UTC-TT', 0.1, 0.11)
    b.add_shift('electronics', 0, 0.16)
    b.calc()
    print(b)
