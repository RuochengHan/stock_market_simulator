import matplotlib.pyplot as plt
import numpy as np
from mpl_finance import candlestick_ohlc
import sys
from numpy import genfromtxt

data = np.loadtxt(sys.argv[1])

plt.plot(data)
plt.show()
