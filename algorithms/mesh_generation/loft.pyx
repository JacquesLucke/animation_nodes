from ... math.ctypes cimport Vector3
from ... math.list_operations cimport mixVector3DLists_LowLevel
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
            Vector3DList vertices = Vector3DList(length = (splineAmount + (splineAmount - 1) * self.subdivisions) * self.splineSamples)
            Vector3* _vertices = <Vector3*>vertices.base.data
            Spline spline
            int i, j
            EvaluationFunction evaluateFunction

        spline = self.splines[0]
        if self.distributionType == "RESOLUTION":
            evaluateFunction = spline.evaluate_LowLevel
        elif self.distributionType == "UNIFORM":
            evaluateFunction = spline.evaluateUniform_LowLevel
            for spline in self.splines:
                spline.ensureUniformConverter(self.uniformResolution)

        for i in range(splineAmount):
            spline = self.splines[i]
            spline.sampleEvaluationFunction_LowLevel(
                evaluateFunction, self.splineSamples,
                self.start, self.end, _vertices + i * (self.subdivisions + 1) * self.splineSamples)
                
        for i in range(splineAmount - 1):
            for j in range(self.subdivisions):
                mixVector3DLists_LowLevel(_vertices + (i + 1) * self.splineSamples + i * self.subdivisions * self.splineSamples + j * self.splineSamples,
                    _vertices + i * (self.subdivisions + 1) * self.splineSamples,
                    _vertices + (i + 1) * (self.subdivisions + 1) * self.splineSamples,
                    self.splineSamples,
                    (j + 1) / <float>(self.subdivisions + 1))

        return vertices

    def calcEdgeIndices(self):
        pass

    def calcPolygonIndices(self):
        pass
