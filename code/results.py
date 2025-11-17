import numpy as np
from matplotlib import pyplot as plt

from_str = '2025-03-26'
to_str = '2025-03-30'
data_str = from_str
# get path of current script
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
# get project script by going one level up
project_dir = os.path.dirname(script_dir)
print(f'Project directory: {project_dir}')

comp_name = 'UMK_LO-UMK_RLS'

# load comparator data files
d1 = np.loadtxt(f'{project_dir}/tock_data/{comp_name}/{data_str}_{comp_name}.dat')

print(d1)
# plot data
plt.figure(figsize=(10, 5))
plt.plot(d1[:, 0], d1[:, 1], label='Comparator Data')
plt.xlabel('Time (MJD)')
plt.ylabel('Frequency Difference (Hz)')
plt.legend()
plt.show()