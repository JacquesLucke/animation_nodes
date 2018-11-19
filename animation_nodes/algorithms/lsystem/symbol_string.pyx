from ... data_structures cimport CharList

cdef class LSystemSymbolString:
    def __cinit__(self):
        pass

    @staticmethod
    cdef fromSymbolString(SymbolString symbols):
        cdef LSystemSymbolString obj = LSystemSymbolString()
        obj.symbols = symbols
        return obj

    def __dealloc__(self):
        freeSymbolString(&self.symbols)

    def toString(self):
        return symbolsToPyString(self.symbols)

cdef symbolsToPyString(SymbolString symbols):
    cdef list parts = []
    cdef Py_ssize_t i = 0
    cdef char c
    cdef CharList chars = CharList()

    while i < symbols.length:
        c = symbols.data[i]
        chars.append_LowLevel(c)

        i += 1
        if c == b"F":
            i += sizeof(MoveForwardGeoCommand)
        elif c == b"f":
            i += sizeof(MoveForwardNoGeoCommand)
        elif c in (b'"', b"!"):
            i += sizeof(ScaleCommand)
        elif c in (b"+", b"-", b"&", b"^", b"\\", b"/", b"~"):
            i += sizeof(RotateCommand)
        elif c == b"T":
            i += sizeof(TropismCommand)
        elif c in (b"[", b"]", b"J", b"K", b"M", b"A", b"B", b"X", b"Y", b"Z"):
            pass
        else:
            raise Exception("unknown opcode")

    return chars.data[:chars.length].decode("UTF-8")


cdef char commandLengths[256]
memset(commandLengths, 0, 256)
for symbols, size in {
        (b"+", b"-", b"&", b"^", b"\\", b"/", b"~") : sizeof(RotateCommand),
        (b'"', b"!") : sizeof(ScaleCommand),
        (b"F", ) : sizeof(MoveForwardGeoCommand),
        (b"f", ) : sizeof(MoveForwardNoGeoCommand),
        (b"T", ) : sizeof(TropismCommand)}.items():
    for symbol in symbols:
        commandLengths[ord(symbol)] = size

cdef char *getCommandLengthsArray():
    return commandLengths
