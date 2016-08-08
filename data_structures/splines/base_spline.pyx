from .. lists.complex_lists cimport Vector3DList

cdef class Spline:
    pass

    cpdef Spline copy(self):
        raise NotImplementedError()

    cpdef transform(self, matrix):
        raise NotImplementedError()

    cpdef double getLength(self, resolution = 0):
        raise NotImplementedError()

    cpdef bint isEvaluable(self):
        raise NotImplementedError()

    cpdef evaluate(self, float t):
        raise NotImplementedError()

    cpdef evaluateTangent(self, float t):
        raise NotImplementedError()

    cpdef void update(self):
        raise NotImplementedError()

    cdef void evaluate_LowLevel(self, float t, Vector3* result):
        raise NotImplementedError()

    cdef void evaluateTangent_LowLevel(self, float t, Vector3* result):
        raise NotImplementedError()


    cpdef getSamples(self, long amount, float start = 0, float end = 1):
        if not self.isEvaluable():
            raise Exception("spline is not evaluable")
        if start < 0 or end < 0 or start > 1 or end > 1:
            raise Exception("start and end have to be between 0 and 1")
        if amount == 0:
            return Vector3DList()
        if amount == 1:
            return Vector3DList.fromValues([self.evaluate((start + end) / 2)])

        cdef:
            Vector3DList samples = Vector3DList(length = amount)
            Vector3* _samples = <Vector3*>samples.base.data
            long stepDivisor, i
            float step, t

        if self.cyclic and start == 0 and end == 1:
            stepDivisor = amount
        else:
            stepDivisor = amount - 1
        step = (end - start) / stepDivisor
        for i in range(amount):
            t = start + i * step
            # needed due to limited float accuracy
            if t > 1: t = 1
            if t < 0: t = 0
            self.evaluate_LowLevel(t, _samples + i)
        return samples
