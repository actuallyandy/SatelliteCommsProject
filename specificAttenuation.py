
#Author: Andres Ortiz

import math
from enum import Enum
import SpectralTable

class Env(Enum):
    OXYGEN=0
    WATER=1

#Water Vapor Partial Pressure: e
#Dry Air Pressure: p
#Elevation Angle: theta

def water_vapor_partial_pressure(water_vapor_density, temp):
    return (water_vapor_density*temp)/216.7

def dry_air_pressure(barometric_pressure, water_vapor_partial_pressure):
    return barometric_pressure - water_vapor_partial_pressure

def specific_gaseous_attenuation(frequency, dry_air_pressure, water_vapor_partial_pressure, temp):
    NOXYGEN = N_oxygen(frequency, dry_air_pressure, water_vapor_partial_pressure, temp)
    NWATER = N_waterVapor(frequency, dry_air_pressure, water_vapor_partial_pressure, temp)
    gamma = 0.1820 * (NOXYGEN + NWATER)
    return gamma


def N_oxygen(frequency, dry_air_pressure, water_vapor_partial_pressure, temp):
    retVal = 0
    SpectralLineNum = SpectralTable.Oxygen.length
    ND = drycontinuum(frequency, dry_air_pressure, water_vapor_partial_pressure, temp)
    for i in range(SpectralLineNum):
        theta = 300/temp
        lineStrength = a1 * math.pow(10,-7) * dry_air_pressure * math.pow(theta, 3) * math.exp(a2*(1-theta))
        retVal += lineStrength*lineShape_factor(type=Env.OXYGEN,index=i,frequency=frequency,
                                                temp=temp, dry_air_pressure=dry_air_pressure, water_vapor_partial_pressure=water_vapor_partial_pressure) + ND
    return retVal

def N_waterVapor(frequency, dry_air_pressure, water_vapor_partial_pressure, temp):
    retVal = 0
    SpectralLineNum = SpectralTable.Water.length
    for i in range(SpectralLineNum):
        theta = 300/temp
        lineStrength = b1 * math.pow(10,-1) * water_vapor_partial_pressure * math.pow(theta,3.5) * math.exp(b2 * (1-theta))
        retVal += lineStrength*lineShape_factor(type=Env.WATER, index=i, frequency=frequency, 
                                                temp=temp, dry_air_pressure=dry_air_pressure, water_vapor_partial_pressure=water_vapor_partial_pressure)
    return retVal

def lineShape_factor(type,index,frequency, temp, dry_air_pressure, water_vapor_partial_pressure):
    deltaF = ZeemanSplitting(type, index, dry_air_pressure, water_vapor_partial_pressure, temp)
    dirac = correctionFactor(type, temp, dry_air_pressure, water_vapor_partial_pressure)
    lineFreq = getLineFrequency(type, index)
    RHS_denom = math.pow(lineFreq+frequency,2) + math.pow(deltaF,2)
    RHS_numer = deltaF - dirac*(lineFreq+frequency)
    LHS_denom = math.pow(lineFreq - frequency, 2) + math.pow(deltaF,2)
    LHS_numer = deltaF - dirac*(lineFreq - frequency)
    RHS = RHS_numer/RHS_denom
    LHS = LHS_numer/LHS_denom
    prefix = frequency/lineFreq

    factor = prefix * (LHS + RHS)
    return factor

def ZeemanSplitting(type,index, dry_air_pressure, water_vapor_partial_pressure, temp):
    deltaF = lineWidth(type,temp,dry_air_pressure,water_vapor_partial_pressure)
    theta = 300/temp
    if (type == Env.OXYGEN):
        new_deltaF = math.sqrt(math.pow(deltaF,2) + 2.25 * math.pow(10,-6))
    else:
        new_deltaF = 0.525 * deltaF + math.sqrt(0.217 * math.pow(deltaF,2) + (2.1316 * math.pow(10,-12) * math.pow(getLineFrequency(Env.WATER,index),2)/theta))
    return new_deltaF

def lineWidth(type,temp, dry_air_pressure, water_vapor_partial_pressure):
    theta = 300/temp
    if (type == Env.OXYGEN):
        retVal = a3 * math.pow(10,-4) * (dry_air_pressure * math.pow(theta, 0.8-a4) + 1.1 * water_vapor_partial_pressure * theta)
    else:
        retVal = b3 * math.pow(10,-4) * (dry_air_pressure * math.pow(theta, b4) + b5 * water_vapor_partial_pressure * math.pow(theta, b6))
    return retVal

def correctionFactor(type, temp, dry_air_pressure, water_vapor_partial_pressure):
    theta = 300/temp
    if (type == Env.OXYGEN):
        dirac = (a5 + a6 * theta) * math.pow(10,-4) * (dry_air_pressure+water_vapor_partial_pressure) * math.pow(theta,0.8)
    else:
        dirac = 0
    return dirac

def width_parameter_debye(dry_air_pressure, water_vapor_partial_pressure, elevation_angle):
    return 5.6 * math.pow(10,-4) * (dry_air_pressure + water_vapor_partial_pressure)*math.pow(elevation_angle,0.8)


def drycontinuum(frequency, dry_air_pressure, water_vapor_partial_pressure, temp):
    theta = temp/300
    d = width_parameter_debye(dry_air_pressure, water_vapor_partial_pressure, theta)
    L_denominator = d * (1 + math.pow(frequency/d,2))
    L = (6.14 * math.pow(10,-5)) / L_denominator
    R_denominator = 1 + (1.9 * math.pow(10,-5)* math.pow(frequency, 1.5))
    R_numerator = 1.4 * math.pow(10,-12) * dry_air_pressure * math.pow(theta, 1.5)
    R = R_numerator/R_denominator
    prefix = dry_air_pressure * frequency * math.pow(theta, 2)
    ND = prefix(L+R)
    return ND

def getLineFrequency(type, index):
    if (type == Env.OXYGEN):
        return SpectralTable.Oxygen.frequency[index]
    else:
        return SpectralTable.Water.frequency[index]


if __name__ == "__main__":
    print("Cheerio")
