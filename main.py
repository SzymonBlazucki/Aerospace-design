# Change span to negative. Proposition: mirror all the graphs for a lazy solution
# Shear and bending in the other direction (drag)
# Include Cm (and Cd) in torque
# Set a coordinate system and possibly a sketch of what is what
# Using Nx, Ny, Nz from xflr file may have been easier, because we won't have to deal with angles or anything else
# in the csv file, changed the name of the column from CmAirf@chord/4 to CmAirf coz python didnt like it

# cl cruise = 0.6767

import math, reader
import matplotlib.pyplot as plt
from scipy import interpolate
from scipy.integrate import quad
import numpy as np
from numpy import heaviside

g = 9.80665  # [m/s^2] gravity acceleration
cld = 0.6767


def interp(x, y):
    f = interpolate.interp1d(x, y, kind='cubic', fill_value='extrapolate')
    return f


def plotter(x, y, xLabel, yLabel):
    plt.plot(x, y(x))
    plt.title(xLabel + ' vs ' + yLabel)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.show()


zeroAngleFirstTable, zeroAngleSecondTable, zeroCl = reader.readXLFR('xlfrData/alpha0.csv')
tenAngleFirstTable, tenAngleSecondTable, tenCl = reader.readXLFR('xlfrData/alpha10.csv')


class Forces:
    def __init__(self, CLs, freeVel, bHalf, angle, xCentroid, engine, AoA, spanSteps):
        self.v = freeVel
        self.Cl = interp(CLs[0]['y-span'], CLs[0].Cl + (cld - zeroCl) / (tenCl - zeroCl) * (CLs[1].Cl - CLs[0].Cl))
        self.chord = interp(CLs[0]['y-span'], CLs[0].Chord)
        self.lCd = interp(CLs[0]['y-span'], CLs[0].ICd + (cld - zeroCl) / (tenCl - zeroCl) * (CLs[1].ICd - CLs[0].ICd))
        self.xCp = interp(CLs[0]['y-span'], CLs[0].XCP + (cld - zeroCl) / (tenCl - zeroCl) * (CLs[1].XCP - CLs[0].XCP))
        self.Cm = interp(CLs[0]['y-span'],
                         CLs[0].CmAirf + (cld - zeroCl) / (tenCl - zeroCl) * (CLs[1].CmAirf - CLs[0].CmAirf))
        self.b2 = bHalf
        self.angle = math.radians(10)
        self.shearFunction = None
        self.bendingFunction = None
        self.twistFunction = None
        self.xCentroid = xCentroid  # x location of wb centroid in chords
        self.dynamicPressure = 1 / 2 * 1.225 * self.v ** 2  # constant rho assumed, update later
        self.engPos = engine.xPos
        self.engWeight = engine.weight
        self.AoA = AoA  # already in radians
        self.span = np.linspace(0, bHalf, spanSteps)
        self.shearForce(self.span)
        self.bendingMoment(self.span)
        self.torque(self.span)

    def lift(self, x):
        L = self.Cl(x) * self.dynamicPressure * self.chord(x)
        return L

    def drag(self, x):
        D = self.lCd(x) * self.dynamicPressure * self.chord(x)
        return D

    def verticalForce(self, x):
        return self.lift(x) * math.cos(self.AoA) + self.drag(x) * math.sin(self.AoA) - heaviside(-x + self.engPos,
                                                                                                 1) * self.engWeight

    def shearForce(self, x):
        out = []
        for y in x:
            shearDist, trash = quad(self.verticalForce, y, self.b2)
            out.append(shearDist)

        self.shearFunction = interp(x, np.array(out))
        tst = interpolate.UnivariateSpline(x, self.lift(x), s=0)
        return np.array(out)

    def bendingMoment(self, x):  # add moment
        if self.shearFunction is None:
            self.shearForce(x)
        out = []
        for y in x:
            shearDist, trash = quad(self.shearFunction, y, self.b2)
            out.append(shearDist)
        self.bendingFunction = interp(x, np.array(out))
        return np.array(out)

    def torque(self, x):
        out = []
        if self.shearFunction is None:
            self.shearForce(x)

        def d(x):  # Distance between wb centroid and xcp
            return (self.xCp(x) - self.xCentroid) * self.chord(x)

        def h(x):  # Function of distance * shear
            return interp(x, d(x) * self.shearFunction(
                x))  # - self.moment(x)) # Cm is  not included becaus it comes from Cl

        for y in x:
            torqueDist, trash = quad(h(x), y, self.b2)
            out.append(torqueDist)
        self.twistFunction = interp(x, np.array(out))
        return np.array(out)


class Wing:
    pass


