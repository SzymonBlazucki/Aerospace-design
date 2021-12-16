import math
from constants import E, K, v, k_s, k_c, k_v, k_ic, a, sigma_y
import numpy as np


class Failure:
    def __init__(self, forces, wingbox, stringer):
        self.Forces = forces
        self.Wingbox = wingbox
        self.Stringer = stringer
        self.tAft = self.Stringer.thickness[0]
        self.tBot = self.Stringer.thickness[1]
        self.tFront = self.Stringer.thickness[2]
        self.tTop = self.Stringer.thickness[3]

    # Stringer buckling at the root (root has the critical stress due to bending)
    def stressBending(self, x):
        # calculate the stress due to torsion without y location at the root
        constbending = -self.Forces.bendingMoment(x)[0]/ self.Wingbox.momentInertiaX(x)[0]
        #print(f'const bending{-self.Forces.bendingMoment(x)/ self.Wingbox.momentInertiaX(x)}')
        # get the y location of the stringers w.r.t the neutral axis and convert it to [m]
        yCentroid, stringerY = self.Wingbox.strYDistance(x)
        yDistance = (stringerY[0] - yCentroid[0]) * self.Forces.chord(x)[0]

        # output result for stress at all stringers at the root
        out = constbending * yDistance
        # print(f"the stresses for stringers {out}")
        # print(f"stressbending{out}")
        return out

    def testStress(self, x):
        index = self.indexCritical(x)
        # print(f"the index of critical stringer is {index}")
        ylocation = self.Stringer.YPos()[index] * self.Forces.chord(x)
        stress = abs(-self.Forces.bendingMoment(x) / self.Wingbox.momentInertiaX(x) * ylocation)
        return stress

    def stressBendingGen(self, x):
        # calculate the stress due to torsion without y location at the root
        constbending = -self.Forces.bendingMoment(x) / self.Wingbox.momentInertiaX(x)

        # get the y location of the stringers w.r.t the neutral axis and convert it to [m]
        yCentroid, stringerY = self.Wingbox.strYDistance(x)
        yDistance = (stringerY[0] - yCentroid[0]) * self.Forces.chord(x)[0]

        # output result for stress at all stringers at the root
        # out = constbending * yDistance

        return np.array(list(map(lambda i: np.amax(i), stringerY)))

    def generalisedStress(self, x):
        y = self.Wingbox.steinerTerm(x)
        return self.Forces.bendingFunction(x) * y / self.Wingbox.momentInertiaX(x)

    # return the critical column buckling stress based on inputs
    def columnBuckling(self, x, rib_pitch):
        # Create boolean array based on stress type (compression = 1, tensile =0)
        cforceboolean = np.where(self.stressBending(x) > 0, np.inf, 1)
        out = cforceboolean * (math.pi ** 2 * K * E * self.Stringer.strIxx) / \
              ((rib_pitch ** 2 * self.Stringer.areaArr))
        return out

    def zero_runs(a):
        # Create an array that is 1 where a is 0, and pad each end with an extra 0.
        iszero = np.concatenate(([0], np.equal(a, 0).view(np.int8), [0]))
        absdiff = np.abs(np.diff(iszero))
        # Runs start and end where absdiff is 1.
        ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
        return ranges

    def ab(self, x):
        rb = self.Wingbox.ribs
        outRb = np.roll(rb, -1)  # implement diff somewhere
        filter = np.array(range(0, len(rb)))
        length = rb[1:] - rb[:-1]
        outB = np.array(list(map(lambda i: max(outRb[rb < i]), x)))
        stringersTot = self.Stringer.activeStringers(self.Stringer.totalStr, x)
        stringersArr = stringersTot[:, -len(self.Stringer.topStr):]
        fullCol = np.zeros(len(stringersArr[:, 0]))  # column of zeros
        padded = np.concatenate(([fullCol * 0], np.transpose(np.equal(stringersArr, 0)), [fullCol * 0]),
                                axis=0).T  # pads left and right column of zeros
        ones = np.abs(np.diff(padded))  # gives 1 at difference between 0 and 1
        outBn = np.array(list(map(lambda i: np.amax(np.append(np.diff(np.where(i == 1)[0].reshape(-1, 2)), [1])),
                                  ones)))  # calculates longest interval between stringers in the unit of stringer
        # spacing
        outA = np.array(list(map(lambda i: length[max(filter[rb < i])], x)))  # calculates "a" side of the pannel
        return outA / (0.45 * self.Forces.chord(outB) * outBn / len(stringersArr[0])), \
               outA / (0.45 * self.Forces.chord(outB) * outBn / len(stringersArr[0]))  # first aft then front

    def tb(self, x):  # to be modified, for now good enough
        rib = self.Wingbox.ribs
        outRb = np.roll(rib, -1)
        # output = 0.0662 * self.Forces.chord(np.array(list(map(lambda i: max(outRb[rib < i]), self.Forces.span))))
        rb = self.Wingbox.ribs
        outRb = np.roll(rb, -1)  # implement diff somewhere
        outB = np.array(list(map(lambda i: max(outRb[rb < i]), x)))
        stringersTot = self.Stringer.activeStringers(self.Stringer.totalStr, x)
        stringersArr = stringersTot[:, -len(self.Stringer.topStr):]
        fullCol = np.zeros(len(stringersArr[:, 0]))  # column of zeros
        padded = np.concatenate(([fullCol * 0], np.transpose(np.equal(stringersArr, 0)), [fullCol * 0]),
                                axis=0).T  # pads left and right column of zeros
        ones = np.abs(np.diff(padded))  # gives 1 at difference between 0 and 1
        outBn = np.array(list(map(lambda i: np.amax(np.append(np.diff(np.where(i == 1)[0].reshape(-1, 2)), [1])),
                                  ones)))
        return self.tBot / (0.45 * self.Forces.chord(outB) * outBn / len(stringersArr[0])), self.tTop / (
                    0.45 * self.Forces.chord(outB) * outBn / len(stringersArr[0])) # REPAIR BOTTOM!!!

    def b(self):
        rib = self.Wingbox.ribs
        outRb = np.roll(rib, -1)
        output = np.array(list(map(lambda i: max(outRb[rib < i]), self.Forces.span)))
        return [0.0662 * self.Forces.chord(output),  # aft
                0.0653 * self.Forces.chord(output)]  # front

    def skinBuckling(self, x):
        # allStress = math.pi ** 2 * k_c * E * self.tb(x) ** 2 / (12 * (1 - v ** 2))  # check that
        top = math.pi ** 2 * k_c * E / 12 / (1 - v ** 2) * self.tb(x)[
            1] ** 2  # math.pi ** 2 * k_c * E / 12 / (1 - v ** 2) * self.tb(x)[0] ** 2, \

        return top, self.tTop

    def webBuckling(self):
        b = self.b()
        # print(f"b{b}")
        aft, front = [math.pi ** 2 * k_s(self.ab(self.Forces.span)[0]) * E * (self.tAft / b[0]) ** 2 / 12 / (1 - v ** 2),
                      math.pi ** 2 * k_s(self.ab(self.Forces.span)[0]) * E * (self.tFront / b[1]) ** 2 / 12 / (1 - v ** 2)]

        if aft[0] > front[0]:
            # print(f"aft{aft}")
            return aft, self.tAft
        else:
            # print(f"front{front}")
            return front, self.tFront

    def crackStress(self):
        # return np.concatenate((aft, front)).max()  # return the highest stress value
        return k_ic / math.sqrt(math.pi * a)

    def shearStressForce(self, x):
        aft, front = self.b()
        average = self.Forces.shearForce(x) / (aft * self.tAft + front * self.tFront)
        return average * k_v

    def shearFlowTorque(self, x):
        stress = self.Forces.torque(x) / (2 * self.Wingbox.enclosedArea(x))
        # print(f"stress{stress}")
        return stress

    def marginWeb(self, x):
        failure, t = self.webBuckling()
        stress = self.shearFlowTorque(x) * t + self.shearStressForce(x)
        margin = failure / stress
        # print(f"marginweb{margin}")
        return margin

    def marginSkin(self, x):
        index = self.indexCritical(x)
        # print(f"the index of critical stringer in compression is {index}")
        ylocation = self.Stringer.YPos()[index] * self.Forces.chord(x)
        stress = abs(-self.Forces.bendingMoment(x) / self.Wingbox.momentInertiaX(x) * ylocation)
        critical_stress = self.skinBuckling(x)[0]
        return critical_stress / stress
        # return 1 - self.stressBending(x)[0] / self.skinBuckling(x)[0]  # for skin buckling I always want top, fix skin
        # buckling and stress bending - I want stress at every point not only at the root

    def marginCrack(self, x):
        index = self.indexCriticalTens(x)
        # print(f"the index of critical stringer in tension is {index}")
        ylocation = self.Stringer.YPos()[index] * self.Forces.chord(x)
        stress = self.Forces.bendingMoment(x) / self.Wingbox.momentInertiaX(x) * ylocation
        return self.crackStress() / abs(stress)

    def indexCritical(self, x, rib_pitch):
        out = - self.stressBending(x) / self.columnBuckling(x, rib_pitch)  # it is dividing be zero sometimes, please fix that
        for i in self.Stringer.cornerIndex:
            out[i] = 0
        critical_point = np.where(out > 0, out, -np.inf).argmax()
        # print(f"criticalpoint{critical_point}")
        return critical_point

    def indexCriticalTens(self, x):
        out = - self.stressBending(x)  # it is dividing be zero sometimes, please fix that
        # print(out)
        for i in self.Stringer.cornerIndex:
            out[i] = 0
        # print(out)
        critical_point = np.where(out < 0, out, np.inf).argmin()
        return critical_point

    # return the margin due to bending stress of the critical stringer
    def marginStringer(self, x, rib_pitch):
        index = self.indexCritical(x, rib_pitch)
        # print(f"the index of critical stringer is {index}")
        ylocation = self.Stringer.YPos()[index] * self.Forces.chord(x)
        stress = -self.Forces.bendingMoment(x) / self.Wingbox.momentInertiaX(x) * ylocation
        critical_stress = - self.columnBuckling(x, rib_pitch)[index]
        # critical_stress = - self.rankineGordon(x)[index]

        margin = critical_stress / stress
        # print(f"stress{stress}")
        # print(f"margin{margin}")
        # print(f"criticalstress{critical_stress}")
        return margin

    def rankineGordon(self, x):
        a = sigma_y / math.pi ** 2 / E
        stress_yield = sigma_y / (1 + a * self.Stringer.totalStr ** 2 * self.Stringer.areaArr / self.Stringer.strIxx)
        return stress_yield
