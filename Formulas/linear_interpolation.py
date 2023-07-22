#Author: Andres Ortiz


def linearInterpolation(input, x_values, y_values):
    result = findExactPoint(input, x_values)
    if result is None:
        x1, y1, x2, y2 = findNearestPoints(input, x_values, y_values)
        return y1 + (input - x1) * ((y2-y1)/(x2-x1))
    else:
        return y_values[result]
    

def findExactPoint(input, x_values):
    for i, value in enumerate(x_values):
        if value == input:
            return i
    return None

def findNearestPoints(input, x_values, y_values):
    data_points = list(zip(x_values, y_values))
    for i, value in enumerate(x_values):
        if value > input:
            break
    x1, y1 = data_points[i-1]
    x2, y2 = data_points[i]
    return x1, y1, x2, y2
