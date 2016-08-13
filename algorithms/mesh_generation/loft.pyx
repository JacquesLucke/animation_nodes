from ... math.ctypes cimport Vector3
from ... math.list_operations cimport mixVec3Arrays
from ... data_structures cimport Vector3DList, Spline
from ... data_structures.splines.base_spline cimport EvaluationFunction
from ... utils.lists cimport calcSegmentIndicesAndFactor

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
            int samples = self.splineSamples
            int subdivisions = self.subdivisions
            int splineAmount = len(self.splines)
            long startIndices[2]
            long endIndices[2]
            float startT, endT

        calcSegmentIndicesAndFactor(splineAmount, self.cyclic, self.start, startIndices, &startT)
        calcSegmentIndicesAndFactor(splineAmount, self.cyclic, self.end, endIndices, &endT)

        cdef:
            Vector3DList vertices, tmp1, tmp2
            Vector3* _vertices
            Vector3* _tmp1
            Vector3* _tmp2
            long totalLineAmount, i, lineIndex

        if endIndices[1] > 0:
            totalLineAmount = endIndices[1] - startIndices[0] + 1
            totalLineAmount += (totalLineAmount - 1) * subdivisions
        elif endIndices[1] == 0: # <- cyclic
            totalLineAmount = splineAmount - startIndices[0] + 1
            totalLineAmount += (totalLineAmount - 1) * subdivisions
            #if endT == 1.0:
            #    totalLineAmount -= 1

        vertices = Vector3DList(length = totalLineAmount * samples)
        _vertices = <Vector3*>vertices.base.data

        if startIndices[0] == endIndices[0]:
            tmp1 = Vector3DList(length = samples); _tmp1 = <Vector3*>tmp1.base.data
            tmp2 = Vector3DList(length = samples); _tmp2 = <Vector3*>tmp2.base.data
            self.writeSplineLine(self.splines[startIndices[0]], _tmp1)
            self.writeSplineLine(self.splines[startIndices[1]], _tmp2)

            self.writeMixedLine(target = _vertices,
                    sourceA = _tmp1,
                    sourceB = _tmp2,
                    factor = startT)
            self.writeMixedLine(target = _vertices + (subdivisions + 1) * samples,
                    sourceA = _tmp1,
                    sourceB = _tmp2,
                    factor = endT)
            self.writeSubdivisionLines(target = _vertices + samples,
                    sourceA = _vertices,
                    sourceB = _vertices + (subdivisions + 1) * samples)
        else:
            tmp1 = Vector3DList(length = samples); _tmp1 = <Vector3*>tmp1.base.data
            tmp2 = Vector3DList(length = samples); _tmp2 = <Vector3*>tmp2.base.data
            self.writeSplineLine(self.splines[startIndices[0]], _tmp1)
            self.writeSplineLine(self.splines[startIndices[1]], _tmp2)
            self.writeMixedLine(target = _vertices,
                    sourceA = _tmp1,
                    sourceB = _tmp2,
                    factor = startT)
            self.writeSplineLine(self.splines[endIndices[0]], _tmp1)
            self.writeSplineLine(self.splines[endIndices[1]], _tmp2)
            self.writeMixedLine(target = _vertices + (totalLineAmount - 1) * samples,
                    sourceA = _tmp1,
                    sourceB = _tmp2,
                    factor = endT)

            for i in range(endIndices[0] - startIndices[0]):
                spline = self.splines[i + startIndices[1]]
                lineIndex = (i + 1) * (subdivisions + 1)
                self.writeSplineLine(spline, _vertices + lineIndex * samples)
                self.writeSubdivisionLines(
                        target = _vertices + (lineIndex - subdivisions) * samples,
                        sourceA = _vertices + (lineIndex - subdivisions - 1) * samples,
                        sourceB = _vertices + lineIndex * samples)

            self.writeSubdivisionLines(
                    target = _vertices + (totalLineAmount - 1 - subdivisions) * samples,
                    sourceA = _vertices + (totalLineAmount - 2 - subdivisions) * samples,
                    sourceB = _vertices + (totalLineAmount - 1) * samples)

        if self.cyclic and self.start == 0 and self.end == 1:
            vertices.base.length -= 3 * samples

        return vertices

    cdef writeSplineLine(self, Spline spline, Vector3* target):
        cdef EvaluationFunction evaluateFunction
        if self.distributionType == "RESOLUTION":
            evaluateFunction = spline.evaluate_LowLevel
        elif self.distributionType == "UNIFORM":
            evaluateFunction = spline.evaluateUniform_LowLevel
            spline.ensureUniformConverter(self.uniformResolution)
        spline.sampleEvaluationFunction_LowLevel(evaluateFunction, self.splineSamples,
                                                 0.0, 1.0, target)

    cdef writeMixedLine(self, Vector3* target, Vector3* sourceA, Vector3* sourceB, float factor):
        mixVec3Arrays(target, sourceA, sourceB, self.splineSamples, factor)

    cdef writeSubdivisionLines(self, Vector3* target, Vector3* sourceA, Vector3* sourceB):
        cdef int i
        for i in range(self.subdivisions):
            self.writeMixedLine(target = target + i * self.splineSamples,
                sourceA = sourceA,
                sourceB = sourceB,
                factor = (i + 1) / <float>(self.subdivisions + 1))


    def calcEdgeIndices(self):
        pass

    def calcPolygonIndices(self):
        pass
