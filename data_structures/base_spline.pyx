cdef class Spline:
    pass

    def copy(self):
        raise NotImplementedError()

    def transform(self, matrix):
        raise NotImplementedError()

    def getLength(self, resolution):
        raise NotImplementedError()

    def evaluate(self, t):
        raise NotImplementedError()

    def update(self):
        raise NotImplementedError()
