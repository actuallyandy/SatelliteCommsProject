#Author: Andres Ortiz
"""
Description: This file contians the underlying functions that are required to calculate 
the attenuation values in attenuation.py. The great majority of functions are contained
in the following report from the ITU:
https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.676-13-202208-I!!PDF-E.pdf
"""

import math
from enum import Enum
import Formulas.SpectralTable as SpectralTable
import Formulas.linear_interpolation as linear_interpolation

#This class exists because I want an more clear switch than 0 or 1
class Env(Enum):
    OXYGEN=0
    WATER=1

#Water Vapor Partial Pressure: e
#Dry Air Pressure: p
#Elevation Angle: theta

#Should be in hectopascals hPa
def water_vapor_partial_pressure(water_vapor_density, temp):
    return (water_vapor_density*temp)/216.7

#Should be hectopascals hPa
def dry_air_pressure(barometric_pressure, water_vapor_partial_pressure):
    return barometric_pressure - water_vapor_partial_pressure


#This functioin defines the imaginary part of the frequency dependent complex refractivities
#Equation: N"_Oxygen(f) = Sum_i(Si*Fi)+N"_D(f)
def N_oxygen(frequency, dry_air_pressure, water_vapor_partial_pressure, temp, oxygen_data):
    retVal = 0
    SpectralLineNum = oxygen_data.length
    ND = drycontinuum(frequency, dry_air_pressure, water_vapor_partial_pressure, temp)
    for i in range(SpectralLineNum):
        theta = 300/temp
        line_strength = lineStrengthOxygen(theta, dry_air_pressure, oxygen_data.a1[i], oxygen_data.a2[i])
        lineShapeFactor = lineShape_factor(type=Env.OXYGEN,index=i,frequency=frequency,
                                                temp=temp, dry_air_pressure=dry_air_pressure, 
                                                water_vapor_partial_pressure=water_vapor_partial_pressure,
                                                data=oxygen_data)
        retVal += line_strength*lineShapeFactor
    return retVal + ND

#This function defines the imaginary part of the frequency dependent complex refractivities
#Equation: N"_Water(f) = Sum_i(Si*Fi)
def N_waterVapor(frequency, dry_air_pressure, water_vapor_partial_pressure, temp, water_data):
    retVal = 0
    SpectralLineNum = water_data.length
    for i in range(SpectralLineNum):
        theta = 300/temp
        line_strength = lineStrengthWater(theta, water_vapor_partial_pressure, water_data.a1[i], water_data.a2[i])
        retVal += line_strength*lineShape_factor(type=Env.WATER, index=i, frequency=frequency, 
                                                temp=temp, dry_air_pressure=dry_air_pressure, 
                                                water_vapor_partial_pressure=water_vapor_partial_pressure, 
                                                data=water_data)
    return retVal

#This function defines the line strength based on a given table for oxygen coefficients
#Equation Si = a1E-7 * p * theta^3 * e^(a2(1-theta))
def lineStrengthOxygen(theta, dry_air_pressure, a1, a2):
    lineStrength = a1 * math.pow(10,-7) * dry_air_pressure * math.pow(theta, 3) * math.exp(a2*(1-theta))
    return lineStrength

#This function defines the line strength based on a given table for water vapor coefficients
#Equation Si = b1E-1 *e * theta ^ 3.5 * e^(b2(1-theta))
def lineStrengthWater(theta, water_vapor_partial_pressure, b1, b2):
    lineStrength = b1 * math.pow(10,-1) * water_vapor_partial_pressure * math.pow(theta,3.5) * math.exp(b2 * (1-theta)) 
    return lineStrength

