import matplotlib.pyplot as plt
import numpy as np
import talib
import tushare as ts
import mpl_finance as mpf
import sys
from numpy import genfromtxt
from matplotlib import gridspec

data = np.loadtxt(sys.argv[1])
price = data[:, 0]
volume = data[:, 1]
gap = int(sys.argv[2])
price = np.reshape(price, (-1, gap))
volume = np.reshape(volume, (-1, gap))

#data = ts.get_k_data('399300', index=True, start='2017-01-01', end='2017-06-31')
sma_10 = talib.SMA(np.array(price[:, gap-1]), 10)
sma_35 = talib.SMA(np.array(price[:, gap-1]), 35)
#sma_200 = talib.SMA(np.array(price[:, gap-1]), 100)

fig = plt.figure(figsize=(17, 10))
gs = gridspec.GridSpec(2, 1, height_ratios=[7, 3])
ax = plt.subplot(gs[0])
ax2 = plt.subplot(gs[1])

#ax.set_xticks(range(0, len(data['date']), 10))
#ax.set_xticklabels(data['date'][::10])
ax.set_xticks(range(0, len(price[:, 0]), 10))
ax.set_xticklabels(range(0, len(price[:, 0]))[::10])
ax.plot(sma_10, label='MA5')
ax.plot(sma_35, label='MA35')
#ax.plot(sma_200, label='MA100')
ax.legend(loc='upper left')
ax.grid(True)

mpf.candlestick2_ochl(ax, price[:, 0], price[:, gap-1],
                    np.amax(price, axis=1), np.amin(price, axis=1),
                    width=0.5, colorup='g',
                    colordown='r', alpha=0.6)

ax2.set_xticks(range(0, len(price[:, 0]), 10))
ax2.grid(True)
mpf.volume_overlay(ax2, price[:, 0], price[:, gap-1],
                    np.sum(volume, axis=1),
                    width=0.5, colorup='g',
                    colordown='r', alpha=0.8)
plt.subplots_adjust(hspace=0)
plt.show()
