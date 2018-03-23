import bpy
import re
from collections import Counter
from ... base_types import AnimationNode
from ... algorithms.random cimport uniformRandomFloat

from libc.string cimport memcpy, memset
from libc.math cimport M_PI as PI
from cpython cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free

from ... data_structures cimport (
    Vector3DList, EdgeIndices, EdgeIndicesList, Mesh
)
from ... math cimport (
    Matrix4, setIdentityMatrix, Vector3, setTranslationMatrix, multMatrix4, toPyVector3,
    setRotationXMatrix, setRotationYMatrix, setRotationZMatrix, Matrix3, addVec3_Inplace,
    multMatrix3, transformVec3AsDirection_InPlace, setRotationMatrix, Euler3,
    normalizedAxisAngleToMatrix, crossVec3, normalizeVec3_InPlace, lengthVec3,
    dotVec3
)

cdef float degToRadFactor = PI / 180.0

class LSystemNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_LSystemNode"
    bl_label = "L System"
    errorHandlingType = "EXCEPTION"

    def create(self):
        self.newInput("Text", "Axiom", "axiom")
        self.newInput("Generic", "Rules", "rules")
        self.newInput("Integer", "Generations", "generations")
        self.newInput("Float", "Step Size", "stepSize", value = 1)
        self.newInput("Float", "Angle", "angle", value = 90)
        self.newInput("Float", "Random Angle", "randomAngle", value = 180)
        self.newInput("Float", "Scale Step Size", "scaleStepSize", value = 0.9)
        self.newInput("Float", "Gravity", "gravity", value = 0)
        self.newOutput("Mesh", "Mesh", "mesh")

    def execute(self, axiom, rules, generations, stepSize, angle, randomAngle, scaleStepSize, gravity):
        defaults = {
            "Step Size" : stepSize,
            "Angle" : angle,
            "Random Angle" : randomAngle,
            "Scale Step Size" : scaleStepSize,
            "Gravity" : gravity
        }

        cdef SymbolString _axiom = parseSymbolString(axiom, defaults)

        cdef RuleSet ruleSet
        initRuleSet(&ruleSet, rules, defaults)

        cdef SymbolString symbols = applyGrammarRules(_axiom, ruleSet, generations)

        freeRuleSet(&ruleSet)
        freeSymbolString(&_axiom)

        mesh = geometryFromSymbolString(symbols)

        freeSymbolString(&symbols)

        return mesh


# Parse Input
##################################################

cdef struct SymbolString:
    unsigned char *data
    Py_ssize_t length
    Py_ssize_t capacity

cdef struct NoArgCommand:
    char dummy
cdef struct MoveForwardGeoCommand:
    float distance
cdef struct MoveForwardNoGeoCommand:
    float distance
cdef struct RotateCommand:
    float angle
cdef struct ScaleStepSizeCommand:
    float factor
cdef struct TropismCommand:
    float gravity

ctypedef fused Command:
    NoArgCommand
    MoveForwardGeoCommand
    MoveForwardNoGeoCommand
    RotateCommand
    ScaleStepSizeCommand
    TropismCommand

cdef SymbolString parseSymbolString(str source, dict defaults) except *:
    cdef SymbolString symbols
    initSymbolString(&symbols)

    cdef Py_ssize_t size
    cdef Py_ssize_t i = 0
    while i < len(source):
        c = source[i]
        if c == "F":
            size = parse_MoveForward_Geo(&symbols, source, i, defaults["Step Size"])
        elif c == "f":
            size = parse_MoveForward_NoGeo(&symbols, source, i, defaults["Step Size"])
        elif c in ("+", "-", "&", "^", "/", "\\"):
            size = parse_Rotate(&symbols, source, i, c, defaults["Angle"])
        elif c == "~":
            size = parse_Rotate(&symbols, source, i, c, defaults["Random Angle"])
        elif c == "[":
            size = parse_BranchStart(&symbols)
        elif c == "]":
            size = parse_BranchEnd(&symbols)
        elif c == '"':
            size = parse_ScaleStepSize(&symbols, source, i, defaults["Scale Step Size"])
        elif c == "T":
            size = parse_Tropism(&symbols, source, i, defaults["Gravity"])
        elif c == "A":
            size = parse_SingleLetter(&symbols, c)
        else:
            size = 1

        i += size

    return symbols

