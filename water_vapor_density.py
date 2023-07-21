#Author: Andres Ortiz

import saturationVaporPressure


def getWaterVaporDensity(relativeHumidity, Temp):
    return relativeHumidity() * getSaturationVaporDensity(Temp)

#This formula is good for Temperatures less than 400K
def getSaturationVaporDensity(Temp):
    MolarMassWater = 18.01528 #g/mol
    SVP = saturationVaporPressure(Temp) #input in kelvin, output is in Pa
    R = 8.3144598 #m^3 Pa/K mol
    density = (SVP * MolarMassWater)/(R*Temp) #g/m^3
    return density