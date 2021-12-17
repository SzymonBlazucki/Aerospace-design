import numpy as np
from scipy.integrate import quad
import math
from constants import interp, E, G, factor


class Wingbox:
    def __init__(self, forces, sweep, stringer, ribs, rib_length, rib_pitch):
        self.Forces = forces
        self.sweep = sweep
        self.t = stringer.thickness
        self.t1 = self.t[0]
        self.t2 = self.t[1]
        self.t3 = self.t[2]
        self.t4 = self.t[3]
        self.Stringer = stringer
        self.ribs = ribs
        self.rib_pitch = rib_pitch
        self.rib_length = rib_length
    # Thickness of wingbox sides in clockwise direction starting from trailing edge

    def enclosedArea(self, x):
        return (0.6-0.15) * (0.0662 + 0.0653) * factor / 2 * self.Forces.chord(x) ** 2



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
        return (yBar - 0.0154) * factor

    def strYDistance(self, x):
        # Get the y locations of the stringer
        stringerY = self.Stringer.activeStringers(self.Stringer.totalStr, x) * self.Stringer.YPos()
        # print(f"YPOS{self.Stringer.YPos()}")
        rows, cols = stringerY.shape
        yCentroid = np.tile(np.array([self.yBarWingbox(x)]).transpose(), (1, cols))

        return (yCentroid, stringerY)

    def steinerTerm(self, x):
        def distance():
            # stringerY = self.Stringer.activeStringers(self.Stringer.totalStr, x) * self.Stringer.YPos()
            # rows, cols = stringerY.shape
            # # print(stringerY)
            # yCentroid = np.tile(np.array([self.yBarWingbox(x)]).transpose(), (1, cols))
            # # print(yCentroid)
            yCentroid, stringerY = self.strYDistance(x)

            length = (yCentroid - stringerY) ** 2
            # print(length)
            lengthCorrection = np.where(stringerY == 0, stringerY, length) * self.Stringer.areaArr

            return np.sum(lengthCorrection, axis=1)

        return distance() * self.Forces.chord(x) ** 2

    def momentInertiaX(self, x):
        Ix = (1 / 12 * self.t1 * (0.0662 * factor) ** 3 + self.t1 * (0.0662 * factor) * (0.0395 * factor - self.yBarWingbox(x)) ** 2 +
              1 / 12 * self.t3 * (0.0653 * factor) ** 3 + self.t3 * (0.0653 * factor) * (0.03265 * factor - self.yBarWingbox(x)) ** 2  +
              self.t2 * 0.45 * (0.00711 * factor - self.yBarWingbox(x)) ** 2 +
              self.t4 * 0.45 * (0.06895 * factor - self.yBarWingbox(x)) ** 2) \
             * self.Forces.chord(x) ** 3 + self.steinerTerm(x)
        return Ix

    # def momentInertiaY(self, x):
    #     Iy = 2.5 * 10 ** (-5) * self.Forces.chord(x) ** 4
    #     return Iy

    def lineInteg(self, x):
        return ((0.0662 * factor / self.t1) + (0.45 / self.t2) + (0.0653 * factor / self.t3) + (0.45 / self.t4)) * self.Forces.chord(x)

    def torsionalStiffness(self, x):
        J = 4 * self.enclosedArea(x) ** 2 / self.lineInteg(x)
        return J


    def twistDisplacement(self, x):
        out = []

        def func(x):
            return (self.Forces.twistFunction(x) * math.cos(self.sweep) + self.Forces.bendingFunction(x) * math.sin(
                self.sweep)) / (G * self.torsionalStiffness(x))

        for y in x:
            twist, trash = quad(interp(x, func(x)), 0, y)
            out.append(twist)
        # out = np.array(list(map(lambda i: quad(func, i, self.Forces.b2)[0], x)))
        return np.array(out) * 180 / math.pi  # you sure about this output?

    def bendingDisplacement(self, x):
        out = []

        def funcTheta(x):
            return -(- self.Forces.twistFunction(x) * math.sin(self.sweep) + self.Forces.bendingFunction(x) * math.cos(
                self.sweep)) / (E * self.momentInertiaX(x))  # check please nto sure if I want x or y

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