cdef parse_MoveForward_Geo(SymbolString *symbols, str source, Py_ssize_t index, float default):
    (distance,), argLength = parseArguments(source, index + 1, ["float"])
    if distance is None: distance = default
    appendSymbol(symbols, ord("F"), MoveForwardGeoCommand(<float>distance))
    return argLength + 1

cdef parse_MoveForward_NoGeo(SymbolString *symbols, str source, Py_ssize_t index, float default):
    (distance,), argLength = parseArguments(source, index + 1, ["float"])
    if distance is None: distance = default
    appendSymbol(symbols, ord("f"), MoveForwardNoGeoCommand(<float>distance))
    return argLength + 1

cdef parse_Rotate(SymbolString *symbols, str source, Py_ssize_t index, letter, float default):
    (angle,), argLength = parseArguments(source, index + 1, ["float"])
    if angle is None: angle = default
    angle *= degToRadFactor
    appendSymbol(symbols, ord(letter), RotateCommand(<float>angle))
    return argLength + 1

cdef parse_BranchStart(SymbolString *symbols):
    appendNoArgSymbol(symbols, ord("["))
    return 1

cdef parse_BranchEnd(SymbolString *symbols):
    appendNoArgSymbol(symbols, ord("]"))
    return 1

cdef parse_ScaleStepSize(SymbolString *symbols, str source, Py_ssize_t index, float default):
    (factor,), argLength = parseArguments(source, index + 1, ["float"])
    if factor is None: factor = default
    appendSymbol(symbols, ord('"'), ScaleStepSizeCommand(<float>factor))
    return argLength + 1

cdef parse_Tropism(SymbolString *symbols, str source, Py_ssize_t index, float default):
    (gravity,), argLength = parseArguments(source, index + 1, ["float"])
    if gravity is None: gravity = default
    appendSymbol(symbols, ord("T"), TropismCommand(<float>gravity))
    return argLength + 1

cdef parse_SingleLetter(SymbolString *symbols, letter):
    appendNoArgSymbol(symbols, ord(letter))
    return 1


cdef parseArguments(str source, Py_ssize_t index, argTypes):
    if letterAtIndexIs(source, index, "("):
        try: endBracketIndex = source.index(")", index)
        except: raise Exception("expected ')' to close the argument list")

        argStrings = source[index + 1:endBracketIndex].split(",")
        argStrings = [s.strip() for s in argStrings]
        if len(argStrings) > len(argTypes):
            raise Exception("too many arguments")

        args = []
        for argString, argType in zip(argStrings, argTypes):
            if len(argString) == 0:
                value = None
            elif argType == "float":
                value = float(argString)
            elif argType == "int":
                value = int(argString)
            args.append(value)

        return args + [None] * (len(argTypes) - len(args)), endBracketIndex - index + 1
    else:
        return [None] * len(argTypes), 0


cdef bint letterAtIndexIs(str source, Py_ssize_t index, str letter):
    if index < len(source):
        return letter == source[index]
    else:
        return False


# Symbol String Utilities
##################################

cdef void initSymbolString(SymbolString *symbols):
    cdef Py_ssize_t DEFAULT_SIZE = 1
    symbols.data = <unsigned char*>PyMem_Malloc(DEFAULT_SIZE)
    symbols.length = 0
    symbols.capacity = DEFAULT_SIZE

cdef void freeSymbolString(SymbolString *symbols):
    PyMem_Free(symbols.data)

cdef void copySymbolString(SymbolString *target, SymbolString *source):
    target.data = <unsigned char*>PyMem_Malloc(source.length)
    memcpy(target.data, source.data, source.length)
    target.length = source.length
    target.capacity = source.length

cdef void growSymbolString(SymbolString *symbols, Py_ssize_t minIncrease):
    cdef Py_ssize_t newCapacity = symbols.capacity * 2 + minIncrease
    symbols.data = <unsigned char*>PyMem_Realloc(symbols.data, newCapacity)
    symbols.capacity = newCapacity

