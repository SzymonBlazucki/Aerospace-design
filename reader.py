import pandas as pd
import numpy as np
import scipy as sp

def readXLFR(fileName):
    firstTable = pd.read_csv(fileName, skipinitialspace=True, encoding_errors='ignore', skiprows=20, nrows=38)
    secondTable = pd.read_csv(fileName, skipinitialspace=True, encoding_errors='ignore', skiprows=62, skip_blank_lines=True)
    secondTable = secondTable[pd.notnull(secondTable.Nz)]
    return firstTable, secondTable