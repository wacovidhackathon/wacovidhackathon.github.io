import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime


def plot(dateDict):
    # create data
    x = []
    y = []

    for i in dateDict:
        x.append(datetime.strptime(i, '%Y-%m-%d %H:%M:%S'))
        y.append(dateDict.get(i))

    # plot
    plt.plot(x, y, '-o')
    plt.gcf().autofmt_xdate()
    plt.show()


myDict = {'2005-11-11 16:11:22': 1, '2005-11-11 16:14:24': 3}
plot(myDict)
