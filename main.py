import math
from forces import Forces
from wingbox import Wingbox
from failure import Failure
from supplementaryClasses import Stringer, Engine
import matplotlib.pyplot as plt
import numpy as np
from constants import cld, zeroCl, tenCl, zeroAngleFirstTable, tenAngleFirstTable
import time

prog_start = time.time()

def plotter(x, y, xLabel, yLabel, logarithmic=False, lowerlimit=None, upperlimit=None):

    plt.plot(x, y(x), label=yLabel)

    if logarithmic:
        plt.yscale("log")
    if lowerlimit:
        plt.hlines(y=lowerlimit, xmin=0, xmax=28, label='Lower limit', color='r')
        plt.legend()
    if upperlimit:
        plt.hlines(y=upperlimit, xmin=0, xmax=28, label='Upper limit', color='m')
        plt.legend()

    plt.title(xLabel + ' vs ' + yLabel)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.grid(True)
    plt.show()


wbThickness = [0.02, 0.03, 0.02, 0.03]  # order: aft, bot, front, top

# 0 type is L, 1 is Hat
strArea = [0.0005, 0.0005]
strIxx = [4.18E-7, 4.18E-7]

topType = [1, 1, 1, 1]
topStringers = [16, 18, 16, 16]

botType = [1, 1, 1]
botStringers = [13, 9, 6]

rib_pitch = 1  # space between ribs in meters
ribs = np.linspace(0, 28, int(28/rib_pitch + 1))

velocity = 250
angle = 10


start = time.time()
eng = Engine()
end = time.time()
print(f"Time to load Engine: {end-start}s")

start = time.time()
strng = Stringer(strIxx, topType, botType, strArea, np.array(topStringers), np.array(botStringers),
                 wbthickness=wbThickness)
end = time.time()
print(f"Time to load Stringer: {end-start}s")

start = time.time()
testForces = Forces([zeroAngleFirstTable, tenAngleFirstTable],
                    freeVel=velocity, bHalf=28,
                    AoA=math.asin((cld - zeroCl) / (tenCl - zeroCl) * math.sin(math.radians(10))), xCentroid=0.3755,
                    # might've changed
                    engine=eng, spanSteps=101, stringer=strng, density=2700) # FOr final results keep steps high
end = time.time()
print(f"Time to load Forces: {end-start}s")

start = time.time()
wb = Wingbox(forces=testForces, stringer=strng, sweep=27, ribs=ribs)
end = time.time()
print(f"Time to load Wingbox: {end-start}s")

start = time.time()
failuremode = Failure(forces=testForces, wingbox=wb, stringer=strng)
end = time.time()
print(f"Time to load Failure: {end-start}s")

start = time.time()


plotter(testForces.span, failuremode.marginStringer, 'Span [m]', 'MoS Stringer', logarithmic=True, lowerlimit=1)
plotter(testForces.span, failuremode.marginWeb, 'Span [m]', 'MoS Web', logarithmic=True, lowerlimit=1)
plotter(testForces.span, failuremode.marginSkin, 'Span [m]', 'MoS Skin', logarithmic=True, lowerlimit=1)
plotter(testForces.span, failuremode.marginCrack, 'Span [m]', 'MoS Crack', logarithmic=True, lowerlimit=1)

# plotter(testForces.span, testForces.chord, 'Span [m]', 'Chord [m]')
# plotter(testForces.span, testForces.weight, 'Span [m]', 'Weight per span [N/m]')
# plotter(testForces.span, testForces.drag, 'Span [m]', 'Drag per span [N/m]')
# plotter(testForces.span, testForces.lift, 'Span', 'Lift per span [N/m]')
# plotter(testForces.span, testForces.verticalForce, 'Span [m]', 'Vertical force per span [N/m]')
# plotter(testForces.span, testForces.shearFunction, 'Span [m]', 'Shear Diagram [N]')
#
# plotter(testForces.span, wb.momentInertiaX, 'Span [m]', 'Moment of Inertia [m^4]')
# plotter(testForces.span, testForces.bendingFunction, 'Span [m]', 'Bending Moment [N*m]')
plotter(testForces.span, wb.bendingDisplacement, 'Span [m]', 'Horizontal Displacement [m]', upperlimit=4.2)
#
# plotter(testForces.span, wb.torsionalStiffness, 'Span [m]', 'Torsional Stiffness [m^4]')
# plotter(testForces.span, testForces.twistFunction, 'Span [m]', 'Torque [N*m]')
plotter(testForces.span, wb.twistDisplacement, 'Span [m]', 'Twist Displacement [deg]', upperlimit=10)


end = time.time()
print(f"Time to load Graphs: {end-start}s")
prog_end = time.time()
print(f"Total time to run the whole program is {prog_end-prog_start}s")