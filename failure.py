import math
from constants import E, K, v, k_s, k_c, k_v, k_ic, a
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
        constbending = self.Forces.bendingMoment(x)[0] / self.Wingbox.momentInertiaX(x)[0]

        # get the y location of the stringers w.r.t the neutral axis and convert it to [m]
        yCentroid, stringerY = self.Wingbox.strYDistance(x)
        yDistance = (stringerY[0] - yCentroid[0]) * self.Forces.chord(x)[0]

        # output result for stress at all stringers at the root
        out = constbending * yDistance
        print(f"the stresses for stringers {out}")
        return out

    def testStress(self, x):
        index = self.indexCritical(x)
        print(f"the index of critical stringer is {index}")
        ylocation = self.Stringer.YPos()[index] * self.Forces.chord(x)
        stress = abs(self.Forces.bendingMoment(x) / self.Wingbox.momentInertiaX(x) * ylocation)
        return stress

    def stressBendingGen(self, x):
        # calculate the stress due to torsion without y location at the root
        constbending = self.Forces.bendingMoment(x) / self.Wingbox.momentInertiaX(x)

        # get the y location of the stringers w.r.t the neutral axis and convert it to [m]
        yCentroid, stringerY = self.Wingbox.strYDistance(x)
        yDistance = (stringerY[0] - yCentroid[0]) * self.Forces.chord(x)[0]

        # output result for stress at all stringers at the root
        #out = constbending * yDistance

        return np.array(list(map(lambda i : np.amax(i), stringerY)))
    def generalisedStress(self, x):
        y = self.Wingbox.steinerTerm(x)
        return self.Forces.bendingFunction(x) * y / self.Wingbox.momentInertiaX(x)

    # return the critical column buckling stress based on inputs
    def columnBuckling(self, x):
        # Create boolean array based on stress type (compression = 1, tensile =0)
        cforceboolean = np.where(self.stressBending(x) > 0, np.inf, 1)
        out = cforceboolean * (math.pi ** 2 * K * E * self.Stringer.strIxx) / \
              (self.Stringer.totalStr ** 2 * self.Stringer.areaArr)
        return out

    def ab(self, x):
        rb = self.Wingbox.ribs
        outRb = np.roll(rb, -1)
        filter = np.array(range(0, len(rb)))
        length = rb[1:] - rb[:-1]
        outB = np.array(list(map(lambda i: max(outRb[rb < i]), x)))
        outA = np.array(list(map(lambda i: length[max(filter[rb < i])], x)))
        return  outA / [0.0662 * self.Forces.chord(outB) ,  # aft
                 outA / 0.0653 * self.Forces.chord(outB)]  # front

    def tb(self, x):  # to be modified, for now good enough
        rib = self.Wingbox.ribs
        outRb = np.roll(rib, -1)
        output = 0.0662 * self.Forces.chord(np.array(list(map(lambda i: max(outRb[rib < i]), self.Forces.span))))
        return self.tBot / output, self.tTop / output

    def b(self):
        rib = self.Wingbox.ribs
        outRb = np.roll(rib, -1)
        output = np.array(list(map(lambda i: max(outRb[rib < i]), self.Forces.span)))
        return [0.0662 * self.Forces.chord(output),  # aft
                0.0653 * self.Forces.chord(output)]  # front

    def skinBuckling(self, x):  # please confirm what value of K I should use
        # allStress = math.pi ** 2 * k_c * E * self.tb(x) ** 2 / (12 * (1 - v ** 2))  # check that
        top = math.pi ** 2 * k_c * E / 12 / (1 - v ** 2) * self.tb(x)[1] ** 2#math.pi ** 2 * k_c * E / 12 / (1 - v ** 2) * self.tb(x)[0] ** 2, \

        return top, self.tTop
        # if bot[0] > top[0]:
        #     print(f"bot{bot}")
        #     return bot, self.tBot
        # else:
        #     print(f"top{top}")
        #     return top, self.tTop

    def webBuckling(self):
        b = self.b()
        aft, front = [math.pi ** 2 * k_s * E * (self.tAft / b[0]) ** 2 / 12 / (1 - v ** 2),
                      math.pi ** 2 * k_s * E * (self.tFront / b[1]) ** 2 / 12 / (1 - v ** 2)]

        if aft[0] > front[0]:
            # print(f"aft{aft}")
            return aft, self.tAft
        else:
            # print(f"front{front}")
            return front, self.tFront
    def crackStress(self):
        # return np.concatenate((aft, front)).max()  # return the highest stress value
        return k_ic/math.sqrt(math.pi * a)

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
        margin = failure / stress  # don't we want percentage of failure stress, not the other way around?
        # print(f"marginweb{margin}")
        return margin

    def marginSkin(self, x):
        index = self.indexCritical(x)
        print(f"the index of critical stringer is {index}")
        ylocation = self.Stringer.YPos()[index] * self.Forces.chord(x)
        stress = abs(self.Forces.bendingMoment(x) / self.Wingbox.momentInertiaX(x) * ylocation)
        critical_stress = self.skinBuckling(x)[0]
        return critical_stress / stress
        # return 1 - self.stressBending(x)[0] / self.skinBuckling(x)[0]  # for skin buckling I always want top, fix skin
        # buckling and stress bending - I want stress at every point not only at the root


    def marginCrack(self, x):
        pass

    def indexCritical(self, x):
        out = - self.stressBending(x) / self.columnBuckling(x)  # it is dividing be zero sometimes, please fix that
        critical_point = np.where(out > 0, out, np.inf).argmin()
        return critical_point

    # return the margin due to bending stress of the critical stringer
    def marginStringer(self, x):
        index = self.indexCritical(x)
        print(f"the index of critical stringer is {index}")
        ylocation = self.Stringer.YPos()[index] * self.Forces.chord(x)
        stress = self.Forces.bendingMoment(x) / self.Wingbox.momentInertiaX(x) * ylocation
        critical_stress = - self.columnBuckling(x)[index]
        margin = critical_stress / stress
        # print(stress)
        # print(margin)
        # print(critical_stress)
        return margin
