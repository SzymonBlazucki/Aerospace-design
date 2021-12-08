import math
from constants import E, K, v, k_s, k_c, k_v
import numpy as np


class Failure:
    def __init__(self, forces, wingbox, stringer):
        self.Forces = forces
        self.Wingbox = wingbox
        self.Stringer = stringer
        self.tAft = self.Stringer.thickness[0]
        self.tFront = self.Stringer.thickness[2]

    def stressShear(self, x):
        return [self.Forces.torque(x) / (2 * self.Wingbox.enclosedArea(x) * self.tAft),  # thickness aft spar
                self.Forces.torque(x) / (2 * self.Wingbox.enclosedArea(x) * self.tFront)]  # thickness front spar


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
    def constBending(self, x):
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

    def ab(self, x):
        rb = self.Wingbox.ribs
        out = np.array(list(map(lambda i: max(rb[rb < i]), x)))
        return (x - out)

    def tb(self, x):  # to be modified, for now good enough
        return self.Wingbox.t / (0.45 * self.Forces.chord(x))

    def b(self):
        rib = self.Wingbox.ribs
        output = np.array([])
        j = 1

        for i in self.Forces.span:
            if i <= rib[j]:
                output = np.append(output, rib[j])
            else:
                output = np.append(output, rib[j])
                j += 1

        return [0.0662 * self.Forces.chord(output),  # aft
               0.0653 * self.Forces.chord(output)]   # front


    def skinBuckling(self, x):  # please confirm what value of K I should use
        allStress = math.pi ** 2 * k_c * E * self.tb(x) ** 2 / (12 * (1 - v ** 2))  # check that
        pass

    def webBuckling(self):
        b = self.b()
        aft, front = [math.pi ** 2 * k_s * E / 12 / (1 - v ** 2) * (self.tAft / b[0]) ** 2,
                      math.pi ** 2 * k_s * E / 12 / (1 - v ** 2) * (self.tFront / b[1]) ** 2]


        if aft[0] > front[0]:
            print(f"aft{aft}")
            return aft, self.tAft
        else:
            print(f"front{front}")
            return front, self.tFront

        # return np.concatenate((aft, front)).max()  # return the highest stress value

    def stressShearStressForce(self, x):
        aft, front = self.b()
        average = self.Forces.shearForce(x)/(aft * self.tAft + front * self.tFront)

        return average


    def stressShearFlowTorque(self, x):
        stress = self.Forces.torque(x) / (2 * self.Wingbox.enclosedArea(x))
        print(f"stress{stress}")
        return stress

    def marginWeb(self, x):
        failure, t = self.webBuckling()
        stress = self.stressShearFlowTorque(x) * t + self.stressShearStressForce(x)

        margin = failure / stress
        print(f"margin{margin}")
        return margin


    def marginBendingIndex(self,x):
        out = - self.stressBending(x) / self.columnBuckling(x)
        critical_point = np.where(out > 0, out, np.inf).argmin()
        return critical_point

    # return the margin due to bending stress of the critical stringer
    def marginCriticalS(self, x):
        index = self.marginBendingIndex(x)
        ylocation = self.Stringer.YPos()[index] * self.Forces.chord(x)
        stress = self.constBending(x) * ylocation
        critical_stress = - self.columnBuckling(x)[index]
        margin = critical_stress / stress
        # print(stress)
        # print(margin)
        # print(critical_stress)
        return margin

