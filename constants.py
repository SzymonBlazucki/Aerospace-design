import reader
from scipy import interpolate

g = 9.80665  # [m/s^2] gravity acceleration
cld = 0.6767
a = 0.005

factor = 1.75  # try to keep below 1.75 or 2
K = 1  # constant for column buckling
E = 68.9E9  # Young's modulus in pascal
G = 26E9  # Shear modulus in pascal
v = 0.33
# k_s = 9.6  # Placeholder, please change
# k_c = 7.8
k_v = 3 / 2  # Ratio max shear stress and average shear stress
k_ic = 29.0E6  # fracture toughness in Pa/m^1/2
sigma_y = 276E06


def k_s(ab):
    r = ab
    return (8.98 + 5.6 / r ** 2)


def k_c(ab):
    return 6.97944 + 2.72925 / ab ** 2 + 1.07135 / ab


zeroAngleFirstTable, zeroAngleSecondTable, zeroCl = reader.readXLFR('xlfrData/alpha0.csv')
tenAngleFirstTable, tenAngleSecondTable, tenCl = reader.readXLFR('xlfrData/alpha10.csv')


def interp(x, y, kind='cubic'):
    f = interpolate.interp1d(x, y, kind=kind, fill_value='extrapolate')
    return f