#This function defines the line shape factor based on a table frequency and the input frequency.
#WARNING: AN assumption had to be made here for the inclusion of the abs function. The ITU report
#does not specify whether the function has absolute value applied to it or not. However, the output
#of this equation will be negative at certain frequencies which makes no sense. Therefore I'm assuming
#the adjustment factor will be abs'ed
#Equation: Fi = f/fi * [ dF-dirac(fi-f)/(fi-f)^2 +dF^2    +    dF-dirac(fi+f)/(fi+f)^2 + dF^2    ]
def lineShape_factor(type,index,frequency, temp, dry_air_pressure, water_vapor_partial_pressure, data):
    deltaF = ZeemanSplitting(type, index, dry_air_pressure, water_vapor_partial_pressure, temp, data)
    dirac = correctionFactor(type, temp, dry_air_pressure, water_vapor_partial_pressure, data, index)
    lineFreq = getLineFrequency(type, data, index)
    RHS_denom = math.pow(lineFreq+frequency,2) + math.pow(deltaF,2)
    RHS_numer = deltaF - dirac*(lineFreq+frequency)
    LHS_denom = math.pow(lineFreq - frequency, 2) + math.pow(deltaF,2)
    LHS_numer = deltaF - dirac*(lineFreq - frequency)
    RHS = RHS_numer/RHS_denom
    LHS = LHS_numer/LHS_denom
    prefix = frequency/lineFreq
    factor = prefix * (LHS + RHS) #Here is the assumptioni
    return factor

#This function calculates the Zeeman splitting
def ZeemanSplitting(type,index, dry_air_pressure, water_vapor_partial_pressure, temp, data):
    deltaF = lineWidth(type,temp,dry_air_pressure,water_vapor_partial_pressure, data, index)
    theta = 300/temp
    if (type == Env.OXYGEN):
        new_deltaF = math.sqrt(math.pow(deltaF,2) + 2.25 * math.pow(10,-6))
    else:
        new_deltaF = 0.525 * deltaF + math.sqrt(0.217 * math.pow(deltaF,2) + (2.1316 * math.pow(10,-12) * math.pow(getLineFrequency(Env.WATER,data,index),2)/theta))
    return new_deltaF

def lineWidth(type,temp, dry_air_pressure, water_vapor_partial_pressure, data, index):
    theta = 300/temp
    if (type == Env.OXYGEN):
        retVal = data.a3[index] * math.pow(10,-4) * (dry_air_pressure * math.pow(theta, 0.8-data.a4[index]) + 1.1 * water_vapor_partial_pressure * theta)
    else:
        retVal = data.a3[index] * math.pow(10,-4) * (dry_air_pressure * math.pow(theta, data.a4[index]) 
                                                     + data.a5[index] * water_vapor_partial_pressure * math.pow(theta, data.a6[index]))
    return retVal

def correctionFactor(type, temp, dry_air_pressure, water_vapor_partial_pressure, data, index):
    theta = 300/temp
    if (type == Env.OXYGEN):
        dirac = (data.a5[index] + data.a6[index] * theta) * math.pow(10,-4) * (dry_air_pressure+water_vapor_partial_pressure) * math.pow(theta,0.8)
    else:
        dirac = 0
    return dirac


def drycontinuum(frequency, dry_air_pressure, water_vapor_partial_pressure, temp):
    theta = temp/300
    d = width_parameter_debye(dry_air_pressure, water_vapor_partial_pressure, theta)
    L_denominator = d * (1 + math.pow(frequency/d,2))
    L = (6.14 * math.pow(10,-5)) / L_denominator
    R_denominator = 1 + (1.9 * math.pow(10,-5)* math.pow(frequency, 1.5))
    R_numerator = 1.4 * math.pow(10,-12) * dry_air_pressure * math.pow(theta, 1.5)
    R = R_numerator/R_denominator
    prefix = dry_air_pressure * frequency * math.pow(theta, 2)
    ND = prefix*(L+R)
    return ND

def width_parameter_debye(dry_air_pressure, water_vapor_partial_pressure, theta):
    return 5.6 * math.pow(10,-4) * (dry_air_pressure + water_vapor_partial_pressure)*math.pow(theta,0.8)


def getLineFrequency(type, data, index):
    if (type == Env.OXYGEN):
        return data.frequency[index]
    else:
        return data.frequency[index]


if __name__ == "__main__":
    print("Cheerio")
