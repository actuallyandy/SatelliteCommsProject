#Author: Andres Ortiz

import Formulas.saturationVaporPressure as SVP


def getWaterVaporDensity(relativeHumidity, Temp):
    SVD = getSaturationVaporDensity(Temp)
    return relativeHumidity * SVD

#This formula is good for Temperatures less than 400K
def getSaturationVaporDensity(Temp):
    MolarMassWater = 18.01528 #g/mol
    svp = SVP.getSaturationVaporPressure(Temp) #input in kelvin, output is in Pa
    R = 8.3144598 #m^3 Pa/K mol
    density = (svp * MolarMassWater)/(R*Temp) #g/m^3
    return density