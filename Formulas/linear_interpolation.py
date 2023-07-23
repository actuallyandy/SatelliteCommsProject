#Author: Andres Ortiz
#Description: This file contains functions that perform linear interpolation
#on the coefficients of interest for the attenuation functions.

#This function either finds the exact point in a table or performs a linear
#interpolation of the nearest two values
def linearInterpolation(input, x_values, y_values):
    result = findExactPoint(input, x_values)
    if result is None:
        x1, y1, x2, y2 = findNearestPoints(input, x_values, y_values)
        return y1 + (input - x1) * ((y2-y1)/(x2-x1))
    else:
        return y_values[result]
    
#This function finds the exact values in a list if it exists
def findExactPoint(input, x_values):
    for i, value in enumerate(x_values):
        if value == input:
            return i
    return None
#This function finds the nearest two points where the input point will
#be residing in between.
def findNearestPoints(input, x_values, y_values):
    data_points = list(zip(x_values, y_values))
    for i, value in enumerate(x_values):
        if value > input:
            break
    x1, y1 = data_points[i-1]
    x2, y2 = data_points[i]
    return x1, y1, x2, y2
