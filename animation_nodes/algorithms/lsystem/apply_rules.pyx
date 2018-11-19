from libc.math cimport floor
from cpython cimport PyMem_Malloc, PyMem_Free
from ... data_structures cimport IntegerList
from ... algorithms.random cimport randomInteger


usedAlgorithm = ["Recursive", "Layered"][0]
cdef char *commandLengths = getCommandLengthsArray()

cdef SymbolString applyGrammarRules(SymbolString axiom, RuleSet ruleSet, float generations,
        int seed = 0, bint onlyPartialMoves = True, symbolLimit = None) except *:

    cdef Py_ssize_t usedSymbolLimit
    if symbolLimit is None:
        usedSymbolLimit = 2 ** (sizeof(Py_ssize_t) * 8 - 1) - 1
    else:
        usedSymbolLimit = symbolLimit

    if usedAlgorithm == "Layered":
        return applyGrammarRules_Layered(axiom, ruleSet, generations, seed, usedSymbolLimit, onlyPartialMoves)
    elif usedAlgorithm == "Recursive":
        return applyGrammarRules_Recursive(axiom, ruleSet, generations, seed, usedSymbolLimit, onlyPartialMoves)
    else:
        raise Exception("unknown algorithm")



# Algorithm 1: Layered
#
# Calculate generations one after the other.
###############################################################

cdef SymbolString applyGrammarRules_Layered(SymbolString source, RuleSet ruleSet,
        float generations, int seed, Py_ssize_t symbolLimit, bint onlyPartialMoves = True) except *:

    cdef SymbolString currentGen
    cdef SymbolString nextGen

    copySymbolString(&currentGen, &source)

    if generations <= 0:
        return currentGen
    else:
        initSymbolString(&nextGen)

    for i in range(int(generations)):
        resetSymbolString(&nextGen)
        applyGrammarRules_FullGeneration(currentGen, ruleSet, &nextGen, seed)
        currentGen, nextGen = nextGen, currentGen

        if symbolLimit is not None and currentGen.length >= symbolLimit:
            raise Exception("Symbol limit reached. You have to increase it to make more complex objects.")

        seed += 654321

    if generations % 1 != 0:
        resetSymbolString(&nextGen)
        applyGrammarRules_PartialGeneration(currentGen, ruleSet, &nextGen, seed, generations % 1, onlyPartialMoves)
        currentGen, nextGen = nextGen, currentGen

    freeSymbolString(&nextGen)
    return currentGen

cdef applyGrammarRules_FullGeneration(SymbolString source, RuleSet ruleSet, SymbolString *target, int seed):
    cdef Py_ssize_t i = 0
    cdef unsigned char c
    cdef void *command
    cdef RuleResultType ruleResult
    cdef SymbolString *replacement

    while i < source.length:
        c = source.data[i]
        i += 1
        command = source.data + i
        i += commandLengths[c]

        ruleResult = getReplacement(&replacement, &ruleSet, c, command, seed)
        if ruleResult in (RuleResultType.CanChange, RuleResultType.WillNotChange):
            appendSingleSymbol(target, c, command, commandLengths[c])
        else:
            appendSymbolString(target, replacement)

        seed += 4321

cdef applyGrammarRules_PartialGeneration(SymbolString source, RuleSet ruleSet, SymbolString *target, int seed,
        float part, bint onlyPartialMoves = True):
    cdef Py_ssize_t i = 0
    cdef unsigned char c
    cdef void *command
    cdef RuleResultType ruleResult
    cdef SymbolString *replacement

    while i < source.length:
        c = source.data[i]
        i += 1
        command = source.data + i
        i += commandLengths[c]

        ruleResult = getReplacement(&replacement, &ruleSet, c, command, seed)
        if ruleResult in (RuleResultType.CanChange, RuleResultType.WillNotChange):
            appendSingleSymbol(target, c, command, commandLengths[c])
        else:
            if c in (b"F", b"f"):
                appendUnknownPartialSymbol(target, c, command, 1 - part, onlyPartialMoves)
            appendPartialSymbolString(target, replacement, part, onlyPartialMoves)

        seed += 4321



# Algorithm 2: Recursive
#
# Mixed calculation of all generations using left recursion.
# Benefit: Symbols that will definitely not change, will not be checked again.
###############################################################################

