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
        applyGrammarRules_Single(currentGen, rules, &nextGen, seed)
        currentGen, nextGen = nextGen, currentGen

        if symbolLimit is not None and currentGen.length >= symbolLimit:
            raise Exception("Symbol limit reached. You have to increase it to make more complex objects.")

        seed += 654321

    if generations % 1 != 0:
        resetSymbolString(&nextGen)
        applyGrammarRules_Single(currentGen, rules, &nextGen, seed, generations % 1, partialRotations)
        currentGen, nextGen = nextGen, currentGen

    freeSymbolString(&nextGen)
    return currentGen

cdef applyGrammarRules_Single(
        SymbolString source, RuleSet ruleSet, SymbolString *target, int seed,
        float generationPart = 1, bint partialRotations = True):
    assert 0 <= generationPart <= 1

    cdef SymbolString *replacement
    cdef MoveForwardGeoCommand moveForwardGeoCommand
    cdef MoveForwardNoGeoCommand moveForwardNoGeoCommand

    cdef Py_ssize_t i = 0
    cdef unsigned char c
    cdef void *command
    cdef bint isFullGeneration = generationPart == 1
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
            if replacement == NULL:
                if c == "F":
                    appendSymbol(target, c, (<MoveForwardGeoCommand*>command)[0])
                    i += sizeof(MoveForwardGeoCommand)
                elif c == "f":
                    appendSymbol(target, c, (<MoveForwardNoGeoCommand*>command)[0])
                    i += sizeof(MoveForwardNoGeoCommand)
                elif c in ("A", "B", "X", "Y", "Z"):
                    appendNoArgSymbol(target, c)
            else:
                if isFullGeneration:
                    appendSymbolString(target, replacement)
                    if c == "F":
                        i += sizeof(MoveForwardGeoCommand)
                    elif c == "f":
                        i += sizeof(MoveForwardNoGeoCommand)
                else:
                    if c == "F":
                        moveForwardGeoCommand = (<MoveForwardGeoCommand*>command)[0]
                        moveForwardGeoCommand.distance *= 1 - generationPart
                        appendSymbol(target, c, moveForwardGeoCommand)
                        i += sizeof(MoveForwardGeoCommand)
                    elif c == "f":
                        moveForwardNoGeoCommand = (<MoveForwardNoGeoCommand*>command)[0]
                        moveForwardNoGeoCommand.distance *= 1 - generationPart
                        appendSymbol(target, c, moveForwardNoGeoCommand)
                        i += sizeof(MoveForwardNoGeoCommand)
                    appendScaledSymbolString(target, replacement, generationPart, partialRotations)


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