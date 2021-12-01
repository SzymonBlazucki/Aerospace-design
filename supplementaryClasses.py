import numpy as np
from constants import g


class Stringe
    def __init__(self, areaStr, topStr, botStr, wbthickness):
        self.area = areaStr  # area of stringer
        self.topStr = topStr
        self.botStr = botStr
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

    def areaTot(self, span):  # dot product with area
        return self.numberStringers(span) * self.area

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



class Engine:  # coordinates with respect to local chord
    xPos = 9.18  # [m]
    zPos = - 0.678  # [m]
    weight = 6120 * g  # [N]
    thrust = 360430  # [N]

    def yPos(self, xCentroid, chord):
        return -xCentroid * chord - 0.3 - 0.6 * 4.77
