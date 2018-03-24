import bpy
import traceback
from collections import Counter
from ... base_types import AnimationNode
from bpy.props import IntProperty, BoolProperty
from ... algorithms.random cimport uniformRandomFloat, randomFloat_Positive

from libc.math cimport M_PI as PI
from libc.string cimport memcpy, memset
from cpython cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free

from ... data_structures cimport (
    Vector3DList, EdgeIndices, EdgeIndicesList, Mesh, FloatList, DoubleList
)
from ... math cimport *

cdef float degToRadFactor = PI / 180

class LSystemNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_LSystemNode"
    bl_label = "LSystem"
    errorHandlingType = "EXCEPTION"
    bl_width_default = 180

    useSymbolLimit = BoolProperty(name = "Use Symbol Limit", default = True)

    symbolLimit = IntProperty(name = "Symbol Limit", default = 100000,
        description = "To prevent freezing Blender when trying to calculate too many generations.",
        min = 0)

    def create(self):
        self.newInput("Text", "Axiom", "axiom")
        self.newInput("Text List", "Rules", "rules")
        self.newInput("Float", "Generations", "generations", minValue = 0)
        self.newInput("Integer", "Seed", "seed")
        self.newInput("Float", "Step Size", "stepSize", value = 1)
        self.newInput("Float", "Angle", "angle", value = 90)
        self.newInput("Float", "Random Angle", "randomAngle", value = 180)
        self.newInput("Float", "Scale Step Size", "scaleStepSize", value = 0.9)
        self.newInput("Float", "Gravity", "gravity", value = 0)
        self.newInput("Boolean", "Partial Rotations", "partialRotations", value = False)
        self.newInput("Float", "Width Scale", "widthScale", value = 0.9)
        self.newOutput("Mesh", "Mesh", "mesh")
        self.newOutput("Float List", "Edge Widths", "edgeWidths")

    def drawAdvanced(self, layout):
        row = layout.row(align = True)
        subrow = row.row(align = True)
        subrow.active = self.useSymbolLimit
        subrow.prop(self, "symbolLimit")
        icon = "LAYER_ACTIVE" if self.useSymbolLimit else "LAYER_USED"
        row.prop(self, "useSymbolLimit", text = "", icon = icon)

    def execute(self, axiom, rules, generations, seed, stepSize, angle, randomAngle, scaleStepSize, gravity, partialRotations, widthScale):
        parseDefaults = {
            "Step Size" : stepSize,
            "Angle" : angle,
            "Random Angle" : randomAngle,
            "Scale Step Size" : scaleStepSize,
            "Gravity" : gravity,
            "Width Scale" : widthScale
        }

        cdef SymbolString _axiom
        try:
            _axiom = parseSymbolString(axiom, parseDefaults)
        except:
            traceback.print_exc()
            self.raiseErrorMessage("error when parsing axiom")

        cdef RuleSet ruleSet
        rules = [rule for rule in rules if len(rule.strip()) > 0]
        try:
            initRuleSet(&ruleSet, rules, parseDefaults)
        except:
            traceback.print_exc()
            self.raiseErrorMessage("error when parsing rules")

        cdef SymbolString symbols
        try:
            limit = self.symbolLimit if self.useSymbolLimit else None
            symbols = applyGrammarRules(_axiom, ruleSet,
                generations, (<int>seed + 34521) * 4523, partialRotations, limit)
        except SymbolLimitReachedException:
            self.raiseErrorMessage("symbol limit reached, you can increase it in the advanced settings")
        except:
            traceback.print_exc()
            self.raiseErrorMessage("error while applying grammar rules")

        freeRuleSet(&ruleSet)
        freeSymbolString(&_axiom)

        geometryDefaults = {
            "Angle" : angle * degToRadFactor
        }

        vertices, edges, widths = geometryFromSymbolString(symbols, seed, geometryDefaults)
        freeSymbolString(&symbols)

        return Mesh(vertices, edges, skipValidation = True), DoubleList.fromValues(widths)

class SymbolLimitReachedException(Exception):
    pass


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
cdef struct ScaleCommand:
    float factor
