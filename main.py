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


wbThickness = [0.01, 0.01, 0.01, 0.02]  # order: aft, bot, front, top

# 0 type is L, 1 is Hat
strArea = [0.0005, 0.0005]
strIxx = [4.18E-7, 4.18E-7]

topType = [1, 1, 1, 1, 1]
topStringers = [16, 18, 16, 16, 28]

botType = [1, 1, 1]
botStringers = [13, 9, 6]

rib_pitch = np.array([0.3, 0.5, 0.75, 1])   # space between ribs in meters (range of 0.2-1)
# ribs = np.linspace(0, 28, int(28/rib_pitch + 1))
rib_length = np.array([5, 13, 20, 27.9])

ribs = np.concatenate((np.arange(0, rib_length[0], rib_pitch[0]), np.arange(rib_length[0], rib_length[1], rib_pitch[1]),
                       np.arange(rib_length[1], rib_length[2], rib_pitch[2]), np.arange(rib_length[2], rib_length[3], rib_pitch[3]), np.array([28]) ))
#print(len(ribs))
#print('here')
#ribs = [0,28]

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
                    engine=eng, spanSteps=51, stringer=strng, density=2700) # For final results keep steps high
end = time.time()
print(f"Time to load Forces: {end-start}s")

start = time.time()
wb = Wingbox(forces=testForces, stringer=strng, sweep=27, ribs= ribs, rib_length=rib_length, rib_pitch=rib_pitch)
end = time.time()
print(f"Time to load Wingbox: {end-start}s")

start = time.time()
failuremode = Failure(forces=testForces, wingbox=wb, stringer=strng)
end = time.time()
print(f"Time to load Failure: {end-start}s")

start = time.time()

def span(a, b):
    size = len(testForces.span)
    a, b = math.floor(a * size / 28), math.floor(b * size / 28)

    return testForces.span[a:b]

rib_length = np.concatenate((np.array([0]), rib_length))
marginStringer = np.array([])
marginSkin = np.array([])
for i in range(len(rib_pitch)):
    # if i == 0:
    #     marginsStringer = failuremode.marginStringer(span(rib_length[i], rib_length[i + 1]), rib_pitch[i])
    # else
    marginStringer = np.concatenate((marginStringer, failuremode.marginStringer(span(rib_length[i], rib_length[i+1]), rib_pitch[i])))
    # print(rib_length[i], rib_length[i+1], rib_pitch[i])
    # print(failuremode.marginStringer(span(rib_length[i], rib_length[i+1]), rib_pitch[i]))
for i in range(len(rib_pitch)):
    # if i == 0:
    #     marginsStringer = failuremode.marginStringer(span(rib_length[i], rib_length[i + 1]), rib_pitch[i])
    # else
    marginSkin = np.concatenate((marginSkin, failuremode.marginSkin(span(rib_length[i], rib_length[i+1]), rib_pitch[i])))


# plt.plot(testForces.span, marginStringer)
# plt.show()

# plt.plot(testForces.span, marginSkin)
# plt.show()


# plotter(testForces.span, failuremode.marginStringer, 'Span [m]', 'MoS Stringer', logarithmic=True, lowerlimit=1)
# plotter(testForces.span, failuremode.marginWeb, 'Span [m]', 'MoS Web', logarithmic=True, lowerlimit=1)
# plotter(testForces.span, failuremode.marginSkin, 'Span [m]', 'MoS Skin', logarithmic=True, lowerlimit=1)
# plotter(testForces.span, failuremode.marginCrack, 'Span [m]', 'MoS Crack', logarithmic=True, lowerlimit=1)

# plotter(testForces.span, testForces.chord, 'Span [m]', 'Chord [m]')
# plotter(testForces.span, testForces.weight, 'Span [m]', 'Weight per span [N/m]')
# plotter(testForces.span, testForces.drag, 'Span [m]', 'Drag per span [N/m]')
# plotter(testForces.span, testForces.lift, 'Span', 'Lift per span [N/m]')
# plotter(testForces.span, testForces.verticalForce, 'Span [m]', 'Vertical force per span [N/m]')
# plotter(testForces.span, testForces.shearFunction, 'Span [m]', 'Shear Diagram [N]')

# plotter(testForces.span, wb.momentInertiaX, 'Span [m]', 'Moment of Inertia [m^4]')
# plotter(testForces.span, testForces.bendingFunction, 'Span [m]', 'Bending Moment [N*m]')
# plotter(testForces.span, wb.bendingDisplacement, 'Span [m]', 'Horizontal Displacement [m]', upperlimit=4.2)

# plotter(testForces.span, wb.torsionalStiffness, 'Span [m]', 'Torsional Stiffness [m^4]')
# plotter(testForces.span, testForces.twistFunction, 'Span [m]', 'Torque [N*m]')
# plotter(testForces.span, wb.twistDisplacement, 'Span [m]', 'Twist Displacement [deg]', upperlimit=10)


end = time.time()
print(f"Time to load Graphs: {end-start}s")
prog_end = time.time()
print(f"Total time to run the whole program is {prog_end-prog_start}s")