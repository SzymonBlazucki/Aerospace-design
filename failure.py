#please add stuff here

#joshua
#josh

class Failure:
    def __init__(self, forces, wingbox, stringer):
        self.Forces = forces
        self.Wingbox = wingbox
        self.Stringer = stringer

    def StressTorsion(self, x):
        constTorsion = - self.Forces.bendingMoment(x)/self.Wingbox.momentInertiaX(x)
        return constTorsion