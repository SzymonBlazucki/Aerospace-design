import reader
import scipy as sp
import matplotlib.pyplot as plt
from scipy import interpolate
import numpy as np


def interp(x, y):
    f = interpolate.interp1d(x, y, kind='cubic', fill_value='extrapolate')
    return f

testFirstTable, testSecondTable = reader.readXLFR('xlfrData/test.csv')



class Forces:
    def __init__(self, first, second):
        self.Cl = interp(first['y-span'], first.Cl)
    def axialForcePlot(self):
        pass

    def shearForcePlot(self):
        pass

    def torquePlot(self):
        pass

    def bendingMomentPlot(self):
        pass

testForces = Forces(testFirstTable,testSecondTable)
span =
#print(testForces.Cl(np.linspace(0,10,100)))
plt.plot()
class Wing:
    pass
