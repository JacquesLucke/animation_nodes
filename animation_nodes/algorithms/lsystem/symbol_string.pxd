from libc.string cimport memcpy, memset
from libc.stdint cimport uint32_t, uint64_t
from cpython cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free

cdef struct SymbolString:
    unsigned char *data
    Py_ssize_t length
    Py_ssize_t capacity

cdef class LSystemSymbolString:
    cdef SymbolString symbols

    @staticmethod
    cdef fromSymbolString(SymbolString symbols)


cdef struct NoArgCommand:
    char dummy
cdef struct MoveForwardGeoCommand:
    unsigned char id
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

cdef inline void initSymbolString(SymbolString *symbols):
    cdef Py_ssize_t DEFAULT_SIZE = 1
    symbols.data = <unsigned char*>PyMem_Malloc(DEFAULT_SIZE)
    symbols.length = 0
    symbols.capacity = DEFAULT_SIZE

cdef inline void freeSymbolString(SymbolString *symbols):
    PyMem_Free(symbols.data)

cdef inline void resetSymbolString(SymbolString *symbols):
    symbols.length = 0

cdef inline void copySymbolString(SymbolString *target, SymbolString *source):
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

cdef inline void appendPartialSymbol(SymbolString *symbols, unsigned char prefix,
        Command command, float part, bint onlyPartialMoves):
    if Command is NoArgCommand:
        appendNoArgSymbol(symbols, prefix)
    elif Command is MoveForwardGeoCommand:
        appendSymbol(symbols, prefix, MoveForwardGeoCommand(command.id, command.distance * part))
    elif Command is MoveForwardNoGeoCommand:
        appendSymbol(symbols, prefix, MoveForwardNoGeoCommand(command.distance * part))
    else:
        if onlyPartialMoves:
            appendSymbol(symbols, prefix, command)
        else:
            if Command is RotateCommand:
                appendSymbol(symbols, prefix, RotateCommand(command.angle * part))
            elif Command is ScaleCommand:
                appendSymbol(symbols, prefix, ScaleCommand((1 - part) + command.factor * part))
            elif Command is TropismCommand:
                appendSymbol(symbols, prefix, TropismCommand(command.gravity * part))


cdef inline void appendNoArgSymbol(SymbolString *symbols, unsigned char prefix):
    appendSymbol(symbols, prefix, NoArgCommand(0))

cdef inline void appendSymbolBuffer(SymbolString *symbols, void *buffer, Py_ssize_t length):
    if symbols.length + length > symbols.capacity:
        growSymbolString(symbols, length)
    memcpy(symbols.data + symbols.length, buffer, length)
    symbols.length += length

cdef inline void appendSymbolString(SymbolString *symbols, SymbolString *other):
    appendSymbolBuffer(symbols, other.data, other.length)

cdef inline void appendSingleSymbol(SymbolString *symbols, unsigned char prefix, void *command, char length):
    if symbols.length + length + 1 > symbols.capacity:
        growSymbolString(symbols, length + 1)
    symbols.data[symbols.length] = prefix
    optimizedMemcpy(symbols.data + symbols.length + 1, command, length)
    symbols.length += 1 + length

cdef inline void optimizedMemcpy(void *target, void *source, char length):
    if length == 0:
        return
    elif length == 4:
        memcpy(target, source, 4)
    elif length == 8:
        memcpy(target, source, 8)
    else:
        memcpy(target, source, length)

cdef char *getCommandLengthsArray()