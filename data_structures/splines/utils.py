def findNearestParameterOnLine(linePosition, lineDirection, point):
    directionLength = lineDirection.length
    lineDirection = lineDirection.normalized()
    if directionLength == 0: return 0
    parameter = (lineDirection.dot(point - linePosition)) / directionLength # can cause division by zero
    return parameter
