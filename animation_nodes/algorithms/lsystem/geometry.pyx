from cpython cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free

from ... math cimport *
from . symbol_string cimport *
from ... data_structures cimport (
    Vector3DList, EdgeIndicesList, FloatList, EdgeIndices, Matrix4x4List
)

from .. random cimport randomFloat_ScaledRange

cdef struct Turtle:
    Matrix3 orientation
    Vector3 position
    float width
    float stepSize
    int lastVertexIndex # -1 indicates that it does not exist

cdef struct TurtleStack:
    Turtle *turtles
    Py_ssize_t amount
    Py_ssize_t capacity

cdef geometryFromSymbolString(SymbolString symbols, Py_ssize_t seed = 0, dict defaults = {}):
    # Calculate default matrices to speedup the common case
    cdef float defaultAngle = defaults.get("Angle", 0)

    cdef Matrix3 defaultXRotation
    setRotationXMatrix(&defaultXRotation, defaultAngle)
    cdef Matrix3 defaultXRotationNeg
    setRotationXMatrix(&defaultXRotationNeg, -defaultAngle)

    cdef Matrix3 defaultYRotation
    setRotationYMatrix(&defaultYRotation, defaultAngle)
    cdef Matrix3 defaultYRotationNeg
    setRotationYMatrix(&defaultYRotationNeg, -defaultAngle)

    cdef Matrix3 defaultZRotation
    setRotationZMatrix(&defaultZRotation, defaultAngle)
    cdef Matrix3 defaultZRotationNeg
    setRotationZMatrix(&defaultZRotationNeg, -defaultAngle)


    cdef TurtleStack stack
    initTurtleStack(&stack)

    cdef TurtleStack availableStack
    initTurtleStack(&availableStack)

    cdef Turtle initialTurtle
    initTurtle(&initialTurtle)
    pushTurtle(&stack, initialTurtle)

    cdef Vector3DList vertices = Vector3DList()
    cdef EdgeIndicesList edges = EdgeIndicesList()
    cdef FloatList widths = FloatList()

    cdef Matrix4x4List statesJ = Matrix4x4List()
    cdef Matrix4x4List statesK = Matrix4x4List()
    cdef Matrix4x4List statesM = Matrix4x4List()

    cdef char c
    cdef void *command
    cdef Turtle *turtle
    cdef Py_ssize_t i = 0

    while i < symbols.length:
        turtle = peekTopTurtle(&stack)
        c = symbols.data[i]
        i += 1
        command = symbols.data + i

        if c == b"F":
            moveForward_Geo(turtle, <MoveForwardGeoCommand*>command, vertices, edges, widths)
            i += sizeof(MoveForwardGeoCommand)
        elif c == b"f":
            moveForward_NoGeo(turtle, <MoveForwardNoGeoCommand*>command)
            i += sizeof(MoveForwardNoGeoCommand)
        elif c == b"[":
            branchStart(&stack, turtle, &availableStack)
        elif c == b"]":
            branchEnd(&stack, &availableStack)
        elif c == b'"':
            scaleStepSize(turtle, <ScaleCommand*>command)
            i += sizeof(ScaleCommand)
        elif c == b"!":
            scaleWidth(turtle, <ScaleCommand*>command)
            i += sizeof(ScaleCommand)
        elif c == b"+":
            rotateRight(turtle, <RotateCommand*>command, defaultAngle, &defaultYRotation)
            i += sizeof(RotateCommand)
        elif c == b"-":
            rotateLeft(turtle, <RotateCommand*>command, defaultAngle, &defaultYRotationNeg)
            i += sizeof(RotateCommand)
        elif c == b"&":
            pitchUp(turtle, <RotateCommand*>command, defaultAngle, &defaultXRotation)
            i += sizeof(RotateCommand)
        elif c == b"^":
            pitchDown(turtle, <RotateCommand*>command, defaultAngle, &defaultXRotationNeg)
            i += sizeof(RotateCommand)
        elif c == b"\\":
            rollClockwise(turtle, <RotateCommand*>command, defaultAngle, &defaultZRotationNeg)
            i += sizeof(RotateCommand)
        elif c == b"/":
            rollCounterClockwise(turtle, <RotateCommand*>command, defaultAngle, &defaultZRotation)
            i += sizeof(RotateCommand)
        elif c == b"~":
            rotateRandom(turtle, <RotateCommand*>command, seed)
            i += sizeof(RotateCommand)
        elif c == b"T":
            applyTropism(turtle, <TropismCommand*>command)
            i += sizeof(TropismCommand)
        elif c == b"J":
            storeTurtleState(turtle, statesJ)
        elif c == b"K":
            storeTurtleState(turtle, statesK)
        elif c == b"M":
            storeTurtleState(turtle, statesM)
        elif c in (b"A", b"B", b"X", b"Y", b"Z"):
            pass
        else:
            raise Exception("unknown opcode")

        seed += 123

    cdef Turtle _turtle
    while stackHasElements(&stack):
        _turtle = popTurtle(&stack)
        freeTurtle(&_turtle)

    while stackHasElements(&availableStack):
        _turtle = popTurtle(&availableStack)
        freeTurtle(&_turtle)

    return vertices, edges, widths, statesJ, statesK, statesM

