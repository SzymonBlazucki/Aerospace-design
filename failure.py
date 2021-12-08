import math
from constants import E, K, v
import numpy as np


class Failure:
    def __init__(self, forces, wingbox, stringer):
        self.Forces = forces
        self.Wingbox = wingbox
        self.Stringer = stringer

    def stressShear(self, x):
        # return [self.Forces.torque(x) / (2 * self.Wingbox.enclosedArea(x) * self.Stringer.thickness[0]),  # thickness aft spar
        #        self.Forces.torque(x) / (2 * self.Wingbox.enclosedArea(x) * self.Stringer.thickness[2])]  # thickness front spar
        return self.Forces.torque(x) / (2 * self.Wingbox.enclosedArea(x) * self.Stringer.thickness[
            0])  # Aft spar is the critical, more stress

    # Stringer buckling at the root (root has the critical stress due to bending)
    def stressBending(self, x):
        # calculate the stress due to torsion without y location at the root
        constbending = self.Forces.bendingMoment(x)[0] / self.Wingbox.momentInertiaX(x)[0]

        # get the y location of the stringers w.r.t the neutral axis and convert it to [m]
        yCentroid, stringerY = self.Wingbox.strYDistance(x)
        yDistance = (stringerY[0] - yCentroid[0]) * self.Forces.chord(x)[0]

        # output result for stress at all stringers at the root
        out = constbending * yDistance

        return out

    # Create the item for the stress due to bending
    def stressBendingGraph(self, x):
        # calculate the stress due to bending moment without y location as a function of span
        constbending = self.Forces.bendingMoment(x) / self.Wingbox.momentInertiaX(x)
        return constbending

    # return the critical column buckling stress based on inputs
    def columnBuckling(self, x):
        # Create boolean array based on stress type (compression = 1, tensile =0)
        cforceboolean = np.where(self.stressBending(x) > 0, 0, 1)
        out = cforceboolean * (math.pi ** 2 * K * E * self.Stringer.strIxx) / \
              (self.Stringer.totalStr ** 2 * self.Stringer.areaArr)
        return out

    # Alternative to columnBuckling, returns required length based on the critical stress at the root
    def columBucklingLenght(self, x):
        # Create boolean array based on stress type (compression = 1, tensile =0)
        cforceboolean = np.where(self.stressBending(x) > 0, 0, 1)
        out = np.sqrt(cforceboolean * (math.pi ** 2 * K * E * self.Stringer.strIxx) / \
                      (self.stressBending(x) * self.Stringer.areaArr))
        return out

    def ab(self, x):
        rb = self.Wingbox.ribs
        out = np.array(list(map(lambda i: max(rb[rb < i]), x)))

        return (x - out)

    def tb(self, x):  # to be modified, for now good enough
        return self.Wingbox.t / (0.45 * self.forces.chord(x))

    def skinBuckling(self, x, k=7.8):  # please confirm what value of K I should use
        allStress = math.pi ** 2 * k * E * self.tb(x) ** 2 / (12 * (1 - v ** 2))  # check that
        pass

    def webBuckling(self, x):
        criticalShear = math.pi ** 2 * k_s * E / 12 / (1 - v ** 2) * (t / b)

    def marginBendingIndex(self,x):
        out = - self.stressBending(x) / self.columnBuckling(x)
        critical_point = np.where(out > 0, out, np.inf).argmin()
        return critical_point

    # Stringer buckling at the root (root has the critical stress due to bending)
    def stressBendingmaxspan(self, x):
        # find the index of the critical stringer
        index = self.marginBendingIndex(x)
        print(index)
        # calculate the stress due to torsion without y location at the root
        constbending = self.Forces.bendingMoment(x) / self.Wingbox.momentInertiaX(x)

        # get the y location of the stringers w.r.t the neutral axis and convert it to [m]
        yCentroid, stringerY = self.Wingbox.strYDistance(x)
        yDistance = (stringerY[index][:] - yCentroid[index][:])
        print(yDistance)
        yDistance2 = yDistance * self.Forces.chord(x)

        # output result for stress at all stringers at the root
        out = constbending * yDistance2

        return out

# test v3