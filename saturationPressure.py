#Author: Andres Ortiz
#Description: Formulas are pulled from here: https://journals.ametsoc.org/view/journals/apme/57/6/jamc-d-17-0334.1.xml

import math

#Temperature input must be in celcius
def saturationPressureWater(Temp):
    num = math.exp(34.494 -(4924.99/(Temp+273.15)))
    den = math.pow(Temp+105,1.57)
    saturationPressure = num/den
    return saturationPressure

def saturationPressureIce(Temp):
    num = math.exp(43.494 - (6545.8/(Temp+278)))
    den = math.pow(Temp+868,2)
    saturationPressure = num/den
    return saturationPressure


def getSaturationPressure(Temp):
    Temp = Temp - 273.15 #Converts from Kelvin to Celcius
    if (Temp > 0):
        return saturationPressureWater(Temp)
    else:
        return saturationPressureIce(Temp)