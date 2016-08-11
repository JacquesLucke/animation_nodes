from mathutils import Vector
from . utils cimport calcSegmentIndicesAndFactor

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

    cpdef void markChanged(self):
        self.uniformParameters = None

    cpdef ensureUniformConverter(self, long resolution):
        resolution = max(2, resolution)
        if self.uniformParameters is None:
            self.updateUniformParameters(resolution)
        elif self.uniformParameters.length < resolution:
            self.updateUniformParameters(resolution)

    cdef updateUniformParameters(self, long resolution):
        from . poly_spline import PolySpline
        cdef Vector3DList samples = self.getSamples(resolution)
        polySpline = PolySpline(samples)
        self.uniformParameters = polySpline.getUniformParameters(resolution)

    cpdef toUniformParameter(self, float t):
        if self.uniformParameters is None:
            raise Exception("cannot evaluate uniform parameters, call spline.ensureUniformConverter() first")
        if t < 0 or t > 1:
            raise ValueError("parameter has to be between 0 and 1")
        return self.toUniformParameter_LowLevel(t)

    cdef float toUniformParameter_LowLevel(self, float t):
        cdef float factor
        cdef long indices[2]
        calcSegmentIndicesAndFactor(self.uniformParameters.length, False, t, indices, &factor)
        return self.uniformParameters.data[indices[0]] * (1 - factor) + \
               self.uniformParameters.data[indices[1]] * factor

    cpdef evaluate(self, float t):
        if t < 0 or t > 1:
            raise ValueError("parameter has to be between 0 and 1")
        if not self.isEvaluable():
            raise Exception("spline is not evaluable")
        cdef Vector3 result
        self.evaluate_LowLevel(t, &result)
        return Vector((result.x, result.y, result.z))

    cpdef evaluateTangent(self, float t):
        if t < 0 or t > 1:
            raise ValueError("parameter has to be between 0 and 1")
        if not self.isEvaluable():
            raise Exception("spline is not evaluable")
        cdef Vector3 result
        self.evaluateTangent_LowLevel(t, &result)
        return Vector((result.x, result.y, result.z))

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