cdef inline void storeTurtleState(Turtle *turtle, Matrix4x4List matrices):
    cdef float size = turtle.stepSize
    cdef Matrix3 *s = &turtle.orientation
    cdef Matrix4 t

    t.a11, t.a12, t.a13, t.a14 = s.a11 * size, s.a12 * size, s.a13 * size, turtle.position.x
    t.a21, t.a22, t.a23, t.a24 = s.a21 * size, s.a22 * size, s.a23 * size, turtle.position.y
    t.a31, t.a32, t.a33, t.a34 = s.a31 * size, s.a32 * size, s.a33 * size, turtle.position.z
    t.a41, t.a42, t.a43, t.a44 = 0, 0, 0, 1

    matrices.append_LowLevel(t)

cdef inline void moveForward_Geo(Turtle *turtle, MoveForwardGeoCommand *command,
        Vector3DList vertices, EdgeIndicesList edges, FloatList widths):

    if turtle.lastVertexIndex == -1:
        vertices.append_LowLevel(turtle.position)
        turtle.lastVertexIndex = vertices.length - 1

    moveTurtleForward(turtle, command.distance * turtle.stepSize)

    vertices.append_LowLevel(turtle.position)

    edges.append_LowLevel(EdgeIndices(
        turtle.lastVertexIndex,
        vertices.length - 1))
    widths.append_LowLevel(turtle.width)

    turtle.lastVertexIndex = vertices.length - 1

cdef inline void moveForward_NoGeo(Turtle *turtle, MoveForwardNoGeoCommand *command):
    moveTurtleForward(turtle, command.distance * turtle.stepSize)
    turtle.lastVertexIndex = -1

cdef inline void rotateRight(Turtle *turtle, RotateCommand *command, float defaultAngle, Matrix3 *defaultRot):
    cdef Matrix3 rotation
    if command.angle == defaultAngle:
        transformOrientation_Local(turtle, defaultRot)
    else:
        setRotationYMatrix(&rotation, command.angle)
        transformOrientation_Local(turtle, &rotation)

cdef inline void rotateLeft(Turtle *turtle, RotateCommand *command, float defaultAngle, Matrix3 *defaultRot):
    cdef Matrix3 rotation
    if command.angle == defaultAngle:
        transformOrientation_Local(turtle, defaultRot)
    else:
        setRotationYMatrix(&rotation, -command.angle)
        transformOrientation_Local(turtle, &rotation)

cdef inline void pitchUp(Turtle *turtle, RotateCommand *command, float defaultAngle, Matrix3 *defaultRot):
    cdef Matrix3 rotation
    if command.angle == defaultAngle:
        transformOrientation_Local(turtle, defaultRot)
    else:
        setRotationXMatrix(&rotation, command.angle)
        transformOrientation_Local(turtle, &rotation)

cdef inline void pitchDown(Turtle *turtle, RotateCommand *command, float defaultAngle, Matrix3 *defaultRot):
    cdef Matrix3 rotation
    if command.angle == defaultAngle:
        transformOrientation_Local(turtle, defaultRot)
    else:
        setRotationXMatrix(&rotation, -command.angle)
        transformOrientation_Local(turtle, &rotation)

cdef inline void rollClockwise(Turtle *turtle, RotateCommand *command, float defaultAngle, Matrix3 *defaultRot):
    cdef Matrix3 rotation
    if command.angle == defaultAngle:
        transformOrientation_Local(turtle, defaultRot)
    else:
        setRotationZMatrix(&rotation, -command.angle)
        transformOrientation_Local(turtle, &rotation)

cdef inline void rollCounterClockwise(Turtle *turtle, RotateCommand *command, float defaultAngle, Matrix3 *defaultRot):
    cdef Matrix3 rotation
    if command.angle == defaultAngle:
        transformOrientation_Local(turtle, defaultRot)
    else:
        setRotationZMatrix(&rotation, command.angle)
        transformOrientation_Local(turtle, &rotation)

cdef inline void rotateRandom(Turtle *turtle, RotateCommand *command, Py_ssize_t seed):
    cdef Matrix3 rotation
    cdef Euler3 euler
    euler.order = 0
    euler.x = randomFloat_ScaledRange(seed + 0, command.angle)
    euler.y = randomFloat_ScaledRange(seed + 1, command.angle)
    euler.z = randomFloat_ScaledRange(seed + 2, command.angle)
    setRotationMatrix(&rotation, &euler)
    transformOrientation_Local(turtle, &rotation)

