# Change span to negative. Proposition: mirror all the graphs for a lazy solution
# Shear and bending in the other direction (drag)
# Include Cm (and Cd) in torque
# Set a coordinate system and possibly a sketch of what is what
# Using Nx, Ny, Nz from xflr file may have been easier, because we won't have to deal with angles or anything else
# in the csv file, changed the name of the column from CmAirf@chord/4 to CmAirf coz python didnt like it

import math, reader
from string import punctuation
import matplotlib.pyplot as plt
from scipy import interpolate, signal
from scipy.integrate import quad
import numpy as np
from numpy import heaviside

g = 9.80665 #[m/s^2] gravity acceleration

def interp(x, y):
    f = interpolate.interp1d(x, y, kind='cubic', fill_value='extrapolate')
    return f

def plotter(plot, x, y, xLabel, yLabel):
        plt.plot(x, y)
        plt.title(xLabel + ' vs ' + yLabel)
        plt.xlabel(xLabel)
        plt.ylabel(yLabel)
        if plot:
            plt.show()

testFirstTable, testSecondTable = reader.readXLFR('xlfrData/alpha0.csv')


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
        self.bendingFunction = None
        self.twistFunction = None
        self.xCentroid = xCentroid # x location of wb centroid in chords
        self.dynamicPressure = 1/2 * 1.225 * self.v ** 2
        self.engPos = engine.xPos
        self.engWeight = engine.weight

    def lift(self, x):
        L = self.Cl(x) * self.dynamicPressure * self.chord(x)  # constant rho assumed, update later
        #L = np.ones_like(x) #To get a straight lift dist.
        #print(np.sum(L))
        return L

    def axialForce(self):
        pass

    def verticalForce(self, x):
        return self.lift(x) - heaviside(-x + self.engPos, 1) * self.engWeight

    def shearForce(self, x):
        out = []
        for y in x:

            shearDist, trash = quad(self.verticalForce, y, self.b2)
            # if y < 15: # Including the engine
            #     shearDist -= 5000*9.81
            out.append(shearDist)

        self.shearFunction = interp(x, np.array(out))
        tst = interpolate.UnivariateSpline(x, self.lift(x), s=0)
        # print(tst.integral(1,self.b2))
        # print(self.shearFunction(1))
        return np.array(out)



    def bendingMoment(self, x):
        if self.shearFunction == None:
            self.shearForce(x)
        out = []
        for y in x:
            shearDist, trash = quad(self.shearFunction, y, self.b2)
            out.append(shearDist)
        self.bendingFunction = interp(x, np.array(out))
        return np.array(out)

    def torque(self, x):
        out = []
        if self.shearFunction == None:
            self.shearForce(x)
        def d(x): # Distance between wb centroid and xcp
            return (self.xCp(x) - self.xCentroid) * self.chord(x)
        def h(x): # Function of distance * shear
            return interp(x, d(x) * self.shearFunction(x)) #- self.moment(x)) # Cm is  not included becaus it comes from Cl
        for y in x:
            torqueDist, trash = quad(h(x), y, self.b2)
            out.append(torqueDist)
        self.twistFunction = interp(x, np.array(out))
        return np.array(out)


class Wing:
    pass


class Stringer:
    def __init__(self, areaStr, topStr, botStr):
        self.area = areaStr # area of stringer

        self.topStr = topStr # count of top stringers
        self.botStr = botStr # count of bot stringers

        self.topXLoc = np.linspace(0, 0.45, topStr)
        self.botXLoc = np.linspace(0, 0.45, botStr)

    def areaDot(self, x): # dot product with area
        return np.dot((np.ones_like(x) * self.area), x)

    def topYPos(self, x): # y-position of stringers in top
        return 0.016222222222 * x + 0.0653
    def botYPos(self, x): # y-position of stringers in bot
        return 0.014222222222 * x


    def xBarStr(self): # x-centroid of stringers from bot-left corner of wingbox which is 0.225
        return (self.areaDot(self.topXLoc) + self.areaDot(self.botXLoc)) / (self.area * (self.topStr + self.botStr))

    def yBarStr(self):
        return (self.areaDot(self.topYPos(self.topXLoc)) + self.areaDot(self.botYPos(self.botXLoc))) / (self.area * (self.topStr + self.botStr))