cdef void appendSymbol(SymbolString *symbols, unsigned char prefix, Command command):
    cdef Py_ssize_t size = 1 + sizeof(Command)
    if symbols.length + size > symbols.capacity:
        growSymbolString(symbols, size)

    symbols.data[symbols.length] = prefix
    symbols.length += 1

    if Command is not NoArgCommand:
        memcpy(symbols.data + symbols.length, &command, sizeof(Command))
        symbols.length += sizeof(Command)

cdef void appendNoArgSymbol(SymbolString *symbols, unsigned char prefix):
    appendSymbol(symbols, prefix, NoArgCommand(0))

cdef appendSymbolBuffer(SymbolString *symbols, void *buffer, Py_ssize_t length):
    if symbols.length + length > symbols.capacity:
        growSymbolString(symbols, length)
    memcpy(symbols.data + symbols.length, buffer, length)
    symbols.length += length



# Apply Grammar Rules
######################################

cdef struct Rule:
    SymbolString replacement

cdef struct RuleSet:
    Rule **rules
    unsigned char *lengths

cdef SymbolString applyGrammarRules(SymbolString axiom, RuleSet rules, generations):
    cdef SymbolString currentGeneration
    cdef SymbolString nextGeneration

    copySymbolString(&currentGeneration, &axiom)

    for i in range(generations):
        nextGeneration = applyGrammarRules_OneGeneration(currentGeneration, rules)
        freeSymbolString(&currentGeneration)
        currentGeneration = nextGeneration

    return currentGeneration

cdef SymbolString applyGrammarRules_OneGeneration(SymbolString source, RuleSet rules):
    cdef SymbolString generated
    initSymbolString(&generated)

    cdef SymbolString *replacement

    cdef Py_ssize_t i = 0
    cdef unsigned char c
    cdef void *command
    while i < source.length:
        c = source.data[i]
        i += 1
        command = source.data + i
        if c in ("[", "]"):
            appendNoArgSymbol(&generated, c)
            i += 0
        elif c in ("+", "-", "&", "^", "\\", "/", "~"):
            appendSymbol(&generated, c, (<RotateCommand*>command)[0])
            i += sizeof(RotateCommand)
        elif c == '"':
            appendSymbol(&generated, c, (<ScaleStepSizeCommand*>command)[0])
            i += sizeof(ScaleStepSizeCommand)
        elif c == "F":
            appendSymbol(&generated, c, (<MoveForwardGeoCommand*>command)[0])
            i += sizeof(MoveForwardGeoCommand)
        elif c == "f":
            appendSymbol(&generated, c, (<MoveForwardNoGeoCommand*>command)[0])
            i += sizeof(MoveForwardNoGeoCommand)
        elif c == "A":
            replacement = getReplacement(&rules, c)
            appendSymbolBuffer(&generated, replacement.data, replacement.length)

    return generated


cdef initRuleSet(RuleSet *ruleSet, rules, defaults):
    ruleSet.rules = <Rule**>PyMem_Malloc(256 * sizeof(Rule*))
    memset(ruleSet.rules, 0, 256 * sizeof(Rule*))

    ruleSet.lengths = <unsigned char*>PyMem_Malloc(256 * sizeof(unsigned char))
    memset(ruleSet.lengths, 0, 256 * sizeof(unsigned char))

    counter = Counter([r[0] for r in rules])
    for symbol, amount in counter.items():
        ruleSet.lengths[ord(symbol)] = amount
        ruleSet.rules[ord(symbol)] = <Rule*>PyMem_Malloc(amount * sizeof(Rule))

    cdef unsigned char insertedAmount[256]
    memset(insertedAmount, 0, 256)

    cdef Rule *rule
    for symbol, replacement in rules:
        rule = ruleSet.rules[ord(symbol)] + insertedAmount[ord(symbol)]
        rule.replacement = parseSymbolString(replacement, defaults)
        insertedAmount[ord(symbol)] += 1