cdef inline void branchStart(TurtleStack *stack, Turtle *current, TurtleStack *availableStack):
    cdef Turtle turtle
    if stackHasElements(availableStack):
        turtle = popTurtle(availableStack)
    else:
        initTurtle(&turtle)
    initBranch(&turtle, current)
    pushTurtle(stack, turtle)

cdef inline void branchEnd(TurtleStack *stack, TurtleStack *availableStack):
    if stack.amount <= 1:
        return
    cdef Turtle turtle = popTurtle(stack)
    pushTurtle(availableStack, turtle)

cdef inline void scaleStepSize(Turtle *turtle, ScaleCommand *command):
    turtle.stepSize *= command.factor

cdef inline void scaleWidth(Turtle *turtle, ScaleCommand *command):
    turtle.width *= command.factor

cdef inline void applyTropism(Turtle *turtle, TropismCommand *command):
    cdef Vector3 forward = Vector3(turtle.orientation.a13, turtle.orientation.a23, turtle.orientation.a33)
    cdef Vector3 newForward = Vector3(forward.x, forward.y, forward.z - command.gravity)
    normalizeVec3_InPlace(&newForward)

    cdef float cosAngle = dotVec3(&forward, &newForward)
    if not (-0.999 < cosAngle < 0.999):
        return

    cdef Vector3 axis
    crossVec3(&axis, &forward, &newForward)
    normalizeVec3_InPlace(&axis)

    cdef Matrix3 rotation
    normalizedAxisCosAngleToMatrix(&rotation, &axis, cosAngle)
    transformOrientation_Global(turtle, &rotation)



# Turtle Utilities
##########################################

cdef void initTurtle(Turtle *turtle):
    setIdentityMatrix(&turtle.orientation)
    turtle.position = Vector3(0, 0, 0)
    turtle.stepSize = 1
    turtle.width = 1
    turtle.lastVertexIndex = -1

cdef void freeTurtle(Turtle *turtle):
    pass

cdef void initBranch(Turtle *turtle, Turtle *source):
    turtle.orientation = source.orientation
    turtle.position = source.position
    turtle.stepSize = source.stepSize
    turtle.width = source.width
    turtle.lastVertexIndex = source.lastVertexIndex

cdef inline void moveTurtleForward(Turtle *turtle, float distance):
    turtle.position.x += turtle.orientation.a13 * distance
    turtle.position.y += turtle.orientation.a23 * distance
    turtle.position.z += turtle.orientation.a33 * distance

cdef inline void transformOrientation_Local(Turtle *turtle, Matrix3 *rotation):
    cdef Matrix3 newOrientation
    multMatrix3(&newOrientation, &turtle.orientation, rotation)
    turtle.orientation = newOrientation

cdef inline void transformOrientation_Global(Turtle *turtle, Matrix3 *rotation):
    cdef Matrix3 newOrientation
    multMatrix3(&newOrientation, rotation, &turtle.orientation)
    turtle.orientation = newOrientation


# Turtle Stack Utilities
#############################################

cdef void initTurtleStack(TurtleStack *stack):
    cdef Py_ssize_t DEFAULT_SIZE = 4
    stack.amount = 0
    stack.capacity = DEFAULT_SIZE
    stack.turtles = <Turtle*>PyMem_Malloc(DEFAULT_SIZE * sizeof(Turtle))

cdef void freeTurtleStack(TurtleStack *stack, bint freeTurtles = False):
    cdef Py_ssize_t i
    if freeTurtles:
        for i in range(stack.amount):
            freeTurtle(stack.turtles + i)
    PyMem_Free(stack.turtles)

cdef inline void pushTurtle(TurtleStack *stack, Turtle turtle):
    if stack.amount == stack.capacity:
        growTurtleStack(stack)
    stack.turtles[stack.amount] = turtle
    stack.amount += 1

cdef inline Turtle *peekTopTurtle(TurtleStack *stack):
    if stack.amount > 0:
        return stack.turtles + stack.amount - 1
    else:
        return NULL

cdef inline Turtle popTurtle(TurtleStack *stack):
    # undefined behavior when the stack is empty
    stack.amount -= 1
    return stack.turtles[stack.amount]

cdef inline void growTurtleStack(TurtleStack *stack):
    cdef Py_ssize_t newCapacity = stack.capacity * 2
    stack.turtles = <Turtle*>PyMem_Realloc(stack.turtles, newCapacity * sizeof(Turtle))
    stack.capacity = newCapacity

cdef inline bint stackHasElements(TurtleStack *stack):
    return stack.amount > 0
