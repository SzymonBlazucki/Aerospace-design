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
    def __init__(self, CLs, freeVel, bHalf, angle, xCentroid, engine, AoA, spanSteps, stringer, density):
        self.v = freeVel
        self.Cl = interp(CLs[0]['y-span'], CLs[0].Cl + (cld - zeroCl) / (tenCl - zeroCl) * (CLs[1].Cl - CLs[0].Cl))
        self.chord = interp(CLs[0]['y-span'], CLs[0].Chord)
        self.lCd = interp(CLs[0]['y-span'], CLs[0].ICd + (cld - zeroCl) / (tenCl - zeroCl) * (CLs[1].ICd - CLs[0].ICd))
        self.xCp = interp(CLs[0]['y-span'], CLs[0].XCP + (cld - zeroCl) / (tenCl - zeroCl) * (CLs[1].XCP - CLs[0].XCP))
        self.Cm = interp(CLs[0]['y-span'],
                         CLs[0].CmAirf + (cld - zeroCl) / (tenCl - zeroCl) * (CLs[1].CmAirf - CLs[0].CmAirf))
        self.b2 = bHalf
        self.angle = math.radians(10)
        self.density = density
        self.Stringer = stringer
        self.t1 = stringer.thickness[0]
        self.t2 = stringer.thickness[1]
        self.t3 = stringer.thickness[2]
        self.t4 = stringer.thickness[3]
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


    def weight(self, x):
        Area = (self.chord(x) * (0.45*(self.t2+self.t4) + 0.063*self.t1 + 0.0653 * self.t3) + self.Stringer.areaTot(x))
        return Area * self.density * g

    def lift(self, x):
        L = self.Cl(x) * self.dynamicPressure * self.chord(x)
        return L

    def drag(self, x):
        D = self.lCd(x) * self.dynamicPressure * self.chord(x)
        return D

    def verticalForce(self, x):
        return self.lift(x) * math.cos(self.AoA) \
               +self.drag(x) * math.sin(self.AoA) \
               - heaviside(-x + self.engPos,1) * self.engWeight

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
    def __init__(self, areaStr, topStr, botStr, wbthickness):
        self.area = areaStr  # area of stringer
        self.topStr = np.concatenate((np.array([28]), topStr, np.array([28]))) # add corner stringers
        self.botStr = np.concatenate((np.array([28]), botStr, np.array([28])))
        self.totalStr = np.concatenate((self.botStr, self.topStr))
        self.thickness = wbthickness
        self.topXPos = np.linspace(0.00000001, 0.45, len(self.topStr))
        self.botXPos = np.linspace(0.00000001, 0.45, len(self.botStr))



    def numberStringers(self, ySpan):
        out = np.array([])
        for i in ySpan:
            j = np.count_nonzero(self.totalStr >= i)
            out = np.append(out, j)
        return out

    def activeStringers(self, loc, ySpan):
        for i in ySpan:
            j = loc * (loc >= i)
            if i == 0:
                out = j
            else:
                out = np.vstack([out, j])
        return np.ones_like(out)

    def topYPos(self):  # y-position of stringers in top
        return 0.016222222222 * self.topXPos + 0.0653

    def botYPos(self):  # y-position of stringers in bot
        return 0.014222222222 * self.botXPos

    def areaTot(self, x):  # dot product with area
        return self.numberStringers(x) * self.area

    def areaX(self, x):
        xActive = self.activeStringers(self.totalStr, x) * self.XPos() * self.area
        return np.sum(xActive, axis=1)

    def areaY(self, x):
        yActive = self.activeStringers(self.totalStr, x) * self.YPos() * self.area
        return np.sum(yActive, axis=1)

    def XPos(self):
        return np.concatenate((self.botXPos, self.topXPos))

    def YPos(self):
        return np.concatenate((self.botYPos(), self.topYPos()))

