
class Failure:
    def __init__(self, forces, wingbox, stringer):
        self.Forces = forces
        self.Wingbox = wingbox
        self.Stringer = stringer



    # Stringer buckling at the root (root has the critical stress due to bending)
    def StressBending(self, x):
        # calculate the stress due to torsion without y location at the root
        constbending = - self.Forces.bendingMoment(x)[0] / self.Wingbox.momentInertiaX(x)[0]

        # get the y location of the stringers w.r.t the neutral axis and convert it to [m]
        yCentroid, stringerY = self.Wingbox.strYDistance(x)
        yDistance = (stringerY[0] - yCentroid[0]) * self.Forces.chord(x)[0]


        # output result for stress at all stringers at the root
        out = constbending * yDistance
        return out

    # Create the item for the stress due to bending
    def StressBendingGraph(self,x):
        # calculate the stress due to bending moment without y location as a function of span
        constbending = - self.Forces.bendingMoment(x) / self.Wingbox.momentInertiaX(x)
        return constbending


