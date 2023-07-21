#Author: Andres Ortiz


def linearInterpolation(input, x_values, y_values):
    x1, y1, x2, y2 = findNearestPoints(input, x_values, y_values)
    return y1 + (input - x1) * ((y2-y1)/(x2-x1))


def findNearestPoints(input, x_values, y_values):
    data_points = list(zip(x_values, y_values))
    data_points = sorted(data_points, key=lambda p: abs(input - p[0]))
    x1, y1 = data_points[0]
    x2, y2 = data_points[1]
    return x1, y1, x2, y2