class Wingbox:
    def __init__(self, forces, shearMod, youngsModulus, sweep, stringer):
        self.Forces = forces
        self.E = youngsModulus
        self.G = shearMod
        self.sweep = sweep
        self.t = stringer.thickness
        self.t1 = self.t[0]
        self.t2 = self.t[1]
        self.t3 = self.t[2]
        self.t4 = self.t[3]
        self.Stringer = stringer

 # Thickness of wingbox sides in clockwise direction starting from trailing edge

    def xBarWingbox(self, x):
        xBar = (0.6 * self.Forces.chord(x) * self.t1 * 0.0662 + \
                0.225 * self.Forces.chord(x) * self.t2 * 0.45 + \
                0.225 * self.Forces.chord(x) * self.t4 * 0.45 + \
                self.Stringer.areaX(x))/ \
                (self.t1 * 0.0662 * self.Forces.chord(x) + self.t2 * 0.45 * self.Forces.chord(x) + \
                 self.t3 * 0.0653 * self.Forces.chord(x) + self.t4 * 0.45 * self.Forces.chord(x) + \
                 self.Stringer.areaTot(x))
        return xBar

    def yBarWingbox(self, x):
        yBar = (0.002615 * self.t1 * self.Forces.chord(x) + 0.0144 * self.t2 * self.Forces.chord(x) +\
                0.002132 * self.t3 * self.Forces.chord(x) + 0.03103 * self.t4 * self.Forces.chord(x) +\
               self.Stringer.areaY(x))/ \
               (0.0662 * self.t1 * self.Forces.chord(x) + 0.45 * self.t2 * self.Forces.chord(x) + \
               0.0653 * self.t3 * self.Forces.chord(x) + 0.45 * self.t4 * self.Forces.chord(x) + \
               self.Stringer.areaTot(x))
        return yBar

    def steinerTerm(self, x):
        def distance():
            stringerY = self.Stringer.activeStringers(self.Stringer.totalStr, x) * self.Stringer.YPos()
            rows, cols = stringerY.shape
            # print(stringerY)
            yCentroid = np.tile(np.array([self.yBarWingbox(x)]).transpose(), (1, cols))
            # print(yCentroid)
            length = (yCentroid - stringerY) ** 2
            # print(length)
            lengthCorrection = np.where(stringerY == 0, stringerY, length)
            # print(lengthCorrection)
            return np.sum(lengthCorrection, axis=1)
        return distance() * self.Stringer.area * self.Forces.chord(x) ** 2

    def momentInertiaX(self, x):
        Ix = (1/12 * self.t1 * 0.0662 ** 3 + self.t1 * 0.0662 * (0.0395 - self.yBarWingbox(x)) ** 2 +\
             self.t2 * 0.45 * (0.032 - self.yBarWingbox(x)) ** 2 + 1/12 * self.t2 * 0.0653 ** 3 +\
             self.t3 * 0.0653 * (0.03265 - self.yBarWingbox(x)) ** 2 +\
             self.t4 * 0.045 * (0.06895 - self.yBarWingbox(x)) ** 2)\
             * self.Forces.chord(x) ** 3 + self.steinerTerm(x)
        return Ix

    # def momentInertiaY(self, x):
    #     Iy = 2.5 * 10 ** (-5) * self.Forces.chord(x) ** 4
    #     return Iy

    def lineInteg(self, x):
        return ((0.0662 / self.t1) + (0.45 / self.t2) + (0.0653 / self.t3) + (0.45 / self.t4)) * self.Forces.chord(x)

    def torsionalStiffness(self, x):
        J = 4 * (0.0295875 * self.Forces.chord(x) ** 2) ** 2 / self.lineInteg(x)
        return J

    def twistDisplacement(self, x):
        out = []

        def func(x):
            return (self.Forces.twistFunction(x) * math.cos(self.sweep) + self.Forces.bendingFunction(x) * math.sin(
               self.sweep)) / (self.G * self.torsionalStiffness(x))

        for y in x:
            twist, trash = quad(interp(x, func(x)), 0, y)
            out.append(twist)
        return np.array(out) * 180 / math.pi  # you sure about this output?

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
        return np.array(out1) #np.array(out) * 360 / 2 * math.pi #


