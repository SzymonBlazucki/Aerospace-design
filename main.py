import math

import reader
import scipy as sp
import matplotlib.pyplot as plt
from scipy import interpolate
from scipy.integrate import quad
import numpy as np


def interp(x, y):
    f = interpolate.interp1d(x, y, kind='cubic', fill_value='extrapolate')
    return f


testFirstTable, testSecondTable = reader.readXLFR('xlfrData/test.csv')


class Forces:
    def __init__(self, first, second, freeVel, bHalf, angle):
        self.v = freeVel
        self.Cl = interp(first['y-span'], first.Cl)
        self.cord = interp(first['y-span'], first.Chord)
        self.lCd = interp(first['y-span'], first.ICd)
        self.b2 = bHalf
        self.angle = math.radians(10)

    def lift(self, x):
        L = self.Cl(x) * 0.5 * 1.225 * self.v ** 2 * self.cord(x)  # constant rho assumed, update later
        #print(np.sum(L))
        return L

    def axialForce(self):
        pass

    def shearForce(self, x):
        for
        shearDist = quad(self.lift, x, self.b2)
        return shearDist

    def torque(self):
        pass

    def bendingMoment(self, axlForce, x):
        # M, self.momentError = quad(axlForce(x), x, self.b2)
        #return M
        pass

testForces = Forces(testFirstTable, testSecondTable, 10, 25, 10)
span = np.linspace(0, 25, 10000)
trash1, teash2 = quad(testForces.lift, 5, 25)
#print(trash1)
#spanDiff = span[1:] - span[:-1]
# print(testForces.Cl(np.linspace(0,10,100)))
# plt.plot(span, testForces.cord(span))
#print(testForces.shearForce(np.array([1,2])))
#plt.plot(span, testForces.shearForce(span))
#plt.show()

fun2int = lambda x, a: np.sqrt(x+a)
intfun = lambda a: quad(fun2int, 0, 4, args=(a))[0]
vec_int = np.vectorize(intfun)
vec_int(np.linspace(0,2,5))
print(vec_int)

# print(span[1:] - span[:-1] )

class Wing:
    pass
