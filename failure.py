import math
from constants import E, K
import numpy as np

class Failure:
    def __init__(self, forces, wingbox, stringer):
        self.Forces = forces
        self.Wingbox = wingbox
        self.Stringer = stringer

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
    def columnBuckling(self):
        out = (math.pi**2 * self.K * self.E * self.Stringer.strIxx) / \
              (self.Stringer.totalStr**2 * self.Stringer.areaArr)
        return out

    # Alternative to columnBuckling, returns required length based on the critical stress at the root
    def columBucklingLenght(self, x):
        # Create boolean array based on stress type (compression = 1, tensile =0)
        cforceboolean = np.where(self.stressBending(x) < 0, 0, 1)
        out = np.sqrt(cforceboolean * (math.pi**2 * self.K * self.E * self.Stringer.strIxx) / \
              (self.stressBending(x) * self.Stringer.areaArr))
        return out


    def webBuckling(self, x):
        criticalShear = math.pi() ** 2 * k_s * self.E
