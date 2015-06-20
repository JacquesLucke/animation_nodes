from mathutils import Matrix

def composeMatrix(location, rotation, scale):
    matrix = Matrix.Translation(location)
    matrix *= Matrix.Rotation(rotation[2], 4, 'Z')
    matrix *= Matrix.Rotation(rotation[1], 4, 'Y')
    matrix *= Matrix.Rotation(rotation[0], 4, 'X')
    matrix *= Matrix.Scale(scale[0], 4, [1, 0, 0])
    matrix *= Matrix.Scale(scale[1], 4, [0, 1, 0])
    matrix *= Matrix.Scale(scale[2], 4, [0, 0, 1])
    return matrix

def findNearestParameterOnLine(linePosition, lineDirection, point):
    directionLength = lineDirection.length
    lineDirection = lineDirection.normalized()
    parameter = (lineDirection.dot(point - linePosition)) / directionLength
    return parameter  