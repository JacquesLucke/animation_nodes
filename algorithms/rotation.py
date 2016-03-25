

#### RotationToDirection 
'''
Converts euler to vector (direction or normal) with custom length

required arguments (as strings):
    input socket name: rotation (euler), length (float),
    output socket name: direction (vector)
    axis in ("X", "Y", "Z", "-X", "-Y", "-Z")
needs mathutils module
'''

def generateRotationToDirectionCode(rotationName, lengthName, directionOutputName, axis):
    directionAxisTuple = {"X": "({}, 0, 0)", "Y": "(0, {}, 0)", "Z": "(0, 0, {})",
                         "-X":"(-{}, 0, 0)","-Y": "(0,-{}, 0)","-Z": "(0, 0,-{})"}
    axisTuple = directionAxisTuple[axis].format(lengthName)
    
    return "{} = {}.to_matrix() * mathutils.Vector({})".format(directionOutputName, rotationName, axisTuple)

##############################


#### DirectionToRotation 
'''
Converts vector to rotation, with an extra guide vector 
(like to_track_quat(), but can specify custom UP axis (as guide))

required arguments (as strings):
    input socket name: direction (vector), guide (vector),
    trackAxis in ("X", "Y", "Z", "-X", "-Y", "-Z")
    guideAxis in ("X", "Y", "Z")
optional outputs / types (as strings):
    output socket names : matrix (matrix), rotation (euler), quaternion (quaternion)
     - will generate that output type if respective name is other than ""
    if no output is specified (all to ""), code will be ""
    this allows to generate that output only if needed (ex if respective socket is linked (isLinked dict))
needs mathutils module
'''

def generateDirectionToRotationCode(directionName, guideName, trackAxis, guideAxis, matrixOutputName = "", rotationOutputName = "", quaternionOutputName = ""):
    
    def getAxesChange(track, guide):
        if track == "X":    a = "( z,-y, x)" if guide == "Z" else "( z, x, y)"
        elif track == "Y":  a = "( y, z, x)" if guide == "Z" else "( x, z,-y)"
        elif track == "Z":  a = "( x, y, z)" if guide == "X" else "(-y, x, z)"
        elif track == "-X": a = "(-z, y, x)" if guide == "Z" else "(-z, x,-y)"
        elif track == "-Y": a = "(-y,-z, x)" if guide == "Z" else "( x,-z, y)"
        elif track == "-Z": a = "( x,-y,-z)" if guide == "X" else "( y, x,-z)"
        return a
    
    outputMatrix, outputEuler, outputQuaternion = False, False, False
    if matrixOutputName != "": outputMatrix = True
    if rotationOutputName != "": outputEuler = True
    if quaternionOutputName != "": outputQuaternion = True
    
    #### exception 0
    if not any([outputMatrix, outputEuler, outputQuaternion]):
        return ""
    
    #### exception 1
    if trackAxis[-1:] == guideAxis[-1:]:
        if outputMatrix: yield "{} = mathutils.Matrix()".format(matrixOutputName)
        if outputEuler: yield "{} = mathutils.Euler((0, 0, 0), 'XYZ')".format(rotationOutputName)
        if outputQuaternion: yield "{} = mathutils.Quaternion((1, 0, 0, 0))".format(quaternionOutputName)
        return

    #### exception 2
    yield "zero = mathutils.Vector((0, 0, 0))"

    yield "if {} == zero:".format(directionName)
    if outputMatrix: yield "    {} = mathutils.Matrix()".format(matrixOutputName)
    if outputEuler: yield "    {} = mathutils.Euler((0, 0, 0), 'XYZ')".format(rotationOutputName)
    if outputQuaternion: yield "    {} = mathutils.Quaternion((1, 0, 0, 0))".format(quaternionOutputName)

    # always same
    yield "else:"
    yield "    z = {}.normalized()".format(directionName)
    yield "    if {} != zero and z.cross({}) != zero: y = z.cross({}.normalized())".format(guideName, guideName, guideName)
    if "X" == guideAxis: yield "    else: y = z.cross(mathutils.Vector((1, 0, 0))) if z.cross(mathutils.Vector((1, 0, 0))) != zero else mathutils.Vector((0, 0, 1))"
    if "Y" == guideAxis: yield "    else: y = z.cross(mathutils.Vector((0, 1, 0))) if z.cross(mathutils.Vector((0, 1, 0))) != zero else mathutils.Vector((0, 0, 1))"
    if "Z" == guideAxis: yield "    else: y = z.cross(mathutils.Vector((0, 0, 1))) if z.cross(mathutils.Vector((0, 0, 1))) != zero else mathutils.Vector((0, 1, 0))"
    yield "    x = y.cross(z)"

    yield "    mx, my, mz = " + getAxesChange(trackAxis, guideAxis)

    yield "    mat = mathutils.Matrix()"
    yield "    mat.col[0].xyz, mat.col[1].xyz, mat.col[2].xyz = mx, my, mz"
                
    #### outputs
    if outputMatrix: yield "    {} = mat.normalized()".format(matrixOutputName)
    if outputEuler: yield "    {} = mat.to_euler()".format(rotationOutputName)
    if outputQuaternion: yield "    {} = mat.to_quaternion()".format(quaternionOutputName)

##############################
