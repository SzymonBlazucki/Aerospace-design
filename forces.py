import numpy as np
from scipy.integrate import quad
from numpy import heaviside
import math
from constants import g, cld, zeroCl, tenCl, interp


class Forces:
    def __init__(self, CLs, freeVel, bHalf, xCentroid, engine, AoA, spanSteps, stringer, density):
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
        self.weightFunction = interp(self.span, self.weight(self.span))
        self.verticalForceFunction = interp(self.span, self.verticalForce(self.span))
        self.shearForce(self.span)
        self.bendingMoment(self.span)
        self.torque(self.span)

    def weight(self, x):
        Area = (self.chord(x) * (
                0.45 * (self.t2 + self.t4) + 0.063 * self.t1 + 0.0653 * self.t3) + self.Stringer.areaTot(x))
        return Area * self.density * g

    def lift(self, x):
        L = self.Cl(x) * self.dynamicPressure * self.chord(x)
        return L

    def drag(self, x):
        D = self.lCd(x) * self.dynamicPressure * self.chord(x)
        return D

    def verticalForce(self, x):
        return self.lift(x) * math.cos(self.AoA) \
               + self.drag(x) * math.sin(self.AoA) \
               - heaviside(-x + self.engPos, 1) * self.engWeight \
               - self.weightFunction(x)

    def shearForce(self, x):
        out = np.array(list(map(lambda i: quad(self.verticalForceFunction, i, self.b2)[0], x)))
        self.shearFunction = interp(x, out)
        return out

    def bendingMoment(self, x):  # add moment
        out = np.array(list(map(lambda i: quad(self.shearFunction, i, self.b2)[0], x)))
        self.bendingFunction = interp(x, out)
        return out

    def torque(self, x):
        def d(x):  # Distance between wb centroid and xcp
            return (self.xCp(x) - self.xCentroid) * self.chord(x)
<<<<<<< HEAD

        def h(x):  # Function of distance * shear
            return interp(x, d(x) * self.shearFunction(
                x))  # - self.moment(x)) # Cm is  not included becaus it comes from Cl

        for y in x:
            torqueDist, trash = quad(h(x), y, self.b2)
            out.append(torqueDist)
        self.twistFunction = interp(x, np.array(out))
        return np.array(out)


    def BendingStressWOylocation(self, x):
        # Divide moment by inertia
        return self.bendingMoment(x)
=======
        h = interp(x, d(x) * self.shearFunction(x))  # Function of distance * shear
        #
        # for y in x:
        #     torqueDist, trash = quad(h(x), y, self.b2)
        #     out.append(torqueDist)
        out = np.array(list(map(lambda i: quad(h, i, self.b2)[0], x)))
        self.twistFunction = interp(x, out)
        return out
>>>>>>> origin/main
