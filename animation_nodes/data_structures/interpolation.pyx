cdef class Interpolation:
    def __cinit__(self):
        self.clamped = False

    def __call__(self, double x):
        x = min(max(x, 0), 1)
        return self.evaluate(x)

    cdef double evaluate(self, double x):
        raise NotImplementedError()

    def __repr__(self):
        return "<Interpolation {}>".format(repr(self.__class__.__name__))
