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

    def StressTorsion(self, x):
        # calculate the stress due to torsion without y location
        consttorsion = - self.Forces.bendingMoment(x)/self.Wingbox.momentInertiaX(x)

        # get the y location of the stringers w.r.t the neutral axis
        print(f"The locations {self.yDistance(x)[0]}")
        return consttorsion