cdef struct TropismCommand:
    float gravity

ctypedef fused Command:
    NoArgCommand
    MoveForwardGeoCommand
    MoveForwardNoGeoCommand
    RotateCommand
    ScaleCommand
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
        elif c in '"':
            size = parse_Scale(&symbols, source, i, c, defaults["Scale Step Size"])
        elif c == "!":
            size = parse_Scale(&symbols, source, i, c, defaults["Width Scale"])
        elif c == "T":
            size = parse_Tropism(&symbols, source, i, defaults["Gravity"])
        elif c in ("A", "B", "X", "Y", "Z"):
            size = parse_SingleLetter(&symbols, c)
        elif c == " ":
            size = 1
        else:
            raise Exception("unkown symbol")

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

cdef parse_Scale(SymbolString *symbols, str source, Py_ssize_t index, letter, float default):
    (factor,), argLength = parseArguments(source, index + 1, ["float"])
    if factor is None: factor = default
    appendSymbol(symbols, ord(letter), ScaleCommand(<float>factor))
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

cdef void resetSymbolString(SymbolString *symbols):
    symbols.length = 0

cdef void copySymbolString(SymbolString *target, SymbolString *source):
    target.data = <unsigned char*>PyMem_Malloc(source.length)
    memcpy(target.data, source.data, source.length)
    target.length = source.length
    target.capacity = source.length

cdef inline void growSymbolString(SymbolString *symbols, Py_ssize_t minIncrease):
    cdef Py_ssize_t newCapacity = symbols.capacity * 2 + minIncrease
    symbols.data = <unsigned char*>PyMem_Realloc(symbols.data, newCapacity)
    symbols.capacity = newCapacity

cdef inline void appendSymbol(SymbolString *symbols, unsigned char prefix, Command command):
    cdef Py_ssize_t size = 1 + sizeof(Command)
    if symbols.length + size > symbols.capacity:
        growSymbolString(symbols, size)

    symbols.data[symbols.length] = prefix
    symbols.length += 1

    if Command is not NoArgCommand:
        memcpy(symbols.data + symbols.length, &command, sizeof(Command))
        symbols.length += sizeof(Command)

cdef inline void appendNoArgSymbol(SymbolString *symbols, unsigned char prefix):
    appendSymbol(symbols, prefix, NoArgCommand(0))

cdef inline void appendSymbolBuffer(SymbolString *symbols, void *buffer, Py_ssize_t length):
    if symbols.length + length > symbols.capacity:
        growSymbolString(symbols, length)
    memcpy(symbols.data + symbols.length, buffer, length)
    symbols.length += length

cdef inline void appendSymbolString(SymbolString *symbols, SymbolString *other):
    appendSymbolBuffer(symbols, other.data, other.length)



# Apply Grammar Rules
######################################

cdef struct Rule:
    unsigned char symbol
    unsigned char hasProbability
    float probability
    SymbolString replacement

cdef struct RuleSet:
    Rule **rules
    unsigned char *lengths

cdef SymbolString applyGrammarRules(SymbolString axiom, RuleSet rules, float generations, int seed = 0,
                                    bint partialRotations = False, symbolLimit = None) except *:
    cdef SymbolString currentGen
    cdef SymbolString nextGen

    copySymbolString(&currentGen, &axiom)

    if generations <= 0:
        return currentGen
    else:
        initSymbolString(&nextGen)

    for i in range(int(generations)):
        resetSymbolString(&nextGen)
        applyGrammarRules_OneGeneration(currentGen, rules, &nextGen, seed)
        currentGen, nextGen = nextGen, currentGen

        if symbolLimit is not None and currentGen.length >= symbolLimit:
            raise SymbolLimitReachedException()

        seed += 654321

    if generations % 1 != 0:
        resetSymbolString(&nextGen)
        applyGrammarRules_PartialGeneration(currentGen, rules, &nextGen, seed, generations % 1, partialRotations)
        currentGen, nextGen = nextGen, currentGen

    freeSymbolString(&nextGen)
    return currentGen

