cdef class InterpolationBase:
    def __call__(self, double x):
        x = min(max(x, 0), 1)
        return self.evaluate(x)

    cdef double evaluate(self, double x):
        raise NotImplementedError()

    def __repr__(self):
        return "<{} Interpolation>".format(self.__class__.__name__)
