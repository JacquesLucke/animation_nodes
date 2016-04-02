from mathutils import Matrix, Vector

def rotationToDirection(rotation, axis = "X"):
    '''axis in ("X", "Y", "Z", "-X", "-Y", "-Z")'''
    return rotation.to_matrix() * axisVectorDict[axis]

def generateRotationMatrix(direction, guide, trackAxis = "Z", guideAxis = "X"):
    '''
    trackAxis in ("X", "Y", "Z", "-X", "-Y", "-Z")
    guideAxis in ("X", "Y", "Z")
    '''

    matrix = Matrix.Identity(4)

    if guideAxis[-1:] == trackAxis[-1:]:
        return matrix

    if direction == zero:
        return matrix

    z = direction.normalized()
    if guide != zero and z.cross(guide) != zero:
        y = z.cross(guide.normalized())
    else:
        if guideAxis == "X":
            if z.cross(xAxis) != zero: y = z.cross(xAxis)
            else: y = zAxis
        elif guideAxis == "Y":
            if z.cross(yAxis) != zero: y = z.cross(yAxis)
            else: y = zAxis
        elif guideAxis == "Z":
            if z.cross(zAxis) != zero: y = z.cross(zAxis)
            else: y = yAxis

    x = y.cross(z)

    mx, my, mz = changeAxesDict[(trackAxis, guideAxis)](x, y, z)
    matrix.col[0][:3] = mx
    matrix.col[1][:3] = my
    matrix.col[2][:3] = mz
    return matrix


changeAxesDict = {
    ( "X", "Z"): lambda x, y, z: ( z, -y,  x),
    ( "X", "Y"): lambda x, y, z: ( z,  x,  y),
    ( "Y", "Z"): lambda x, y, z: ( y,  z,  x),
    ( "Y", "X"): lambda x, y, z: ( x,  z, -y),

    ( "Z", "X"): lambda x, y, z: ( x,  y,  z),
    ( "Z", "Y"): lambda x, y, z: (-y,  x,  z),
    ("-X", "Z"): lambda x, y, z: (-z,  y,  x),
    ("-X", "Y"): lambda x, y, z: (-z,  x, -y),

    ("-Y", "Z"): lambda x, y, z: (-y, -z,  x),
    ("-Y", "X"): lambda x, y, z: ( x, -z,  y),
    ("-Z", "X"): lambda x, y, z: ( x, -y, -z),
    ("-Z", "Y"): lambda x, y, z: ( y,  x, -z),
}

zero = Vector((0, 0, 0))
xAxis = Vector((1, 0, 0))
yAxis = Vector((0, 1, 0))
zAxis = Vector((0, 0, 1))

axisVectorDict = {
     "X" : Vector(( 1,  0,  0)),
     "Y" : Vector(( 0,  1,  0)),
     "Z" : Vector(( 0,  0,  1)),
    "-X" : Vector((-1,  0,  0)),
    "-Y" : Vector(( 0, -1,  0)),
    "-Z" : Vector(( 0,  0, -1)),
}
