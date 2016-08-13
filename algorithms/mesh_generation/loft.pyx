from ... math.ctypes cimport Vector3
from ... math.list_operations cimport mixVec3Arrays
from ... data_structures cimport Vector3DList, Spline
from ... data_structures.splines.base_spline cimport EvaluationFunction

cdef class LinearLoft:
    cdef:
        public list splines
        public int splineSamples, subdivisions
        public float start, end
        public bint cyclic
        public str distributionType
        public int uniformResolution

    def validate(self):
        if self.start > self.end:
            self.start, self.end = self.end, self.start
        self.start = min(max(self.start, 0), 1)
        self.end = min(max(self.end, 0), 1)
        self.splineSamples = max(self.splineSamples, 2)
        self.subdivisions = max(self.subdivisions, 0)
        self.uniformResolution = max(self.uniformResolution, 2)

        if self.distributionType not in ("RESOLUTION", "UNIFORM"): return False
        if len(self.splines) < 2: return False
        for spline in self.splines:
            if not isinstance(spline, Spline): return False
            if not spline.isEvaluable(): return False
        return True

    def calcVertices(self):
        cdef:
            int splineAmount = len(self.splines)
            Vector3DList vertices = Vector3DList(length = self.getVertexAmount())
            Vector3* _vertices = <Vector3*>vertices.base.data
            Spline spline
            int i, j


        for i in range(splineAmount):
            self.writeSplineLine(self.splines[i], _vertices + i * (self.subdivisions + 1) * self.splineSamples)

        for i in range(splineAmount - 1):
            for j in range(self.subdivisions):
                self.writeMixedLine(_vertices + ((i + 1) + i * self.subdivisions + j) * self.splineSamples,
                    _vertices + i *       (self.subdivisions + 1) * self.splineSamples,
                    _vertices + (i + 1) * (self.subdivisions + 1) * self.splineSamples,
                    (j + 1) / <float>(self.subdivisions + 1))

        return vertices

    cdef getVertexAmount(self):
        cdef int splineAmount = len(self.splines)
        cdef int splineLinesAmount = splineAmount
        cdef int mixedLinesAmount = (splineAmount - 1) * self.subdivisions
        return (splineLinesAmount + mixedLinesAmount) * self.splineSamples

    cdef writeSplineLine(self, Spline spline, Vector3* target):
        cdef EvaluationFunction evaluateFunction
        if self.distributionType == "RESOLUTION":
            evaluateFunction = spline.evaluate_LowLevel
        elif self.distributionType == "UNIFORM":
            evaluateFunction = spline.evaluateUniform_LowLevel
            spline.ensureUniformConverter(self.uniformResolution)
        spline.sampleEvaluationFunction_LowLevel(evaluateFunction, self.splineSamples,
                                                 0.0, 1.0, target)

    cdef writeMixedLine(self, Vector3* target, Vector3* a, Vector3* b, float factor):
        mixVec3Arrays(target, a, b, self.splineSamples, factor)

    def calcEdgeIndices(self):
        pass

    def calcPolygonIndices(self):
        pass
