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
    def __init__(self, first, second, freeVel):
        self.v = freeVel
        self.Cl = interp(first['y-span'], first.Cl)
        self.cord = interp(first['y-span'], first.Chord)
        self.lCd = interp(first['y-span'], first.ICd)
    def lift(self, x):
        L = self.Cl(x) * 0.5 * 1.225 * self.v ** 2 * self.cord(x) #* abs(x[1]-x[0])
        print(np.sum(L))
        return L
    def axialForcePlot(self):
        pass
    def shearForcePlot(self):
        pass

    def torquePlot(self):
        pass

    def bendingMomentPlot(self):
        pass

testForces = Forces(testFirstTable,testSecondTable, 10)
span = np.linspace(-25.5, 25.5 ,10000)
print()
spanDiff = span[1:] - span[:-1]
#print(testForces.Cl(np.linspace(0,10,100)))
#plt.plot(span, testForces.cord(span))
plt.plot(span, testForces.lift(span))
plt.show()

#print(span[1:] - span[:-1] )

class Wing:
    pass
