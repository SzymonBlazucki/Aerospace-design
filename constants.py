import reader
from scipy import interpolate

g = 9.80665  # [m/s^2] gravity acceleration
cld = 0.6767

zeroAngleFirstTable, zeroAngleSecondTable, zeroCl = reader.readXLFR('xlfrData/alpha0.csv')
tenAngleFirstTable, tenAngleSecondTable, tenCl = reader.readXLFR('xlfrData/alpha10.csv')


def interp(x, y, kind='cubic'):
    f = interpolate.interp1d(x, y, kind=kind, fill_value='extrapolate')
    return f

