#please add stuff here

#joshua
#josh
import numpy as np


class Failure:
    def __init__(self, forces, wingbox, stringer):
        self.Forces = forces
        self.Wingbox = wingbox
        self.Stringer = stringer

    def yDistance(self, x):
        # Get the y locations of the stringer
        stringerY = self.Stringer.activeStringers(self.Stringer.totalStr, x) * self.Stringer.YPos()
        rows, cols = stringerY.shape
        yCentroid = np.tile(np.array([self.Wingbox.yBarWingbox(x)]).transpose(), (1, cols))
        return (yCentroid - stringerY)

    # Stringer buckling at the root (root has the critical stress due to bending)
    def StressBending(self, x):
        # calculate the stress due to torsion without y location at the root
        constbending = - self.Forces.bendingMoment(x)[0] / self.Wingbox.momentInertiaX(x)[0]

        # get the y location of the stringers w.r.t the neutral axis and convert it to [m]
        ydistance = self.yDistance(x)[0] * self.Forces.chord(x)[0]

        # output result for stress at all stringers at the root
        out = constbending * ydistance
        return out

    # Create the item for the stress due to bending
    def StressBendingGraph(self,x):
        # calculate the stress due to torsion without y location as a function of span
        constbending = - self.Forces.bendingMoment(x) / self.Wingbox.momentInertiaX(x)
        return constbending


