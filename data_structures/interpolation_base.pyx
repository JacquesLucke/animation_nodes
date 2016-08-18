cdef class InterpolationBase:
    def __call__(self, float x):
        x = min(max(x, 0), 1)
        return self.evaluate(x)

    cdef float evaluate(self, float x):
        raise NotImplementedError()