class Engine:  # coordinates with respect to local chord
    xPos = 9.18  # [m]
    zPos = - 0.678  # [m]
    weight = 6120 * g  # [N]
    thrust = 360430  # [N]

    def yPos(self, xCentroid, chord):
        return -xCentroid * chord - 0.3 - 0.6 * 4.77


eng = Engine()

strArea = float(input("Area of stringer in m2\n"))

wbThickness = input("Thickness of wingbox sides in meters in this order: aft, bottom, front, top\nExample input: 0.03, 0.05, 0.01, 0.03\n")
wbThickness = [float(x) for x in wbThickness.split(',')]

topStringers = input("The length of top side stringers in meters from front to back. Corner stringers are included, so no need to include them. Half span is 28 meters.\nExample input: 18, 5, 1, 7, 25\n")
if topStringers == '':
    topStringers = []
else:
    topStringers = [float(x) for x in topStringers.split(',')]



botStringers = input("The length of bot side stringers in meters from front to back. Corner stringers are included, so no need to include them. Half span is 28 meters.\nExample input: 18, 5, 1, 7, 25\n")
if botStringers == '':
    botStringers = []
else:
    botStringers = [float(x) for x in botStringers.split(',')]


strng = Stringer(strArea, np.array(topStringers), np.array(botStringers), wbthickness=wbThickness)
# print(strng.numberStringers(np.array([20, 16, 10, 8, 8]), np.linspace(5,10,10)))

velocity = input("Do you want to change the velocity in m/s? To use default value, press enter.\nDefault value = 250 m/s which is Mach 0.84 at cruising altitude\n")
if velocity == '':
    velocity = 250
else:
    velocity = float(velocity)

angle = input("Do you want to change the angle of attack in deg? To use default value, press enter.\nDefault value = 10 deg\n")
if angle == '':
    angle = 10
else:
    angle = float(angle)

testForces = Forces([zeroAngleFirstTable, tenAngleFirstTable],
                    freeVel=velocity, bHalf=28, angle=angle,
                    AoA=math.asin((cld - zeroCl) / (tenCl - zeroCl) * math.sin(math.radians(10))), xCentroid=0.3755, #might've changed
                    engine=eng, spanSteps=101, stringer=strng, density=2700)
wb = Wingbox(forces=testForces, shearMod=(26 * 10 ** 9), youngsModulus=(68.9 * 10 ** 9),
             stringer=strng, sweep=27)


plotter(testForces.span, testForces.lift, 'Span [m]', 'Lift per span [N/m]')
# plotter(testForces.span, testForces.weight, 'Span [m]', 'Weight per span [N/m]')
# plotter(testForces.span, testForces.drag, 'Span [m]', 'Drag per span [N/m]')
# plotter(testForces.span, testForces.verticalForce, 'Span [m]', 'Vertical force per span [N]')
plotter(testForces.span, testForces.shearForce, 'Span [m]', 'Shear Diagram [N]')

plotter(testForces.span, wb.momentInertiaX, 'Span [m]', 'Moment of Inertia [m^4]')
plotter(testForces.span, testForces.bendingMoment, 'Span [m]', 'Bending Moment [N*m]')
plotter(testForces.span, wb.bendingDisplacement, 'Span [m]', 'Horizontal Displacement [m]')


plotter(testForces.span, wb.torsionalStiffness, 'Span [m]', 'Torsional Stiffness [m^4]')
plotter(testForces.span, testForces.torque, 'Span [m]', 'Torque [N*m]')
plotter(testForces.span, wb.twistDisplacement, 'Span [m]', 'Twist Displacement [deg]')


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