cdef applyGrammarRules_OneGeneration(SymbolString source, RuleSet ruleSet, SymbolString *target, int seed):
    cdef SymbolString *replacement

    cdef Py_ssize_t i = 0
    cdef unsigned char c
    cdef void *command
    while i < source.length:
        c = source.data[i]
        i += 1
        command = source.data + i
        if c in ("[", "]"):
            appendNoArgSymbol(target, c)
            i += 0
        elif c in ("+", "-", "&", "^", "\\", "/", "~"):
            appendSymbol(target, c, (<RotateCommand*>command)[0])
            i += sizeof(RotateCommand)
        elif c in ('"', "!"):
            appendSymbol(target, c, (<ScaleCommand*>command)[0])
            i += sizeof(ScaleCommand)
        elif c == "T":
            appendSymbol(target, c, (<TropismCommand*>command)[0])
            i += sizeof(TropismCommand)
        else:
            replacement = getReplacement(&ruleSet, c, seed)
            if replacement != NULL:
                appendSymbolString(target, replacement)
                if c == "F":
                    i += sizeof(MoveForwardGeoCommand)
                elif c == "f":
                    i += sizeof(MoveForwardNoGeoCommand)
            else:
                if c == "F":
                    appendSymbol(target, c, (<MoveForwardGeoCommand*>command)[0])
                    i += sizeof(MoveForwardGeoCommand)
                elif c == "f":
                    appendSymbol(target, c, (<MoveForwardNoGeoCommand*>command)[0])
                    i += sizeof(MoveForwardNoGeoCommand)
                elif c in ("A", "B", "X", "Y", "Z"):
                    appendNoArgSymbol(target, c)

        seed += 4321

cdef applyGrammarRules_PartialGeneration(SymbolString source, RuleSet ruleSet, SymbolString *target, int seed, float genRemainder, bint partialRotations):
    cdef SymbolString *replacement
    cdef MoveForwardGeoCommand moveForwardGeoCommand
    cdef MoveForwardNoGeoCommand moveForwardNoGeoCommand

    cdef Py_ssize_t i = 0
    cdef unsigned char c
    cdef void *command
    while i < source.length:
        c = source.data[i]
        i += 1
        command = source.data + i
        if c in ("[", "]"):
            appendNoArgSymbol(target, c)
            i += 0
        elif c in ("+", "-", "&", "^", "\\", "/", "~"):
            appendSymbol(target, c, (<RotateCommand*>command)[0])
            i += sizeof(RotateCommand)
        elif c in ('"', "!"):
            appendSymbol(target, c, (<ScaleCommand*>command)[0])
            i += sizeof(ScaleCommand)
        elif c == "T":
            appendSymbol(target, c, (<TropismCommand*>command)[0])
            i += sizeof(TropismCommand)
        else:
            replacement = getReplacement(&ruleSet, c, seed)
            if replacement != NULL:
                if c == "F":
                    moveForwardGeoCommand = (<MoveForwardGeoCommand*>command)[0]
                    moveForwardGeoCommand.distance *= 1 - genRemainder
                    appendSymbol(target, c, moveForwardGeoCommand)
                    i += sizeof(MoveForwardGeoCommand)
                elif c == "f":
                    moveForwardNoGeoCommand = (<MoveForwardNoGeoCommand*>command)[0]
                    moveForwardNoGeoCommand.distance *= 1 - genRemainder
                    appendSymbol(target, c, moveForwardNoGeoCommand)
                    i += sizeof(MoveForwardNoGeoCommand)
                appendScaledSymbolString(target, replacement, genRemainder, partialRotations)
            else:
                if c == "F":
                    appendSymbol(target, c, (<MoveForwardGeoCommand*>command)[0])
                    i += sizeof(MoveForwardGeoCommand)
                elif c == "f":
                    appendSymbol(target, c, (<MoveForwardNoGeoCommand*>command)[0])
                    i += sizeof(MoveForwardNoGeoCommand)
                elif c in ("A", "B", "X", "Y", "Z"):
                    appendNoArgSymbol(target, c)

        seed += 4321

