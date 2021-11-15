# Change span to negative. Proposition: mirror all the graphs for a lazy solution
# Shear and bending in the other direction (drag)
# Include Cm (and Cd) in torque
# Set a coordinate system and possibly a sketch of what is what
# Using Nx, Ny, Nz from xflr file may have been easier, because we won't have to deal with angles or anything else
# in the csv file, changed the name of the column from CmAirf@chord/4 to CmAirf coz python didnt like it

import math, reader
import matplotlib.pyplot as plt
from scipy import interpolate, signal
from scipy.integrate import quad
import numpy as np
from numpy import heaviside

g = 9.80665 #[m/s^2] gravity acceleration

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
    def __init__(self, first, second, freeVel, bHalf, angle, xCentroid, engine):
        self.v = freeVel
        self.Cl = interp(first['y-span'], first.Cl)
        self.chord = interp(first['y-span'], first.Chord)
        self.lCd = interp(first['y-span'], first.ICd)
        self.xCp = interp(first['y-span'], first.XCP)
        self.Cm = interp(first['y-span'], first.CmAirf)
        self.b2 = bHalf
        self.angle = math.radians(10)
        self.shearFunction = None
        self.xCentroid = xCentroid # x location of wb centroid in chords
        self.dynamicPressure = 1/2 * 1.225 * self.v ** 2
        self.shearForceIntervals = engine.xPos

    def lift(self, x):
        L = self.Cl(x) * self.dynamicPressure * self.chord(x)  # constant rho assumed, update later
        #L = np.ones_like(x) #To get a straight lift dist.
        #print(np.sum(L))
        return L

    # def moment(self, x):
    #     CmCentroid = self.Cm(x) + (self.xCentroid - 1/4) * self.Cl(x) # Cm at wb centroid
    #     M = CmCentroid * self.dynamicPressure * self.chord(x) ** 2
    #     return M

    def axialForce(self):
        pass

    def shearForce(self, x):
        out = []
        for y in x:

            shearDist, trash = quad(self.lift + heaviside(,1), y, self.b2)
            # if y < 15: # Including the engine
            #     shearDist -= 5000*9.81
            out.append(shearDist)

        self.shearFunction = interp(x, np.array(out))
        tst = interpolate.UnivariateSpline(x, self.lift(x), s=0)
        print(tst.integral(1,self.b2))
        print(self.shearFunction(1))
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
            return (self.xCp(x) - self.xCentroid) * self.chord(x)
        def h(x): # Function of distance * shear
            return interp(x, d(x) * self.shearFunction(x)) #- self.moment(x)) # Cm is  not included becaus it comes from Cl
        for y in x:
            torqueDist, trash = quad(h(x), y, self.b2)
            out.append(torqueDist)
        return np.array(out)


testForces = Forces(testFirstTable, testSecondTable,
                    freeVel=10, bHalf=28, angle=10,
                    xCentroid=0.3755)

span = np.linspace(0, 25, 101)

# plt.plot(span, testForces.lift(span))
# plt.show()
# plt.plot(span, testForces.shearForce(span))
# plt.show()
# plt.plot(span, testForces.bendingMoment(span))
# plt.show()
#
plotter(span, testForces.lift(span), 'Span [m]', 'Lift per span [N/m]')
plotter(span, testForces.shearForce(span), 'Span [m]', 'Shear force [N]')
plotter(span, testForces.bendingMoment(span), 'Span [m]', 'Bending moment [N*m]')
plotter(span, testForces.torque(span), 'Span [m]', 'Torque [N*m]')
#plotter(span, testForces.moment(span), 'Span [m]', 'Cm Moment [N*m]')

class Wing:
    pass

class Engine: # coordinates with respect to local chord
    def __init__(self, Forces):
        xPos = 9.18 # [m]
        yPos = - (Forces.xCentroid * Forces.chord(xPos) - 0.3 - 0.6 * 4.77)
        zPos = - 0.678 # [m]
        weight = 6120 * g # [N]
        thrust = 360430 # [N]
