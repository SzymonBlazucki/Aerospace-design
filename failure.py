import numpy as np

class Failure:
    def __init__(self, forces, wingbox, stringer):
        self.Forces = forces
        self.Wingbox = wingbox
        self.Stringer = stringer

    def yDistance(self, x):
        stringerY = self.Stringer.activeStringers(self.Stringer.totalStr, x) * self.Stringer.YPos()
        rows, cols = stringerY.shape

        yCentroid = np.tile(np.array([self.Wingbox.yBarWingbox(x)]).transpose(), (1, cols))
        return (yCentroid - stringerY)