cdef inline void appendScaledSymbolString(SymbolString *target, SymbolString *source, float factor, bint partialRotations):
    cdef TropismCommand tropismCommand
    cdef RotateCommand rotateCommand
    cdef ScaleCommand scaleCommand
    cdef MoveForwardGeoCommand moveForwardGeoCommand
    cdef MoveForwardNoGeoCommand moveForwardNoGeoCommand

    cdef Py_ssize_t i = 0
    cdef unsigned char c
    cdef void *command
    while i < source.length:
        c = source.data[i]
        i += 1
        command = source.data + i
        if c in ("[", "]"):
            appendNoArgSymbol(target, c)
            i += 0
        elif c in ("+", "-", "&", "^", "\\", "/", "~"):
            rotateCommand = (<RotateCommand*>command)[0]
            if partialRotations: rotateCommand.angle *= factor
            appendSymbol(target, c, rotateCommand)
            i += sizeof(RotateCommand)
        elif c in ('"', "!"):
            scaleCommand = (<ScaleCommand*>command)[0]
            scaleCommand.factor = (1 - factor) * 1 + factor * scaleCommand.factor
            appendSymbol(target, c, scaleCommand)
            i += sizeof(ScaleCommand)
        elif c == "T":
            tropismCommand = (<TropismCommand*>command)[0]
            tropismCommand.gravity *= factor
            appendSymbol(target, c, tropismCommand)
            i += sizeof(TropismCommand)
        elif c == "F":
            moveForwardGeoCommand = (<MoveForwardGeoCommand*>command)[0]
            moveForwardGeoCommand.distance *= factor
            appendSymbol(target, c, moveForwardGeoCommand)
            i += sizeof(MoveForwardGeoCommand)
        elif c == "f":
            moveForwardNoGeoCommand = (<MoveForwardNoGeoCommand*>command)[0]
            moveForwardNoGeoCommand.distance *= factor
            appendSymbol(target, c, moveForwardNoGeoCommand)
            i += sizeof(MoveForwardNoGeoCommand)
        elif c in ("A", "B", "X", "Y", "Z"):
            appendNoArgSymbol(target, c)

cdef inline SymbolString *getReplacement(RuleSet *ruleSet, unsigned char symbol, int seed):
    cdef Py_ssize_t i
    cdef Rule *rule
    cdef float randomNumber
    for i in range(ruleSet.lengths[symbol]):
        rule = ruleSet.rules[symbol] + i
        if rule.hasProbability:
            randomNumber = randomFloat_Positive(seed+i)
            if randomNumber < rule.probability:
                return &rule.replacement
        else:
            return &rule.replacement
    else:
        return NULL

cdef initRuleSet(RuleSet *ruleSet, rules, defaults):
    ruleSet.rules = <Rule**>PyMem_Malloc(256 * sizeof(Rule*))
    memset(ruleSet.rules, 0, 256 * sizeof(Rule*))

    ruleSet.lengths = <unsigned char*>PyMem_Malloc(256 * sizeof(unsigned char))
    memset(ruleSet.lengths, 0, 256 * sizeof(unsigned char))

    counter = Counter([getRuleSymbol(r) for r in rules])
    for symbol, amount in counter.items():
        ruleSet.lengths[ord(symbol)] = amount
        ruleSet.rules[ord(symbol)] = <Rule*>PyMem_Malloc(amount * sizeof(Rule))

    cdef unsigned char insertedAmount[256]
    memset(insertedAmount, 0, 256)

    cdef Rule *rule
    for sourceRule in rules:
        symbol = getRuleSymbol(sourceRule)
        rule = ruleSet.rules[ord(symbol)] + insertedAmount[ord(symbol)]
        parse_Rule(sourceRule, rule, defaults)
        insertedAmount[ord(symbol)] += 1

def getRuleSymbol(str rule):
    return rule.strip()[0]

cdef parse_Rule(str source, Rule *rule, defaults):
    parts = source.split("=")
    if len(parts) != 2:
        raise Exception("Rule must have an '='")
    parse_RulePremise(rule, parts[0])
    parse_RuleProduction(rule, parts[1], defaults)