cdef freeRuleSet(RuleSet *ruleSet):
    cdef Py_ssize_t symbol, j
    for symbol in range(256):
        for j in range(ruleSet.lengths[symbol]):
            freeRule(ruleSet.rules[symbol] + j)
        if ruleSet.lengths[symbol] > 0:
            PyMem_Free(ruleSet.rules[symbol])
    PyMem_Free(ruleSet.rules)
    PyMem_Free(ruleSet.lengths)

cdef freeRule(Rule *rule):
    freeSymbolString(&rule.replacement)

cdef SymbolString *getReplacement(RuleSet *rules, unsigned char symbol):
    if rules.lengths[symbol] > 0:
        return &(rules.rules[symbol] + 0).replacement
    else:
        return NULL


# Create Geometry from SymbolString
################################################

cdef struct Turtle:
    Matrix3 orientation
    Vector3 position
    float stepSize
    bint currentPositionStored

    Py_ssize_t pointAmount
    Py_ssize_t pointCapacity
    Vector3 *points

    Py_ssize_t edgeAmount
    Py_ssize_t edgeCapacity
    EdgeIndices *edges

cdef struct TurtleStack:
    Turtle *turtles
    Py_ssize_t amount
    Py_ssize_t capacity

cdef geometryFromSymbolString(SymbolString symbols):
    cdef TurtleStack stack
    initTurtleStack(&stack)

    cdef Turtle initialTurtle
    initTurtle(&initialTurtle)
    pushTurtle(&stack, initialTurtle)

    cdef TurtleStack allTurtles
    initTurtleStack(&allTurtles)

    cdef char c
    cdef void *command
    cdef Turtle *turtle
    cdef Py_ssize_t i = 0
    cdef Py_ssize_t seed = 1234

    while i < symbols.length:
        turtle = peekTopTurtle(&stack)
        c = symbols.data[i]
        i += 1
        command = symbols.data + i

        if c == "F":
            moveForward_Geo(turtle, <MoveForwardGeoCommand*>command)
            i += sizeof(MoveForwardGeoCommand)
        elif c == "f":
            moveForward_NoGeo(turtle, <MoveForwardNoGeoCommand*>command)
            i += sizeof(MoveForwardNoGeoCommand)
        elif c == "[":
            branchStart(&stack, turtle)
        elif c == "]":
            branchEnd(&stack, &allTurtles)
        elif c == '"':
            scaleStepSize(turtle, <ScaleStepSizeCommand*>command)
            i += sizeof(ScaleStepSizeCommand)
        elif c == "+":
            rotateRight(turtle, <RotateCommand*>command)
            i += sizeof(RotateCommand)
        elif c == "-":
            rotateLeft(turtle, <RotateCommand*>command)
            i += sizeof(RotateCommand)
        elif c == "&":
            pitchUp(turtle, <RotateCommand*>command)
            i += sizeof(RotateCommand)
        elif c == "^":
            pitchDown(turtle, <RotateCommand*>command)
            i += sizeof(RotateCommand)
        elif c == "\\":
            rollClockwise(turtle, <RotateCommand*>command)
            i += sizeof(RotateCommand)
        elif c == "/":
            rollCounterClockwise(turtle, <RotateCommand*>command)
            i += sizeof(RotateCommand)
        elif c == "~":
            rotateRandom(turtle, <RotateCommand*>command, seed)
            i += sizeof(RotateCommand)
        elif c == "A":
            pass
        else:
            raise Exception("unknown opcode")

        seed += 123

    while peekTopTurtle(&stack) != NULL:
        pushTurtle(&allTurtles, popTurtle(&stack))

    cdef Mesh mesh = meshFromTurtles(allTurtles.turtles, allTurtles.amount)
    freeTurtleStack(&allTurtles, freeTurtles = True)
    return mesh