cdef SymbolString applyGrammarRules_Recursive(
        SymbolString source, RuleSet ruleSet, float generations,
        int seed, Py_ssize_t symbolLimit, bint onlyPartialMoves = True) except *:

    cdef SymbolString target
    initSymbolString(&target)

    if generations == 0:
        appendSymbolString(&target, &source)
        return target

    cdef int fullGenerations = <int>floor(generations)
    cdef float partialGeneration = generations % 1
    cdef int stackSize = 1 + fullGenerations - bool(partialGeneration == 0)

    # create stack of SymbolStrings to simulate recursion
    # the top of the stack will contain the source symbols
    cdef SymbolString *stack = <SymbolString*>PyMem_Malloc(sizeof(SymbolString) * stackSize)
    copySymbolString(stack + 0, &source)
    cdef Py_ssize_t i
    for i in range(1, stackSize):
        initSymbolString(stack + i)

    # one index per generation -> index of symbol that is evaluated atm
    cdef int *indices = <int*>PyMem_Malloc(sizeof(int) * stackSize)
    memset(indices, 0, sizeof(int) * stackSize)

    # one seed per generation to make growing possible
    cdef int *seeds = <int*>PyMem_Malloc(sizeof(int) * stackSize)
    for i in range(stackSize):
        seeds[i] = randomInteger(seed * 3421 + i)

    cdef void *command
    cdef unsigned char c
    cdef int currentGen = 0
    cdef RuleResultType ruleResult
    cdef SymbolString *replacement

    while currentGen > 0 or indices[0] < stack[0].length:
        c = stack[currentGen].data[indices[currentGen]]
        indices[currentGen] += 1

        command = stack[currentGen].data + indices[currentGen]
        indices[currentGen] += commandLengths[c]

        ruleResult = getReplacement(&replacement, &ruleSet, c, command, seeds[currentGen])
        seeds[currentGen] += 1

        if currentGen < stackSize - 1: # currently not in the last generation
            if ruleResult == RuleResultType.WillNotChange:
                appendSingleSymbol(&target, c, command, commandLengths[c])
            else:
                currentGen += 1
                resetSymbolString(stack + currentGen)
                indices[currentGen] = 0
                if ruleResult == RuleResultType.CanChange:
                    appendSingleSymbol(stack + currentGen, c, command, commandLengths[c])
                else:
                    appendSymbolString(stack + currentGen, replacement)
        else: # last generation
            if partialGeneration > 0: # partial last generation
                if ruleResult in (RuleResultType.WillNotChange, RuleResultType.CanChange):
                    appendSingleSymbol(&target, c, command, commandLengths[c])
                else:
                    if c in (b"F", b"f"):
                        appendUnknownPartialSymbol(&target, c, command, 1 - partialGeneration, onlyPartialMoves)
                    appendPartialSymbolString(&target, replacement, partialGeneration, onlyPartialMoves)
            else: # complete last generation
                if ruleResult in (RuleResultType.WillNotChange, RuleResultType.CanChange):
                    appendSingleSymbol(&target, c, command, commandLengths[c])
                else:
                    appendSymbolString(&target, replacement)

        while stack[currentGen].length == indices[currentGen]:
            currentGen -= 1

        if target.length > symbolLimit:
            raise Exception("Symbol limit reached. You have to increase it to make more complex objects.")

    for i in range(fullGenerations):
        freeSymbolString(stack + i)
    PyMem_Free(stack)
    PyMem_Free(seeds)
    PyMem_Free(indices)

    return target



# Partial Symbol Utilities
#################################################

cdef inline void appendPartialSymbolString(SymbolString *target, SymbolString *source, float part, bint onlyPartialMoves):
    cdef Py_ssize_t i = 0
    cdef unsigned char c
    cdef void *command
    while i < source.length:
        c = source.data[i]
        i += 1
        command = source.data + i
        i += commandLengths[c]
        appendUnknownPartialSymbol(target, c, command, part, onlyPartialMoves)

cdef inline void appendUnknownPartialSymbol(SymbolString *symbols, unsigned char opcode,
        void *command, float part, bint onlyPartialMoves):
    if opcode == b"F":
        appendPartialSymbol(symbols, opcode, (<MoveForwardGeoCommand*>command)[0], part, onlyPartialMoves)
    elif opcode == b"f":
        appendPartialSymbol(symbols, opcode, (<MoveForwardNoGeoCommand*>command)[0], part, onlyPartialMoves)
    elif opcode in (b"[", b"]"):
        appendPartialSymbol(symbols, opcode, (<NoArgCommand*>command)[0], part, onlyPartialMoves)
    elif opcode in (b"+", b"-", b"&", b"^", b"\\", b"/", b"~"):
        appendPartialSymbol(symbols, opcode, (<RotateCommand*>command)[0], part, onlyPartialMoves)
    elif opcode in (b'"', b"!"):
        appendPartialSymbol(symbols, opcode, (<ScaleCommand*>command)[0], part, onlyPartialMoves)
    elif opcode == b"T":
        appendPartialSymbol(symbols, opcode, (<TropismCommand*>command)[0], part, onlyPartialMoves)
    elif opcode in (b"A", b"B", b"X", b"Y", b"Z", b"J", b"K", b"M"):
        appendPartialSymbol(symbols, opcode, (<NoArgCommand*>command)[0], part, onlyPartialMoves)