cdef parse_RulePremise(Rule *rule, str source):
    source = source.strip()
    if len(source) != 1:
        raise Exception("Left side of rule must be a single symbol")
    rule.symbol = ord(source)

cdef parse_RuleProduction(Rule *rule, str source, defaults):
    if ":" in source:
        left, right = source.split(":")
        rule.replacement = parseSymbolString(left.strip(), defaults)
        rule.hasProbability = True
        rule.probability = float(right.strip())
    else:
        rule.replacement = parseSymbolString(source.strip(), defaults)
        rule.hasProbability = False

cdef freeRuleSet(RuleSet *ruleSet):
    cdef Py_ssize_t symbol, j
    for symbol in range(256):
        for j in range(ruleSet.lengths[symbol]):
            freeRule(&ruleSet.rules[symbol][j])
        if ruleSet.lengths[symbol] > 0:
            PyMem_Free(ruleSet.rules[symbol])
    PyMem_Free(ruleSet.rules)
    PyMem_Free(ruleSet.lengths)

cdef freeRule(Rule *rule):
    freeSymbolString(&rule.replacement)



# Create Geometry from SymbolString
################################################

cdef struct Turtle:
    Matrix3 orientation
    Vector3 position
    float width
    float stepSize
    bint currentPositionStored

    Py_ssize_t pointAmount
    Py_ssize_t pointCapacity
    Vector3 *points

    Py_ssize_t edgeAmount
    Py_ssize_t edgeCapacity
    TurtleEdge *edges

    Py_ssize_t widthAmount
    Py_ssize_t widthCapacity
    float *widths

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

    cdef char c
    cdef void *command
    cdef Turtle *turtle
    cdef Py_ssize_t i = 0

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
            branchStart(&stack, turtle, &availableStack)
        elif c == "]":
            branchEnd(&stack, vertices, edges, widths, &availableStack)
        elif c == '"':
            scaleStepSize(turtle, <ScaleCommand*>command)
            i += sizeof(ScaleCommand)
        elif c == "!":
            scaleWidth(turtle, <ScaleCommand*>command)
            i += sizeof(ScaleCommand)
        elif c == "+":
            rotateRight(turtle, <RotateCommand*>command, defaultAngle, &defaultYRotation)
            i += sizeof(RotateCommand)
        elif c == "-":
            rotateLeft(turtle, <RotateCommand*>command, defaultAngle, &defaultYRotationNeg)
            i += sizeof(RotateCommand)
        elif c == "&":
            pitchUp(turtle, <RotateCommand*>command, defaultAngle, &defaultXRotation)
            i += sizeof(RotateCommand)
        elif c == "^":
            pitchDown(turtle, <RotateCommand*>command, defaultAngle, &defaultXRotationNeg)
            i += sizeof(RotateCommand)
        elif c == "\\":
            rollClockwise(turtle, <RotateCommand*>command, defaultAngle, &defaultZRotationNeg)
            i += sizeof(RotateCommand)
        elif c == "/":
            rollCounterClockwise(turtle, <RotateCommand*>command, defaultAngle, &defaultZRotation)
            i += sizeof(RotateCommand)
        elif c == "~":
            rotateRandom(turtle, <RotateCommand*>command, seed)
            i += sizeof(RotateCommand)
        elif c == "T":
            applyTropism(turtle, <TropismCommand*>command)
            i += sizeof(TropismCommand)
        elif c in ("A", "B", "X", "Y", "Z"):
            pass
        else:
            raise Exception("unknown opcode")

        seed += 123

    cdef Turtle _turtle
    while stackHasElements(&stack):
        _turtle = popTurtle(&stack)
        appendTurtleData(&_turtle, vertices, edges, widths)
        freeTurtle(&_turtle)

    while stackHasElements(&availableStack):
        _turtle = popTurtle(&availableStack)
        freeTurtle(&_turtle)

    return vertices, edges, widths

