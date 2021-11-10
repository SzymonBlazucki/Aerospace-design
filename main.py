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
        self.shearFunction = None

    def lift(self, x):
        L = self.Cl(x) * 0.5 * 1.225 * self.v ** 2 * self.cord(x)  # constant rho assumed, update later
        #print(np.sum(L))
        return L

    def axialForce(self):
        pass

    def shearForce(self, x):
        out = []
        for y in x:
            shearDist, trash = quad(self.lift, y, self.b2)
            out.append(shearDist)
        self.shearFunction = interp(x, np.array(out))
        return np.array(out)

    def torque(self):
        pass

    def bendingMoment(self, x):
        if self.shearFunction == None:
            self.shearForce(x)
        out = []
        for y in x:
            shearDist, trash = quad(self.shearFunction, y, self.b2)
            out.append(shearDist)
        #self.shearFunction = interp(x, np.array(out))
        return np.array(out)

testForces = Forces(testFirstTable, testSecondTable, 10, 25, 10)
span = np.linspace(0, 25, 100)

plt.plot(span, testForces.lift(span))
plt.show()
plt.plot(span, testForces.shearForce(span))
plt.show()
plt.plot(span, testForces.bendingMoment(span))
plt.show()


class Wing:
    pass
