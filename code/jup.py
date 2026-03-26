# %%
%load_ext autoreload
%autoreload 2
%matplotlib widget

import numpy as np

# %%
x = np.linspace(0,10,1000)
y = np.sin(x)

# %%
import matplotlib.pyplot as plt
plt.plot(x,y)
plt.show()
# %%
