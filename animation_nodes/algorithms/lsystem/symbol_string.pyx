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
        if c == "F":
            i += sizeof(MoveForwardGeoCommand)
        elif c == "f":
            i += sizeof(MoveForwardNoGeoCommand)
        elif c in ('"', "!"):
            i += sizeof(ScaleCommand)
        elif c in ("+", "-", "&", "^", "\\", "/", "~"):
            i += sizeof(RotateCommand)
        elif c == "T":
            i += sizeof(TropismCommand)
        elif c in ("[", "]", "J", "K", "M", "A", "B", "X", "Y", "Z"):
            pass
        else:
            raise Exception("unknown opcode")

    return chars.data[:chars.length].decode("UTF-8")


cdef char commandLengths[256]
memset(commandLengths, 0, 256)
for symbols, size in {
        ("+", "-", "&", "^", "\\", "/", "~") : sizeof(RotateCommand),
        ('"', "!") : sizeof(ScaleCommand),
        ("F", ) : sizeof(MoveForwardGeoCommand),
        ("f", ) : sizeof(MoveForwardNoGeoCommand),
        ("T", ) : sizeof(TropismCommand)}.items():
    for symbol in symbols:
        commandLengths[ord(symbol)] = size

cdef char *getCommandLengthsArray():
    return commandLengths