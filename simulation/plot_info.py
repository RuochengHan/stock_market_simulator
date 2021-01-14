import matplotlib.pyplot as plt
import numpy as np
from mpl_finance import candlestick_ohlc
import sys
from numpy import genfromtxt

data = np.loadtxt(sys.argv[1])

for i in range(100):
    plt.plot(data[:, i])

plt.savefig('./figures/' + sys.argv[1] + '.png')
