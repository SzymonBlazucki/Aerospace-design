import numpy as np
from constants import g

# def Arrayize(array):


class Stringer:
    def __init__(self, strIxx, topType, botType, areaStr, topStr, botStr, wbthickness):
        self.topType = np.concatenate((np.array([0]), topType, np.array([0])))
        self.botType = np.concatenate((np.array([0]), botType, np.array([0])))
        self.totalType = np.concatenate((self.botType, self.topType))

        self.strIxx = strIxx
        self.area = areaStr  # area of stringer

        for i in range(len(self.area)):
            if i == 0:
                self.areaArr = (self.totalType == 0) * self.area[0]
            else:
                self.areaArr += (self.totalType == i) * self.area[i]

        self.topStr = np.concatenate((np.array([28]), topStr, np.array([28])))  # add corner stringers
        self.botStr = np.concatenate((np.array([28]), botStr, np.array([28])))
        self.totalStr = np.concatenate((self.botStr, self.topStr))

        self.thickness = wbthickness
        self.topXPos = np.linspace(0.00000001, 0.45, len(self.topStr))
        self.botXPos = np.linspace(0.00000001, 0.45, len(self.botStr))

    # def numberStringers(self, ySpan):
    #     out = np.array([])
    #     for i in ySpan:
    #         j = np.count_nonzero(self.totalStr >= i)
    #         out = np.append(out, j)
    #     return out

    def activeStringers(self, loc, ySpan):
        for i in ySpan:
            j = loc * (loc >= i)
            if i == ySpan[0]:
                out = j
            else:
                out = np.vstack([out, j])
        return (out > 0) * 1

    def topYPos(self):  # y-position of stringers in top
        return 0.016222222222 * self.topXPos + 0.0653

    def botYPos(self):  # y-position of stringers in bot
        return 0.014222222222 * self.botXPos

    def areaTot(self, span):  # dot product with area
        # return self.numberStringers(span) * self.area
        area = self.areaArr * self.activeStringers(self.totalStr, span)
        return np.sum(area, axis=1)

    def areaX(self, x):
        xActive = self.activeStringers(self.totalStr, x) * self.XPos() * self.areaArr
        return np.sum(xActive, axis=1)

    def areaY(self, x):
        yActive = self.activeStringers(self.totalStr, x) * self.YPos() * self.areaArr
        return np.sum(yActive, axis=1)

    def XPos(self):
        return np.concatenate((self.botXPos, self.topXPos))

    def YPos(self):
        return np.concatenate((self.botYPos(), self.topYPos()))

    def IxxStringer(self):
        # there are two types of stingers
        # head stringer (I) or l stringer (0)
        # replace array item by Ixx
        return out

class Engine:  # coordinates with respect to local chord
    xPos = 9.18  # [m]
    zPos = - 0.678  # [m]
    weight = 6120 * g  # [N]
    thrust = 360430  # [N]

    def yPos(self, xCentroid, chord):
        return -xCentroid * chord - 0.3 - 0.6 * 4.77
