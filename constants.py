import reader
from scipy import interpolate

g = 9.80665  # [m/s^2] gravity acceleration
cld = 0.6767

factor = 1.5 # try to keep below 1.75 or 2
K = 1/4  # constant for column buckling
E = 68.9E9  # Young's modulus in pascal
G = 26E9  # Shear modulus in pascal
v = 0.33
k_s = 9.6  # Placeholder, please change
k_c = 7.8
k_v = 3/2  # Ratio max shear stress and average shear stress
k_ic = 29.0E9  # fracture toughness in Pa/m^1/2

zeroAngleFirstTable, zeroAngleSecondTable, zeroCl = reader.readXLFR('xlfrData/alpha0.csv')
tenAngleFirstTable, tenAngleSecondTable, tenCl = reader.readXLFR('xlfrData/alpha10.csv')


def interp(x, y, kind='cubic'):
    f = interpolate.interp1d(x, y, kind=kind, fill_value='extrapolate')
    return f