cdef inline appendTurtleData(Turtle *turtle, Vector3DList vertices, EdgeIndicesList edges, FloatList widths):
    cdef Py_ssize_t i
    cdef Py_ssize_t offset = vertices.length
    for i in range(turtle.pointAmount):
        vertices.append_LowLevel(turtle.points[i])
    for i in range(turtle.edgeAmount):
        edges.append_LowLevel(EdgeIndices(
            turtle.edges[i].indices.v1 + offset,
            turtle.edges[i].indices.v2 + offset))
        widths.append_LowLevel(turtle.edges[i].width)

cdef inline void moveForward_Geo(Turtle *turtle, MoveForwardGeoCommand *command):
    cdef Vector3 translation = Vector3(0, 0, turtle.stepSize * command.distance)
    transformVec3AsDirection_InPlace(&translation, &turtle.orientation)
    move_WithGeometry(turtle, &translation)

cdef inline void moveForward_NoGeo(Turtle *turtle, MoveForwardNoGeoCommand *command):
    cdef Vector3 translation = Vector3(0, 0, turtle.stepSize * command.distance)
    transformVec3AsDirection_InPlace(&translation, &turtle.orientation)
    move_NoGeometry(turtle, &translation)

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
    euler.x = uniformRandomFloat(seed + 0, -command.angle, command.angle)
    euler.y = uniformRandomFloat(seed + 1, -command.angle, command.angle)
    euler.z = uniformRandomFloat(seed + 2, -command.angle, command.angle)
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

cdef inline void branchEnd(TurtleStack *stack, Vector3DList vertices, EdgeIndicesList edges, FloatList widths, TurtleStack *availableStack):
    if stack.amount <= 1:
        return
    cdef Turtle turtle = popTurtle(stack)
    appendTurtleData(&turtle, vertices, edges, widths)
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
    cdef Vector3 axis
    crossVec3(&axis, &forward, &newForward)
    normalizeVec3_InPlace(&axis)

    cdef Matrix3 rotation
    normalizedAxisCosAngleToMatrix(&rotation, &axis, cosAngle)
    transformOrientation_Global(turtle, &rotation)



# Turtle Utilities
##########################################

cdef struct TurtleEdge:
    EdgeIndices indices
    float width

cdef void initTurtle(Turtle *turtle):
    setIdentityMatrix(&turtle.orientation)
    turtle.position = Vector3(0, 0, 0)
    turtle.stepSize = 1
    turtle.width = 1
    turtle.currentPositionStored = False

    cdef Py_ssize_t DEFAULT_SIZE = 4

    turtle.pointAmount = 0
    turtle.pointCapacity = DEFAULT_SIZE
    turtle.points = <Vector3*>PyMem_Malloc(DEFAULT_SIZE * sizeof(Vector3))

    turtle.edgeAmount = 0
    turtle.edgeCapacity = DEFAULT_SIZE
    turtle.edges = <TurtleEdge*>PyMem_Malloc(DEFAULT_SIZE * sizeof(TurtleEdge))

cdef void freeTurtle(Turtle *turtle):
    PyMem_Free(turtle.points)
    PyMem_Free(turtle.edges)

cdef void initBranch(Turtle *turtle, Turtle *source):
    turtle.orientation = source.orientation
    turtle.position = source.position
    turtle.stepSize = source.stepSize
    turtle.width = source.width
    turtle.currentPositionStored = False
    turtle.pointAmount = 0
    turtle.edgeAmount = 0

cdef inline void growPointsArray(Turtle *turtle):
    cdef Py_ssize_t newCapacity = turtle.pointCapacity * 2
    turtle.points = <Vector3*>PyMem_Realloc(turtle.points, newCapacity * sizeof(Vector3))
    turtle.pointCapacity = newCapacity

cdef inline void growEdgesArray(Turtle *turtle):
    cdef Py_ssize_t newCapacity = turtle.edgeCapacity * 2
    turtle.edges = <TurtleEdge*>PyMem_Realloc(turtle.edges, newCapacity * sizeof(TurtleEdge))
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
    turtle.edges[turtle.edgeAmount].indices.v1 = turtle.pointAmount - 2
    turtle.edges[turtle.edgeAmount].indices.v2 = turtle.pointAmount - 1
    turtle.edges[turtle.edgeAmount].width = turtle.width
    turtle.edgeAmount += 1

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