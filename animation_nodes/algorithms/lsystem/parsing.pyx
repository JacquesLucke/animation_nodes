from . rule cimport *
from . symbol_string cimport *

from cpython cimport PyMem_Malloc
from libc.string cimport memset
from libc.math cimport M_PI as PI

from collections import Counter


# Parse Symbol String
###################################################

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
            size = parse_Scale(&symbols, source, i, c, defaults["Scale Width"])
        elif c == "T":
            size = parse_Tropism(&symbols, source, i, defaults["Gravity"])
        elif c in ("A", "B", "X", "Y", "Z", "J", "K", "M"):
            size = parse_SingleLetter(&symbols, c)
        elif c == " ":
            size = 1
        else:
            raise Exception("unkown symbol")

        i += size

    return symbols

cdef parse_MoveForward_Geo(SymbolString *symbols, str source, Py_ssize_t index, float default):
    id, (distance,), argLength = parseArgumentsAndID(source, index + 1, ["float"])
    if id is None: id = 0
    if distance is None: distance = default
    appendSymbol(symbols, ord("F"), MoveForwardGeoCommand(id, <float>distance))
    return argLength + 1

cdef parse_MoveForward_NoGeo(SymbolString *symbols, str source, Py_ssize_t index, float default):
    (distance,), argLength = parseArguments(source, index + 1, ["float"])
    if distance is None: distance = default
    appendSymbol(symbols, ord("f"), MoveForwardNoGeoCommand(<float>distance))
    return argLength + 1

cdef parse_Rotate(SymbolString *symbols, str source, Py_ssize_t index, letter, float default):
    (angle,), argLength = parseArguments(source, index + 1, ["float"])
    if angle is None: angle = default
    angle *= PI / 180
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


cdef parseArgumentsAndID(str source, Py_ssize_t index, argTypes):
    if letterAtIndexIsDigit(source, index):
        digitLetters = getLettersUntilDigitsEnd(source, index)
        id = int(digitLetters)
        if not (0 <= id <= 255):
            raise Exception("id must be between 0 and 255")
        idLength = len(digitLetters)
    else:
        id = None
        idLength = 0
    values, argLength = parseArguments(source, index + idLength, argTypes)
    return id, values, argLength + idLength

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

cdef bint letterAtIndexIsDigit(str source, Py_ssize_t index):
    if index < len(source):
        return source[index].isdigit()
    else:
        return False

cdef str getLettersUntilDigitsEnd(str source, Py_ssize_t index):
    letters = ""
    while letterAtIndexIsDigit(source, index):
        letters += source[index]
        index += 1
    return letters



# Parse Rule Set
######################################################

cdef RuleSet parseRuleSet(ruleStrings, defaults) except *:
    cdef RuleSet ruleSet
    initRuleSet(&ruleSet)

    counter = Counter([getRuleSymbolIndex(s) for s in ruleStrings])
    for symbolIndex, amount in counter.items():
        ruleSet.lengths[symbolIndex] = amount
        ruleSet.rules[symbolIndex] = <Rule*>PyMem_Malloc(amount * sizeof(Rule))

    cdef unsigned char insertedAmount[256]
    memset(insertedAmount, 0, 256)

    cdef Rule *rule
    for ruleString in ruleStrings:
        symbolIndex = getRuleSymbolIndex(ruleString)
        rule = ruleSet.rules[symbolIndex] + insertedAmount[symbolIndex]
        initRule(rule)
        parse_Rule(ruleString, rule, defaults)
        insertedAmount[symbolIndex] += 1

    return ruleSet

cdef getRuleSymbolIndex(str rule):
    return ord(getRuleSymbol(rule))

cdef getRuleSymbol(str rule):
    return rule.strip()[0]

cdef parse_Rule(str source, Rule *rule, defaults):
    parts = source.split("=")
    if len(parts) != 2:
        raise Exception("Rule must have an '='")
    parse_RulePremise(rule, parts[0])
    parse_RuleProduction(rule, parts[1], defaults)

cdef parse_RulePremise(Rule *rule, str source):
    source = source.strip()
    if len(source) == 0:
        raise Exception("A rule requires a premise")
    else:
        symbol = source[0]
        rule.symbol = ord(symbol)

        if symbol == "F" and len(source) > 1:
            idStr = source[1:]
            try: id = int(idStr)
            except: raise Exception("Cannot parse symbol ID")
            if not (0 <= id <= 255):
                raise Exception("Symbol ID has to be between 0 and 255")
            rule.flags |= RULE_HAS_CONDITION
            rule.condition.function = checkFID
            rule.condition.data.id = id

cdef bint checkFID(RuleConditionData data, void *command):
    return data.id == (<MoveForwardGeoCommand*>command).id

cdef parse_RuleProduction(Rule *rule, str source, defaults):
    if ":" in source:
        left, right = source.split(":")
        rule.replacement = parseSymbolString(left.strip(), defaults)
        rule.flags |= RULE_HAS_PROBABILITY
        try:
            rule.probability = float(right.strip())
            assert 0 <= rule.probability <= 1
        except: raise Exception("probability must be between 0 and 1")
    else:
        rule.replacement = parseSymbolString(source.strip(), defaults)