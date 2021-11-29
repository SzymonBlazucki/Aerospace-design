import numpy as np
from scipy.integrate import quad
import math
from constants import interp


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
        xBar = (0.6 * self.Forces.chord(x) * self.t1 * 0.0662 +
                0.225 * self.Forces.chord(x) * self.t2 * 0.45 +
                0.225 * self.Forces.chord(x) * self.t4 * 0.45 +
                self.Stringer.areaX(x)) / \
               (self.t1 * 0.0662 * self.Forces.chord(x) + self.t2 * 0.45 * self.Forces.chord(x) +
                self.t3 * 0.0653 * self.Forces.chord(x) + self.t4 * 0.45 * self.Forces.chord(x) +
                self.Stringer.areaTot(x))
        return xBar

    def yBarWingbox(self, x):
        yBar = (0.002615 * self.t1 * self.Forces.chord(x) + 0.0144 * self.t2 * self.Forces.chord(x) +
                0.002132 * self.t3 * self.Forces.chord(x) + 0.03103 * self.t4 * self.Forces.chord(x) +
                self.Stringer.areaY(x)) / \
               (0.0662 * self.t1 * self.Forces.chord(x) + 0.45 * self.t2 * self.Forces.chord(x) +
                0.0653 * self.t3 * self.Forces.chord(x) + 0.45 * self.t4 * self.Forces.chord(x) +
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
        Ix = (1 / 12 * self.t1 * 0.0662 ** 3 + self.t1 * 0.0662 * (0.0395 - self.yBarWingbox(x)) ** 2 +
              self.t2 * 0.45 * (0.032 - self.yBarWingbox(x)) ** 2 + 1 / 12 * self.t2 * 0.0653 ** 3 +
              self.t3 * 0.0653 * (0.03265 - self.yBarWingbox(x)) ** 2 +
              self.t4 * 0.045 * (0.06895 - self.yBarWingbox(x)) ** 2) \
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

    # noinspection PyTupleAssignmentBalance
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
            # noinspection PyTupleAssignmentBalance
            twist, trash = quad(interp(x, thetaFun(x)), 0, y)
            out1.append(twist)
        return np.array(out1)  # np.array(out) * 360 / 2 * math.pi #