cdef meshFromTurtles(Turtle *turtles, Py_ssize_t amount):
    cdef Py_ssize_t pointAmount = 0
    cdef Py_ssize_t edgeAmount = 0
    cdef Py_ssize_t i
    for i in range(amount):
        pointAmount += turtles[i].pointAmount
        edgeAmount += turtles[i].edgeAmount

    cdef Vector3DList vertices = Vector3DList(length = pointAmount)
    cdef EdgeIndicesList edges = EdgeIndicesList(length = edgeAmount)

    cdef Py_ssize_t vertexOffset = 0
    cdef Py_ssize_t edgeOffset = 0
    cdef Py_ssize_t j
    for i in range(amount):
        memcpy(vertices.data + vertexOffset, turtles[i].points, turtles[i].pointAmount * sizeof(Vector3))

        for j in range(turtles[i].edgeAmount):
            edges.data[edgeOffset + j].v1 = turtles[i].edges[j].v1 + vertexOffset
            edges.data[edgeOffset + j].v2 = turtles[i].edges[j].v2 + vertexOffset

        vertexOffset += turtles[i].pointAmount
        edgeOffset += turtles[i].edgeAmount

    return Mesh(vertices, edges, skipValidation = True)


cdef inline void moveForward_Geo(Turtle *turtle, MoveForwardGeoCommand *command):
    cdef Vector3 translation = Vector3(0, 0, turtle.stepSize * command.distance)
    transformVec3AsDirection_InPlace(&translation, &turtle.orientation)
    move_WithGeometry(turtle, &translation)

cdef inline void moveForward_NoGeo(Turtle *turtle, MoveForwardNoGeoCommand *command):
    cdef Vector3 translation = Vector3(0, 0, turtle.stepSize * command.distance)
    transformVec3AsDirection_InPlace(&translation, &turtle.orientation)
    move_NoGeometry(turtle, &translation)

cdef inline void rotateRight(Turtle *turtle, RotateCommand *command):
    cdef Matrix3 rotation
    setRotationYMatrix(&rotation, command.angle)
    transformOrientation(turtle, &rotation)

cdef inline void rotateLeft(Turtle *turtle, RotateCommand *command):
    cdef Matrix3 rotation
    setRotationYMatrix(&rotation, -command.angle)
    transformOrientation(turtle, &rotation)

cdef inline void pitchUp(Turtle *turtle, RotateCommand *command):
    cdef Matrix3 rotation
    setRotationXMatrix(&rotation, command.angle)
    transformOrientation(turtle, &rotation)

cdef inline void pitchDown(Turtle *turtle, RotateCommand *command):
    cdef Matrix3 rotation
    setRotationXMatrix(&rotation, -command.angle)
    transformOrientation(turtle, &rotation)

cdef inline void rollClockwise(Turtle *turtle, RotateCommand *command):
    cdef Matrix3 rotation
    setRotationZMatrix(&rotation, -command.angle)
    transformOrientation(turtle, &rotation)

cdef inline void rollCounterClockwise(Turtle *turtle, RotateCommand *command):
    cdef Matrix3 rotation
    setRotationZMatrix(&rotation, command.angle)
    transformOrientation(turtle, &rotation)

cdef inline void rotateRandom(Turtle *turtle, RotateCommand *command, Py_ssize_t seed):
    cdef Matrix3 rotation
    cdef Euler3 euler
    euler.order = 0
    euler.x = uniformRandomFloat(seed + 0, -command.angle, command.angle)
    euler.y = uniformRandomFloat(seed + 1, -command.angle, command.angle)
    euler.z = uniformRandomFloat(seed + 2, -command.angle, command.angle)
    setRotationMatrix(&rotation, &euler)
    transformOrientation(turtle, &rotation)

cdef inline void branchStart(TurtleStack *stack, Turtle *current):
    cdef Turtle turtle
    initBranch(&turtle, current)
    pushTurtle(stack, turtle)

cdef inline void branchEnd(TurtleStack *stack, TurtleStack *allTurtles):
    pushTurtle(allTurtles, popTurtle(stack))

cdef inline void scaleStepSize(Turtle *turtle, ScaleStepSizeCommand *command):
    turtle.stepSize *= command.factor


# Turtle Utilities
##########################################

cdef void initTurtle(Turtle *turtle):
    setIdentityMatrix(&turtle.orientation)
    turtle.position = Vector3(0, 0, 0)
    turtle.stepSize = 1
    turtle.currentPositionStored = False
    initTurtleArrays(turtle)

