import numpy as np
from constants import g, factor

def arrayize(array, type): # returnarray with length number of stringers, including effect of stringer type
    for i in range(len(array)):
        if i == 0:
            out = (type == 0) * array[0]
        else:
            out += (type == i) * array[i]
    return out

class Stringer:
    def __init__(self, IxxStr, topType, botType, areaStr, topStr, botStr, wbthickness):
        self.topType = np.concatenate((np.array([0]), topType, np.array([0])))
        self.botType = np.concatenate((np.array([0]), botType, np.array([0])))
        self.totalType = np.concatenate((self.botType, self.topType))  # array for types of all stringers

        self.strIxx = arrayize(IxxStr, self.totalType)  # array for Ixx of all stringers
        # self.area = areaStr  # area of stringer
        self.areaArr = arrayize(areaStr, self.totalType)  # array for area of all stringers

        self.topStr = np.concatenate((np.array([28]), topStr, np.array([28])))
        self.botStr = np.concatenate((np.array([28]), botStr, np.array([28])))
        self.totalStr = np.concatenate((self.botStr, self.topStr))  # array for length of all stringers

        self.thickness = wbthickness
        self.topXPos = np.linspace(0.00000001, 0.45, len(self.topStr))
        self.botXPos = np.linspace(0.00000001, 0.45, len(self.botStr))

    def activeStringers(self, loc, ySpan):
        for i in ySpan:
            j = loc * (loc >= i)
            if i == ySpan[0]:
                out = j
            else:
                out = np.vstack([out, j])
        return (out > 0) * 1

    def topYPos(self):  # y-position of stringers in top
        return 0.016222222222 * self.topXPos + 0.0653 * factor

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

class Engine:  # coordinates with respect to local chord
    xPos = 9.18  # [m]
    zPos = - 0.678  # [m]
    weight = 6120 * g  # [N]
    thrust = 360430  # [N]

    def yPos(self, xCentroid, chord):
        return -xCentroid * chord - 0.3 - 0.6 * 4.77
