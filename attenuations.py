#Author: Andres Ortiz
import Formulas.basicFormulas as basicFormulas
import Formulas.linear_interpolation as linear_interpolation
import math

def specific_gaseous_attenuation(frequency, barometric_pressure, water_vapor_density, Temperature, OXD, WD, BC):
    es = basicFormulas.water_vapor_partial_pressure(water_vapor_density=water_vapor_density,temp=Temperature)
    ps = barometric_pressure-es
    NOXYGEN = basicFormulas.N_oxygen(frequency, dry_air_pressure=ps, water_vapor_partial_pressure=es, temp=Temperature,oxygen_data=OXD, basicCoeff=BC)
    NWATER = basicFormulas.N_waterVapor(frequency, dry_air_pressure=ps, water_vapor_partial_pressure=es, temp=Temperature, water_data=WD, basicCoeff=BC)
    gamma = 0.1820 * frequency * (NOXYGEN + NWATER)
    return gamma

def slantPath_instantanueousOxygen_attenuation(frequency, barometric_pressure, Temperature, water_vapor_density,elevation, OXD, BC, coi):
    es = basicFormulas.water_vapor_partial_pressure(water_vapor_density=water_vapor_density,temp=Temperature)
    ps = barometric_pressure-es
    gamma = 0.1820 * frequency * basicFormulas.N_oxygen(frequency=frequency, dry_air_pressure=ps, water_vapor_partial_pressure=es, temp=Temperature, oxygen_data=OXD, basicCoeff=BC)
    coefficients = getCoefficients(frequency,coi)
    h0 = coefficients.index(0)+coefficients.index(1)*Temperature+coefficients.index(2)*barometric_pressure+coefficients.index(3)*water_vapor_density
    A0 = (gamma*h0)/math.sin(elevation)
    return A0

def slantPath_instantanueousWater_attenuation(frequency, barometric_pressure, Temperature, water_vapor_density,elevation, WD, BC):
    es = basicFormulas.water_vapor_partial_pressure(water_vapor_density=water_vapor_density,temp=Temperature)
    ps = barometric_pressure-es
    gamma = 0.1820 * frequency * basicFormulas.N_waterVapor(frequency=frequency, dry_air_pressure=ps, water_vapor_partial_pressure=es, temp=Temperature, water_data=WD, basicCoeff=BC)
    freq_list = [22.235080, 183.310087, 325.152888] #GHZ
    a_list = [2.6846, 5.8905, 2.9810]
    b_list = [2.7649, 4.9219, 3.0748]
    hw = 5.6585 * math.pow(10,-5) * frequency + 1.8348
    for i in range (2):
        hw += a_list(i)/(math.pow(frequency-freq_list(i),2)+b_list(i))
    AW = (gamma * hw)/math.sin(elevation)
    return AW

class CoefficientsOfInterest:
    def __init__(self) -> None:
        self.frequency = []
        self.a = []
        self.b = []
        self.c = []
        self.d = []
        self.length = -1


def loadCoefficients():
    filepath = "./coefficientsOxygen.txt"
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