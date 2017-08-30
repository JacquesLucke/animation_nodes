cdef class PathActionChannel(ActionChannel):
    def __init__(self, str path):
        self.path = path

    def __richcmp__(x, y, int op):
        if not isinstance(x, y.__class__):
            return NotImplemented

        if op == 2:
            return x.path == y.path
        elif op == 3:
            return x.path != y.path

    def __hash__(self):
        return hash(self.path)

    def __repr__(self):
        return "<Channel '{}'>".format(self.path)

cdef class PathIndexActionChannel(ActionChannel):
    def __init__(self, str property, Py_ssize_t index):
        if index < 0:
            raise ValueError("Index must be >= 0")

        self.property = property
        self.index = index

    @property
    def path(self):
        return "{}[{}]".format(self.property, self.index)

    def __richcmp__(x, y, int op):
        if not isinstance(x, y.__class__):
            return NotImplemented

        if op == 2:
            return x.property == y.property and x.index == y.index
        elif op == 3:
            return x.property != y.property or x.index != y.index

    def __hash__(self):
        return hash((self.property, self.index))

    def __repr__(self):
        return "<Channel '{}'[{}]>".format(self.property, self.index)

    @classmethod
    def forArray(cls, str property, Py_ssize_t arrayLength):
        return [cls(property, i) for i in range(arrayLength)]

    @classmethod
    def forArrays(cls, list properties, Py_ssize_t arrayLength):
        return [c for p in properties for c in cls.forArray(p, arrayLength)]
