import pandas as pd
import numpy as np
import scipy as sp

firstTable = pd.read_csv('xlfrData/test.csv', skipinitialspace=True, encoding_errors='ignore', skiprows=20, nrows=38)
secondTable = pd.read_csv('xlfrData/test.csv', skipinitialspace=True, encoding_errors='ignore', skiprows=62, skip_blank_lines=True)
secondTable = secondTable[pd.notnull(secondTable.Nz)]

