# Change span to negative. Proposition: mirror all the graphs for a lazy solution
# Shear and bending in the other direction (drag)
# Include Cm (and Cd) in torque
# Set a coordinate system and possibly a sketch of what is what
# Using Nx, Ny, Nz from xflr file may have been easier, because we won't have to deal with angles or anything else
# in the csv file, changed the name of the column from CmAirf@chord/4 to CmAirf coz python didnt like it
#
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


def plotter(x, y, xLabel, yLabel, logarithmic=False):
    plt.plot(x, y(x))
    if logarithmic:
        plt.yscale("log")
    plt.title(xLabel + ' vs ' + yLabel)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.show()


eng = Engine()

# strArea = float(input("Area of stringer in m2\n"))
#
# wbThickness = input("Thickness of wingbox sides in meters in this order: aft, bottom, front, top\nExample input: "
#                     "0.03, 0.05, 0.01, 0.03\n")
# wbThickness = [float(x) for x in wbThickness.split(',')]
#
# topStringers = input("The length of top side stringers in meters from front to back. Corner stringers are included, "
#                      "so no need to include them. Half span is 28 meters.\nExample input: 18, 5, 1, 7, 25\n")
# if topStringers == '':
#     topStringers = []
# else:
#     topStringers = [float(x) for x in topStringers.split(',')]
#
# botStringers = input("The length of bot side stringers in meters from front to back. Corner stringers are included, "
#                      "so no need to include them. Half span is 28 meters.\nExample input: 18, 5, 1, 7, 25\n")
# if botStringers == '':
#     botStringers = []
# else:
#     botStringers = [float(x) for x in botStringers.split(',')]
#
# strng = Stringer(strArea, np.array(topStringers), np.array(botStringers), wbthickness=wbThickness)
# # print(strng.numberStringers(np.array([20, 16, 10, 8, 8]), np.linspace(5,10,10)))
#
# velocity = input("Do you want to change the velocity in m/s? To use default value, press enter.\nDefault value = 250 "
#                  "m/s which is Mach 0.84 at cruising altitude\n")
# if velocity == '':
#     velocity = 250
# else:
#     velocity = float(velocity)
#
# angle = input("Do you want to change the angle of attack in deg? To use default value, press enter.\nDefault value = "
#               "10 deg\n")
# if angle == '':
#     angle = 10
# else:
#     angle = float(angle)

# DEBUG

wbThickness = [0.03, 0.05, 0.01, 0.03]

# 0 type is L, 1 is Hat
strArea = [0.0001, 0.0001]
strIxx = [8.23E-7*100, 8.23E-7*100]

topType = [1, 1, 1, 1]
topStringers = [16, 12, 10, 8]

botType = [1, 1, 1]
botStringers = [13, 9, 6]

ribs = np.array([0, 6, 8, 15, 28])

strng = Stringer(strIxx, topType, botType, strArea, np.array(topStringers), np.array(botStringers),
                 wbthickness=wbThickness)
velocity = 250
angle = 10

testForces = Forces([zeroAngleFirstTable, tenAngleFirstTable],
                    freeVel=velocity, bHalf=28,
                    AoA=math.asin((cld - zeroCl) / (tenCl - zeroCl) * math.sin(math.radians(10))), xCentroid=0.3755,
                    # might've changed
                    engine=eng, spanSteps=51, stringer=strng, density=2700) # FOr final results keep steps high
end = time.time()
print(end - start)
start = time.time()
wb = Wingbox(forces=testForces, stringer=strng, sweep=27, ribs=ribs)
end = time.time()
print(end - start)
# failure mode
failuremode = Failure(forces=testForces, wingbox=wb, stringer=strng)
#print(failuremode.ab(testForces.span))
print('here')
print(failuremode.ab(testForces.span))
print(failuremode.marginSkin(testForces.span))
print('above')
# plotter(testForces.span, failuremode.stressShear, 'Span [m]', 'Shear stress at spar [Pa]')

plotter(testForces.span, failuremode.marginStringer, 'Span [m]', 'MoS Stringer', logarithmic=True)
plotter(testForces.span, failuremode.marginWeb, 'Span [m]', 'MoS Web', logarithmic=True)
plotter(testForces.span, failuremode.marginSkin, 'Span [m]', 'MoS Skin', logarithmic=True)
# Check statements
# print(f"Stresses: {failuremode.stressBending(testForces.span)}")
# print(f"Buckling Stress{failuremode.columnBuckling()}")
# print(f"Margin of safety {failuremode.stressBending(testForces.span) / failuremode.columnBuckling()}")  # Margin of Safety
# print(f"Length{failuremode.columBucklingLenght(testForces.span)}")
# plotter(testForces.span, failuremode.stressBending, "Span[m]", "Stress due to bending const")

# start = time.time()
# plotter(testForces.span, testForces.verticalForce, 'Span [m]', 'Vertical force per span [N/m]')
# plotter(testForces.span, testForces.verticalForceFunction, 'Span [m]',
#         'Vertical force per span [N/m] - from interpolation')
# end = time.time()
# print(end - start)
# start = time.time()
#plotter(testForces.span, testForces.chord, 'Span [m]', 'Chord [m]')
#plotter(testForces.span, testForces.weight, 'Span [m]', 'Weight per span [N/m]')
# plotter(testForces.span, testForces.drag, 'Span [m]', 'Drag per span [N/m]')
plotter(testForces.span, testForces.shearFunction, 'Span [m]', 'Shear Diagram [N]')
# #
# plotter(testForces.span, wb.momentInertiaX, 'Span [m]', 'Moment of Inertia [m^4]')
# plotter(testForces.span, testForces.bendingFunction, 'Span [m]', 'Bending Moment [N*m]')
# plotter(testForces.span, wb.bendingDisplacement, 'Span [m]', 'Horizontal Displacement [m]')
# #
# plotter(testForces.span, wb.torsionalStiffness, 'Span [m]', 'Torsional Stiffness [m^4]')
# plotter(testForces.span, testForces.twistFunction, 'Span [m]', 'Torque [N*m]')
# plotter(testForces.span, wb.twistDisplacement, 'Span [m]', 'Twist Displacement [deg]')
# end = time.time()
# print('total time')
# print(end - zeroTIme)
# start = time.time()
