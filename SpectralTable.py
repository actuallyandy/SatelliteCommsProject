#Author: Andres Ortiz
#Description: Table for spectroscopic oxygen and water attenuation
#Preface: This is not a good way to code this, but I am short on time and I'm copying these values from this pdf: 
#https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.676-13-202208-I!!PDF-E.pdf

import linear_interpolation


class Oxygen:
    def __init__(self) -> None:
        self.frequency = []
        self.a1 = []
        self.a2 = []
        self.a3 = []
        self.a4 = []
        self.a5 = []
        self.a6 = []
        self.length = -1

class Water:
    def __init__(self) -> None:
        self.frequency = []
        self.a1 = []
        self.a2 = []
        self.a3 = []
        self.a4 = []
        self.a5 = []
        self.a6 = []
        self.length = -1

def loadOxygenData():
    filepath = "./coefficientsOxygen.txt"
    oxygen = Oxygen()
    with open(filepath, "r") as file:
        line = file.readline()
        while line:    
            entry_array = line.split(" ")
            oxygen.frequency.append(float(entry_array[0]))
            oxygen.a1.append(float(entry_array[1]))
            oxygen.a2.append(float(entry_array[2]))
            oxygen.a3.append(float(entry_array[3]))
            oxygen.a4.append(float(entry_array[4]))
            oxygen.a5.append(float(entry_array[5]))
            oxygen.a6.append(float(entry_array[6]))
            line = file.readline()
    oxygen.length = len(oxygen.frequency)
    return oxygen

def loadWaterData():
    filepath = "./coefficientsWater.txt"
    water = Water()
    with open(filepath, "r") as file:
        line = file.readline()
        while line:
            entry_array = line.split(" ")
            water.frequency.append(float(entry_array[0]))
            water.a1.append(float(entry_array[1]))
            water.a2.append(float(entry_array[2]))
            water.a3.append(float(entry_array[3]))
            water.a4.append(float(entry_array[4]))
            water.a5.append(float(entry_array[5]))
            water.a6.append(float(entry_array[6]))
            line = file.readline()
    water.length = len(water.frequency)
    return water

def interpolateCoefficients(frequency, data):
    if isinstance(data, Oxygen):
        if frequency<data.frequency[0] or frequency>data.frequency[data.length-1]:
            return False, False, False, False, False, False
        else:
            a1 = linear_interpolation.linearInterpolation(frequency, data.frequency, data.a1)
            a2 = linear_interpolation.linearInterpolation(frequency, data.frequency, data.a2)
            a3 = linear_interpolation.linearInterpolation(frequency, data.frequency, data.a3)
            a4 = linear_interpolation.linearInterpolation(frequency, data.frequency, data.a4)
            a5 = linear_interpolation.linearInterpolation(frequency, data.frequency, data.a5)
            a6 = linear_interpolation.linearInterpolation(frequency, data.frequency, data.a6)
            return a1, a2, a3, a4, a5, a6
    elif isinstance(data, Oxygen):
        if frequency<data.frequency[0] or frequency>data.frequency[data.length-1]:
            return False, False, False, False, False, False
        else:
            b1 = linear_interpolation.linearInterpolation(frequency, data.frequency, data.b1)
            b2 = linear_interpolation.linearInterpolation(frequency, data.frequency, data.b2)
            b3 = linear_interpolation.linearInterpolation(frequency, data.frequency, data.b3)
            b4 = linear_interpolation.linearInterpolation(frequency, data.frequency, data.b4)
            b5 = linear_interpolation.linearInterpolation(frequency, data.frequency, data.b5)
            b6 = linear_interpolation.linearInterpolation(frequency, data.frequency, data.b6)
            return b1, b2, b3, b4, b5, b6
    else:
        return False, False, False, False, False, False





if __name__ == "__main__":
    oxygen_data = loadOxygenData()
    water_data  = loadWaterData()
    a1, a2, a3, a4, a5, a6 = interpolateCoefficients(68, oxygen_data)
    print("Cheerio")



    