class Stringer:
    def __init__(self, areaStr, topStr, botStr):
        self.area = areaStr  # area of stringer

        self.topStr = topStr  # count of top stringers
        self.botStr = botStr  # count of bot stringers

        self.topXLoc = np.linspace(0, 0.45, topStr)
        self.botXLoc = np.linspace(0, 0.45, botStr)

    def areaDot(self, x):  # dot product with area
        return np.dot((np.ones_like(x) * self.area), x)

    def topYPos(self, x):  # y-position of stringers in top
        return 0.016222222222 * x + 0.0653

    def botYPos(self, x):  # y-position of stringers in bot
        return 0.014222222222 * x

    def xBarStr(self):  # x-centroid of stringers from bot-left corner of wingbox which is 0.225
        return (self.areaDot(self.topXLoc) + self.areaDot(self.botXLoc)) / (self.area * (self.topStr + self.botStr))

    def yBarStr(self):
        return (self.areaDot(self.topYPos(self.topXLoc)) + self.areaDot(self.botYPos(self.botXLoc))) / (
                self.area * (self.topStr + self.botStr))


class Wingbox:
    def __init__(self, thickness, forces, shearMod, youngsModulus, sweep, Stringer):
        self.t = thickness
        self.Forces = forces
        self.E = youngsModulus
        self.G = shearMod
        self.sweep = sweep

    # Thickness of wingbox sides in clockwise direction starting from trailing edge

    def xBarWb(self):
        pass

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
            return (self.Forces.twistFunction(x) * math.cos(self.sweep) + self.Forces.bendingFunction(x) * math.sin(
                self.sweep)) / (self.G * self.torsionalStiffness(x))

        for y in x:
            twist, trash = quad(interp(x, func(x)), 0, y)
            out.append(twist)
        return np.array(out)  # you sure about this output?

    def bendingDisplacement(self, x):
        out = []

        def funcTheta(x):
            return -(- self.Forces.twistFunction(x) * math.sin(self.sweep) + self.Forces.bendingFunction(x) * math.cos(
                self.sweep)) / (self.E * self.momentInertiaX(x))  # check please nto sure if I want x or y

        for y in x:
            twist, trash = quad(interp(x, funcTheta(x)), 0, y)
            out.append(twist)
        thetaFun = interp(x, np.array(out))
        out1 = []
        for y in x:
            twist, trash = quad(interp(x, thetaFun(x)), 0, y)
            out1.append(twist)
        return [np.array(out) * 360 / 2 * math.pi, np.array(out1)]


class Engine:  # coordinates with respect to local chord
    xPos = 9.18  # [m]
    zPos = - 0.678  # [m]
    weight = 6120 * g  # [N]
    thrust = 360430  # [N]

    def yPos(self, xCentroid, chord):
        return -xCentroid * chord - 0.3 - 0.6 * 4.77


eng = Engine()
stringer = Stringer(0.0000006, 0, 2)
testForces = Forces([zeroAngleFirstTable, tenAngleFirstTable],
                    freeVel=300, bHalf=28, angle=10,
                    AoA=math.asin((cld - zeroCl) / (tenCl - zeroCl) * math.sin(math.radians(10))), xCentroid=0.3755,
                    engine=eng, spanSteps=101)
wb = Wingbox(thickness=0.001, forces=testForces, shearMod=(26 * 10 ** 9), youngsModulus=(68.9 * 10 ** 9),
             Stringer=Stringer, sweep=27)

plotter(testForces.span, testForces.bendingMoment, 'Span [m]', 'Torque [N*m]')
# plotter(False, span, testForces.verticalForce(span), 'Span [m]', 'Vertical force per span [N/m]')
# plotter(False, span, testForces.lift(span), 'Span [m]', 'Lift per span [N/m]')
# plotter(False, span, testForces.shearForce(span), 'Span [m]', 'Shear force [N]')
# plotter(False, span, testForces.bendingMoment(span), 'Span [m]', 'Bending moment [N*m]')
# plt.show()
# plotter(True, span, testForces.torque(span), 'Span [m]', 'Torque [N*m]')
# plotter(True, span, wb.torsionalStiffness(span), 'Span [m]', 'Torsional Stiffness [m^4]')
# plotter(True, span, wb.twistDisplacement(span), 'Span [m]', 'horizontal displacement [m]')
# plotter(False, span, wb.bendingDisplacement(span)[1], 'Span [m]', 'horizontal displacement [m]')
# plotter(True, span, wb.twistDisplacement(span), 'Span [m]', 'twist displacement [rad]')
# plotter(True, span, wb.bendingDisplacement(span)[1], 'Span [m]', 'horizontal displacement [m]')
