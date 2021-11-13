# Change span to negative. Proposition: mirror all the graphs for a lazy solution
# Shear and bending in the other direction (drag)
# Include Cm (and Cd) in torque
# Set a coordinate system and possibly a sketch of what is what



import math, reader
import matplotlib.pyplot as plt
from scipy import interpolate, signal
from scipy.integrate import quad
import numpy as np


def interp(x, y):
    f = interpolate.interp1d(x, y, kind='cubic', fill_value='extrapolate')
    return f

def plotter(x, y, xLabel, yLabel):
        plt.plot(x, y)
        plt.title(xLabel + ' vs ' + yLabel)
        plt.xlabel(xLabel)
        plt.ylabel(yLabel)
        plt.show()

testFirstTable, testSecondTable = reader.readXLFR('xlfrData/test.csv')


class Forces:
    def __init__(self, first, second, freeVel, bHalf, angle):
        self.v = freeVel
        self.Cl = interp(first['y-span'], first.Cl)
        self.chord = interp(first['y-span'], first.Chord)
        self.lCd = interp(first['y-span'], first.ICd)
        self.xCp = interp(first['y-span'], first.XCP)
        self.b2 = bHalf
        self.angle = math.radians(10)
        self.shearFunction = None

    def lift(self, x):
        L = self.Cl(x) * 0.5 * 1.225 * self.v ** 2 * self.chord(x)  # constant rho assumed, update later
        #L = np.ones_like(x) #To get a straight lift dist.
        # print(np.sum(L))
        return L

    def axialForce(self):
        pass

    def shearForce(self, x):
        out = []
        for y in x:
            shearDist, trash = quad(self.lift, y, self.b2)
            # if y < 15: # Including the engine
            #     shearDist -= 5000*9.81
            out.append(shearDist)

        self.shearFunction = interp(x, np.array(out))
        return np.array(out)

    def bendingMoment(self, x):
        if self.shearFunction == None:
            self.shearForce(x)
        out = []
        for y in x:
            shearDist, trash = quad(self.shearFunction, y, self.b2)
            out.append(shearDist)
        # self.shearFunction = interp(x, np.array(out))
        return np.array(out)

    def torque(self, x):
        out = []
        def d(x): # Distance between wb centroid and xcp
            return self.xCp(x) - 0.3755 * self.chord(x)
        def h(x): # Function of distance * shear
            return interp(x, d(x) * self.shearFunction(x))
        for y in x:
            torqueDist, trash = quad(h(x), y, self.b2)
            out.append(torqueDist)

        return np.array(out)


testForces = Forces(testFirstTable, testSecondTable, 10, 25, 10)
span = np.linspace(0, 25, 101)

# plt.plot(span, testForces.lift(span))
# plt.show()
# plt.plot(span, testForces.shearForce(span))
# plt.show()
# plt.plot(span, testForces.bendingMoment(span))
# plt.show()

plotter(span, testForces.lift(span), 'Span [m]', 'Lift per span [N/m]')
plotter(span, testForces.shearForce(span), 'Span [m]', 'Shear force [N]')
plotter(span, testForces.bendingMoment(span), 'Span [m]', 'Bending moment [N*m]')
plotter(span, testForces.torque(span), 'Span [m]', 'Torque [N*m]')


class Wing:
    pass