cdef void freeTurtle(Turtle *turtle):
    PyMem_Free(turtle.points)
    PyMem_Free(turtle.edges)

cdef void initBranch(Turtle *turtle, Turtle *source):
    turtle.orientation = source.orientation
    turtle.position = source.position
    turtle.stepSize = source.stepSize
    turtle.currentPositionStored = False
    initTurtleArrays(turtle)

cdef void initTurtleArrays(Turtle *turtle):
    cdef Py_ssize_t DEFAULT_SIZE = 4

    turtle.pointAmount = 0
    turtle.pointCapacity = DEFAULT_SIZE
    turtle.points = <Vector3*>PyMem_Malloc(DEFAULT_SIZE * sizeof(Vector3))

    turtle.edgeAmount = 0
    turtle.edgeCapacity = DEFAULT_SIZE
    turtle.edges = <EdgeIndices*>PyMem_Malloc(DEFAULT_SIZE * sizeof(EdgeIndices))

cdef inline void growPointsArray(Turtle *turtle):
    cdef Py_ssize_t newCapacity = turtle.pointCapacity * 2
    turtle.points = <Vector3*>PyMem_Realloc(turtle.points, newCapacity * sizeof(Vector3))
    turtle.pointCapacity = newCapacity

cdef inline void growEdgesArray(Turtle *turtle):
    cdef Py_ssize_t newCapacity = turtle.edgeCapacity * 2
    turtle.edges = <EdgeIndices*>PyMem_Realloc(turtle.edges, newCapacity * sizeof(EdgeIndices))
    turtle.edgeCapacity = newCapacity

cdef inline void move_NoGeometry(Turtle *turtle, Vector3 *translation):
    addVec3_Inplace(&turtle.position, translation)
    turtle.currentPositionStored = False

cdef inline void move_WithGeometry(Turtle *turtle, Vector3 *translation):
    if not turtle.currentPositionStored:
        storeCurrentPosition(turtle)
    addVec3_Inplace(&turtle.position, translation)
    storeCurrentPosition(turtle)
    connectLastTwoPoints(turtle)

cdef inline void storeCurrentPosition(Turtle *turtle):
    if turtle.pointAmount == turtle.pointCapacity:
        growPointsArray(turtle)
    turtle.points[turtle.pointAmount] = turtle.position
    turtle.pointAmount += 1
    turtle.currentPositionStored = True

cdef inline void connectLastTwoPoints(Turtle *turtle):
    if turtle.edgeAmount == turtle.edgeCapacity:
        growEdgesArray(turtle)
    turtle.edges[turtle.edgeAmount].v1 = turtle.pointAmount - 2
    turtle.edges[turtle.edgeAmount].v2 = turtle.pointAmount - 1
    turtle.edgeAmount += 1

cdef inline void transformOrientation(Turtle *turtle, Matrix3 *rotation):
    cdef Matrix3 newOrientation
    multMatrix3(&newOrientation, &turtle.orientation, rotation)
    turtle.orientation = newOrientation

cdef Vector3DList getTurtlePoints(Turtle *turtle):
    cdef Vector3DList vectors = Vector3DList(length = turtle.pointAmount)
    memcpy(vectors.data, turtle.points, turtle.pointAmount * sizeof(Vector3))
    return vectors

cdef EdgeIndicesList getTurtleEdges(Turtle *turtle):
    cdef EdgeIndicesList edges = EdgeIndicesList(length = turtle.edgeAmount)
    memcpy(edges.data, turtle.edges, turtle.edgeAmount * sizeof(EdgeIndices))
    return edges


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
    cdef Turtle *turtle = peekTopTurtle(stack)
    stack.amount -= 1
    return turtle[0]

cdef inline void growTurtleStack(TurtleStack *stack):
    cdef Py_ssize_t newCapacity = stack.capacity * 2
    stack.turtles = <Turtle*>PyMem_Realloc(stack.turtles, newCapacity * sizeof(Turtle))
    stack.capacity = newCapacity