def findNearestParameterOnLine(linePosition, lineDirection, point):
    directionLength = lineDirection.length
    lineDirection = lineDirection.normalized()
    parameter = (lineDirection.dot(point - linePosition)) / directionLength
    return parameter