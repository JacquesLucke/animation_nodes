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
        return self.sampleEvaluationFunction(self.evaluate_LowLevel, amount, start, end)

    cpdef getTangentSamples(self, long amount, float start = 0, float end = 1):
        return self.sampleEvaluationFunction(self.evaluateTangent_LowLevel, amount, start, end)

    cdef sampleEvaluationFunction(self, EvaluationFunction evaluate,
                                        long amount, float start, float end):
        if not self.isEvaluable():
            raise Exception("spline is not evaluable")
        if start < 0 or end < 0 or start > 1 or end > 1:
            raise ValueError("start and end have to be between 0 and 1")
        if amount < 0:
            raise ValueError("amount has to be greator or equal to 0")

        cdef Vector3DList samples = Vector3DList(length = amount)
        self.sampleEvaluationFunction_LowLevel(evaluate, amount, start, end, <Vector3*>samples.base.data)
        return samples

    cdef void sampleEvaluationFunction_LowLevel(self, EvaluationFunction evaluate,
                                                long amount, float start, float end,
                                                Vector3* output):
        '''amount >= 0; 0 <= start, end <= 1'''
        if amount == 1: evaluate(self, (start + end) / 2, output)
        if amount <= 1: return

        cdef float step

        if self.cyclic and start == 0 and end == 1:
            step = (end - start) / amount
        else:
            step = (end - start) / (amount - 1)

        cdef long i
        cdef float t
        for i in range(amount):
            t = start + i * step
            # needed due to limited float accuracy
            if t > 1: t = 1
            if t < 0: t = 0
            evaluate(self, t, output + i)
