import math
from forces import Forces
from wingbox import Wingbox
from failure import Failure
from supplementaryClasses import Stringer, Engine
import matplotlib.pyplot as plt
import numpy as np
from constants import cld, zeroCl, tenCl, zeroAngleFirstTable, tenAngleFirstTable
import time

zeroTIme = time.time()
start = time.time()


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


wbThickness = [0.01, 0.01, 0.01, 0.01]  # order: aft, bot, front, top

# 0 type is L, 1 is Hat
strArea = [0.0005, 0.0005]
strIxx = [4.18E-7, 4.18E-7]

topType = [1, 1, 1, 1]
topStringers = [16, 18, 16, 16]

botType = [1, 1, 1]
botStringers = [13, 9, 6]
strng = Stringer(strArea, np.array(topStringers), np.array(botStringers), wbthickness=wbThickness)
velocity = 250
angle = 10

testForces = Forces([zeroAngleFirstTable, tenAngleFirstTable],
                    freeVel=velocity, bHalf=28,
                    AoA=math.asin((cld - zeroCl) / (tenCl - zeroCl) * math.sin(math.radians(10))), xCentroid=0.3755,
                    # might've changed
                    engine=eng, spanSteps=51, stringer=strng, density=2700)
end = time.time()
print(end - start)
start = time.time()
wb = Wingbox(forces=testForces, stringer=strng, sweep=27, ribs=ribs, rib_pitch=rib_pitch)
end = time.time()
print(end - start)
start = time.time()
failuremode = Failure(forces=testForces, wingbox=wb, stringer=strng)
end = time.time()
print(end - start)
start = time.time()
plotter(testForces.span, testForces.weight, 'Span [m]', 'Weight per span [N/m]')
plotter(testForces.span, testForces.drag, 'Span [m]', 'Drag per span [N/m]')
plotter(testForces.span, testForces.shearFunction, 'Span [m]', 'Shear Diagram [N]')
#
plotter(testForces.span, wb.momentInertiaX, 'Span [m]', 'Moment of Inertia [m^4]')
plotter(testForces.span, testForces.bendingFunction, 'Span [m]', 'Bending Moment [N*m]')
plotter(testForces.span, wb.bendingDisplacement, 'Span [m]', 'Horizontal Displacement [m]')
#
plotter(testForces.span, wb.torsionalStiffness, 'Span [m]', 'Torsional Stiffness [m^4]')
plotter(testForces.span, testForces.twistFunction, 'Span [m]', 'Torque [N*m]')
plotter(testForces.span, wb.twistDisplacement, 'Span [m]', 'Twist Displacement [deg]')
end = time.time()
print('total time')
print(end - zeroTIme)
start = time.time()