class Wingbox:
    def __init__(self, thickness, forces, shearMod, youngsModulus, Stringer):
        self.t = thickness
        self.Forces = forces
        self.E = youngsModulus
        self.G = shearMod
 # Thickness of wingbox sides in clockwise direction starting from trailing edge

    def xBarWb(self):




    def momentInertiaX(self, x):
        Ix = 1.18 * 10 ** (-5) * self.Forces.chord(x) ** 4
        return Ix
    def momentInertiaY(self, x):
        Iy = 2.5 * 10 ** (-5) * self.Forces.chord(x) ** 4
        return Iy

    def lineInteg(self, x):
        return 1.031604716 * self.Forces.chord(x)

    def torsionalStiffness(self, x):
        J = (4 * (0.0295875 * self.Forces.chord(x) ** 2) ** 2) / (self.lineInteg(x) / self.t)
        return J

    def twistDisplacement(self, x):
        out = []
        def func(x):
            return self.Forces.twistFunction(x)/(self.G * self.torsionalStiffness(x))
        for y in x:
            twist, trash = quad(interp(x, func(x)), 0, y)
            out.append(twist)
        return np.array(out)  # you sure about this output?

    def bendingDisplacement(self, x):
        out = []

        def funcTheta(x):
            return -self.Forces.bendingFunction(x)/(self.E * self.momentInertiaY(x)) # check please nto sure if I want x or y
        for y in x:
            twist, trash = quad(interp(x, funcTheta(x)), 0, y)
            out.append(twist)
        thetaFun = interp(x, np.array(out))
        out1 = []
        for y in x:
            twist, trash = quad(interp(x, thetaFun(x)), 0, y)
            out1.append(twist)
        return [np.array(out)*360/2*math.pi, np.array(out1)]




class Engine: # coordinates with respect to local chord
    xPos = 9.18 # [m]
    zPos = - 0.678 # [m]
    weight = 6120 * g # [N]
    thrust = 360430 # [N]
    def yPos(self, xCentroid, chord):
        return (-xCentroid * chord - 0.3 - 0.6 * 4.77)


eng = Engine()
stringer = Stringer(0.0000006, 0, 2)
testForces = Forces(testFirstTable, testSecondTable,
                    freeVel=300, bHalf=28, angle=10,
                    xCentroid=0.3755, engine=eng)
wb = Wingbox(thickness=0.001, forces=testForces, shearMod=(26 * 10 ** 9),
             youngsModulus=(68.9 * 10**9), Stringer=Stringer)

print(stringer.xBar())
print(stringer.yBar())
span = np.linspace(0, 25, 101)

plotter(False, span, testForces.verticalForce(span), 'Span [m]', 'Vertical force per span [N/m]')
plotter(False, span, testForces.lift(span), 'Span [m]', 'Lift per span [N/m]')
plotter(False, span, testForces.shearForce(span), 'Span [m]', 'Shear force [N]')
plotter(False, span, testForces.bendingMoment(span), 'Span [m]', 'Bending moment [N*m]')
plt.show()
plotter(True, span, testForces.torque(span), 'Span [m]', 'Torque [N*m]')
plotter(True, span, wb.torsionalStiffness(span), 'Span [m]', 'Torsional Stiffness [m^4]')
plotter(True, span, wb.twistDisplacement(span), 'Span [m]', 'twist displacement [rad]')
plotter(True, span, wb.bendingDisplacement(span)[1], 'Span [m]', 'horizontal displacement [m]')