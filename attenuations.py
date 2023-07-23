#Author: Andres Ortiz
import Formulas.basicFormulas as basicFormulas
import Formulas.linear_interpolation as linear_interpolation
import math

"""
Coefficient of Oxygen valid for 50.474214 to 834.145546 GHZ
Coefficient of Water valid for 22.235080 to 1 780 GHZ
COI for Oxygen valid for 1.00  to 350 GHZ
"""

#This function calculates the specific gaseous attenuation due to dry air and water vapor
#Equation: y = 0.1820*f*(N"_ox(f)+N"_wv(f))
#Valid frequency Range 50.474214 to 834.145546 GHZ
def specific_gaseous_attenuation(frequency, barometric_pressure, water_vapor_density, Temperature, OXD, WD):
    es = basicFormulas.water_vapor_partial_pressure(water_vapor_density=water_vapor_density,temp=Temperature)
    ps = barometric_pressure-es
    NOXYGEN = basicFormulas.N_oxygen(frequency, dry_air_pressure=ps, water_vapor_partial_pressure=es, temp=Temperature,oxygen_data=OXD)
    NWATER = basicFormulas.N_waterVapor(frequency, dry_air_pressure=ps, water_vapor_partial_pressure=es, temp=Temperature, water_data=WD)
    gamma = 0.1820 * frequency * (NOXYGEN + NWATER)
    return gamma

#This function calculates the slant path instantaneous gaseous attenuation attributable to oxygen.
#Equation: A0 = y0*h0/sin(theta)
#Equation h0 = a0 +b0*T + c0*P +d0*wvd  These coefficients have to be interpolated
#Valid frequency Range 50.474214 to 350 GHZ
def slantPath_instantanueousOxygen_attenuation(frequency, barometric_pressure, Temperature, water_vapor_density,elevation, OXD, coi):
    es = basicFormulas.water_vapor_partial_pressure(water_vapor_density=water_vapor_density,temp=Temperature)
    ps = barometric_pressure-es
    gamma = 0.1820 * frequency * basicFormulas.N_oxygen(frequency=frequency, dry_air_pressure=ps, water_vapor_partial_pressure=es, temp=Temperature, oxygen_data=OXD)
    coefficients = getCoefficients(frequency,coi)
    h0 = coefficients[0]+coefficients[1]*Temperature+coefficients[2]*barometric_pressure+coefficients[3]*water_vapor_density
    A0 = (gamma*h0)/math.sin(math.radians(elevation))
    return A0

#This function calculates the slant path instantaneous gaseous attenuation attributable to water vapor
#Equation: Aw = yw*hw/sin(theta)
#Equation: hw = Af+B + sum (ai/(f-fi)^2 +bi)
#Valid frequency Range 22.235080 to 1780 GHz
def slantPath_instantanueousWater_attenuation(frequency, barometric_pressure, Temperature, water_vapor_density,elevation, WD):
    es = basicFormulas.water_vapor_partial_pressure(water_vapor_density=water_vapor_density,temp=Temperature)
    ps = barometric_pressure-es
    gamma = 0.1820 * frequency * basicFormulas.N_waterVapor(frequency=frequency, dry_air_pressure=ps, water_vapor_partial_pressure=es, temp=Temperature, water_data=WD)
    freq_list = [22.235080, 183.310087, 325.152888] #GHZ
    a_list = [2.6846, 5.8905, 2.9810]
    b_list = [2.7649, 4.9219, 3.0748]
    hw = 5.6585 * math.pow(10,-5) * frequency + 1.8348
    for i in range (2):
        hw += a_list[i]/(math.pow(frequency-freq_list[i],2)+b_list[i])
    AW = (gamma * hw)/math.sin(math.radians(elevation))
    return AW
#This class holds a list of coefficients to calculate slant path values via interpolation
class CoefficientsOfInterest:
    def __init__(self) -> None:
        self.frequency = []
        self.a = []
        self.b = []
        self.c = []
        self.d = []
        self.length = -1
#This function reads in the coefficients of interest file
def loadCoefficients():
    filepath = "./coefficientsOfInterestOxygen.txt"
    coi = CoefficientsOfInterest()
    with open(filepath, "r") as file:
        line = file.readline()
        while line:    
            entry_array = line.split(" ")
            coi.frequency.append(float(entry_array[0]))
            coi.a.append(float(entry_array[1]))
            coi.b.append(float(entry_array[2]))
            coi.c.append(float(entry_array[3]))
            coi.d.append(float(entry_array[4]))
            line = file.readline()
    coi.length = len(coi.frequency)
    return coi

#This function will perform a linear interpolation to calculate coefficients 
#required for the slant path oxygen equation
def getCoefficients(frequency, coi):
    x_points = coi.frequency
    a_points = coi.a
    b_points = coi.b 
    c_points = coi.c
    d_points = coi.d
    a = linear_interpolation.linearInterpolation(frequency, x_values=x_points, y_values=a_points)
    b = linear_interpolation.linearInterpolation(frequency, x_values=x_points, y_values=b_points)
    c = linear_interpolation.linearInterpolation(frequency, x_values=x_points, y_values=c_points)
    d = linear_interpolation.linearInterpolation(frequency, x_values=x_points, y_values=d_points)
    return a,b,c,d