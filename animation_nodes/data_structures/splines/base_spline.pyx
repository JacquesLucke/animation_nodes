cimport cython
from ... utils.lists cimport findListSegment_LowLevel
from ... math.vector cimport distanceSquaredVec3
from ... math.conversion cimport toPyVector3, toVector3
from ... math.geometry cimport findNearestLineParameter
from ... math.list_operations cimport distanceSumOfVector3DList

ctypedef void (*EvaluateVector)(Spline, float, Vector3*)
ctypedef float (*EvaluateFloat)(Spline, float)

cdef class Spline:

    cpdef void markChanged(self):
        self.uniformParameters = None


    # Generic
    #############################################

    def copy(self):
        raise NotImplementedError()

    def transform(self, matrix):
        raise NotImplementedError()


    # Evaluability
    #############################################

    cpdef bint isEvaluable(self):
        raise NotImplementedError()

    cdef checkEvaluability(self):
        if not self.isEvaluable():
            raise Exception("Spline is not evaluable")


    # Uniform Conversion
    #############################################

    cdef checkUniformConverter(self):
        if self.uniformParameters is None:
            raise Exception("cannot evaluate uniform parameters, call spline.ensureUniformConverter(resolution) first")

    cpdef ensureUniformConverter(self, long minResolution):
        cdef long pointAmount = len(self.points)
        cdef long totalResolution = pointAmount + max((pointAmount - 1), 0) * max(0, minResolution)
        if self.uniformParameters is None:
            self._updateUniformParameters(totalResolution)
        elif self.uniformParameters.length < totalResolution:
            self._updateUniformParameters(totalResolution)

    cdef _updateUniformParameters(self, long totalResolution):
        from . poly_spline import PolySpline
        if isinstance(self, PolySpline): polySpline = self
        else: polySpline = PolySpline(self.getDistributedPoints(totalResolution))
        self.uniformParameters = polySpline.getUniformParameters(totalResolution)


    def toUniformParameter(self, float t):
        self.checkUniformConverter()
        if t < 0 or t > 1:
            raise ValueError("parameter has to be between 0 and 1")
        return self.toUniformParameter_LowLevel(t)

    def toUniformParameters(self, FloatList parameters):
        self.checkUniformConverter()
        cdef FloatList result = FloatList(length = parameters.length)
        cdef Py_ssize_t i
        for i in range(parameters.length):
            result.data[i] = self.toUniformParameter_LowLevel(parameters.data[i])
        return result

    cdef float toUniformParameter_LowLevel(self, float t):
        cdef float factor
        cdef long indices[2]
        findListSegment_LowLevel(self.uniformParameters.length, False, t, indices, &factor)
        return self.uniformParameters.data[indices[0]] * (1 - factor) + \
               self.uniformParameters.data[indices[1]] * factor


    # Get Multiple Samples
    #############################################

    cdef calcDistributedPoints_LowLevel(self, Py_ssize_t amount, Vector3 *result,
                                        float start = 0, float end = 1,
                                        str distributionType = "RESOLUTION"):
        evaluateDistributed(self, amount, self.evaluatePoint_LowLevel,
            start, end, distributionType, result)

    cdef calcDistributedTangents_LowLevel(self, Py_ssize_t amount, Vector3 *result,
                                          float start = 0, float end = 1,
                                          str distributionType = "RESOLUTION"):
        evaluateDistributed(self, amount, self.evaluateTangent_LowLevel,
            start, end, distributionType, result)

    cdef calcDistributedRadii_LowLevel(self, Py_ssize_t amount, float *result,
                                    float start = 0, float end = 1,
                                    str distributionType = "RESOLUTION"):
        evaluateDistributed(self, amount, self.evaluateRadius_LowLevel,
            start, end, distributionType, result)


    def getDistributedPoints(self, Py_ssize_t amount,
                             float start = 0, float end = 1,
                             str distributionType = "RESOLUTION"):
        cdef Vector3DList result = Vector3DList(length = amount)
        self.calcDistributedPoints_LowLevel(amount, result.data, start, end, distributionType)
        return result

    def getDistributedTangents(self, Py_ssize_t amount,
                               float start = 0, float end = 1,
                               str distributionType = "RESOLUTION"):
        cdef Vector3DList result = Vector3DList(length = amount)
        self.calcDistributedTangents_LowLevel(amount, result.data, start, end, distributionType)
        return result

    def getDistributedRadii(self, Py_ssize_t amount,
                            float start = 0, float end = 1,
                            str distributionType = "RESOLUTION"):
        cdef FloatList result = FloatList(length = amount)
        self.calcDistributedRadii_LowLevel(amount, result.data, start, end, distributionType)
        return result


    def samplePoints(self, FloatList parameters,
                     bint checkRange = True, parameterType = "RESOLUTION"):
        cdef FloatList _parameters = self._prepareParameters(parameters, checkRange, parameterType)
        cdef Vector3DList result = Vector3DList(length = parameters.length)
        evaluateVectorFunction_Array(self, self.evaluatePoint_LowLevel,
            _parameters.data, result.data, _parameters.length)
        return result

    def sampleTangents(self, FloatList parameters,
                       bint checkRange = True, parameterType = "RESOLUTION"):
        cdef FloatList _parameters = self._prepareParameters(parameters, checkRange, parameterType)
        cdef Vector3DList result = Vector3DList(length = parameters.length)
        evaluateVectorFunction_Array(self, self.evaluateTangent_LowLevel,
            _parameters.data, result.data, _parameters.length)
        return result

    def sampleRadii(self, FloatList parameters,
                    bint checkRange = True, parameterType = "RESOLUTION"):
        cdef FloatList _parameters = self._prepareParameters(parameters, checkRange, parameterType)
        cdef FloatList result = FloatList(length = parameters.length)
        evaluateFloatFunction_Array(self, self.evaluateRadius_LowLevel,
            _parameters.data, result.data, _parameters.length)
        return result

    def _prepareParameters(self, FloatList parameters, bint checkRange, str parameterType):
        if checkRange:
            if not parameters.allValuesInRange(0, 1):
                raise Exception("parameters have to be between 0 and 1")

        if parameterType == "RESOLUTION":
            outParameters = parameters
        elif parameterType == "UNIFORM":
            outParameters = self.toUniformParameters(parameters)
        else:
            raise Exception("Unknown parameterType; expected 'RESOLUTION' or 'UNIFORM' but got {}".format(repr(parameterType)))

        return outParameters



   # Evaluate Single Parameter
   #############################################

    def evaluatePoint(self, float t):
        return evaluateFunction_PyResult(self, self.evaluatePoint_LowLevel, t)

    def evaluateTangent(self, float t):
        return evaluateFunction_PyResult(self, self.evaluateTangent_LowLevel, t)

    def evaluateRadius(self, float t):
        return evaluateFunction_PyResult(self, self.evaluateRadius_LowLevel, t)

    cdef void evaluatePoint_LowLevel(self, float t, Vector3 *result):
        raise NotImplementedError()

    cdef void evaluateTangent_LowLevel(self, float t, Vector3 *result):
        raise NotImplementedError()

    cdef float evaluateRadius_LowLevel(self, float t):
        raise NotImplementedError()


    # Projection
    #############################################

    def project(self, point):
        if not self.isEvaluable():
            raise Exception("spline is not evaluable")
        cdef Vector3 _point = toVector3(point)
        return self.project_LowLevel(&_point)

    def projectExtended(self, point):
        cdef Vector3 _point = toVector3(point)
        cdef Vector3 nearestPoint, nearestTangent
        self.projectExtended_LowLevel(&_point, &nearestPoint, &nearestTangent)
        return toPyVector3(&nearestPoint), toPyVector3(&nearestTangent)

    cdef float project_LowLevel(self, Vector3 *point):
        raise NotImplementedError()

    cdef void projectExtended_LowLevel(self, Vector3 *point,
                                       Vector3 *resultPoint, Vector3 *resultTangent):
        cdef:
            float t, smallestDistance, distance
            Vector3 nearestProjection, projection
            Vector3 nearestTangent
            Vector3 startPoint, startTangent
            Vector3 endPoint, endTangent

        t = self.project_LowLevel(point)
        self.evaluatePoint_LowLevel(t, &nearestProjection)
        self.evaluateTangent_LowLevel(t, &nearestTangent)

        if not self.cyclic:
            smallestDistance = distanceSquaredVec3(point, &nearestProjection)

            self.evaluatePoint_LowLevel(0, &startPoint)
            self.evaluatePoint_LowLevel(1, &endPoint)
            self.evaluateTangent_LowLevel(0, &startTangent)
            self.evaluateTangent_LowLevel(1, &endTangent)

            t = findNearestLineParameter(&startPoint, &startTangent, point)
            if t < 0:
                projection.x = startPoint.x + t * startTangent.x
                projection.y = startPoint.y + t * startTangent.y
                projection.z = startPoint.z + t * startTangent.z
                distance = distanceSquaredVec3(point, &projection)
                if distance < smallestDistance:
                    smallestDistance = distance
                    nearestProjection = projection
                    nearestTangent = startTangent

            t = findNearestLineParameter(&endPoint, &endTangent, point)
            if t > 0:
                projection.x = endPoint.x + t * endTangent.x
                projection.y = endPoint.y + t * endTangent.y
                projection.z = endPoint.z + t * endTangent.z
                distance = distanceSquaredVec3(point, &projection)
                if distance < smallestDistance:
                    smallestDistance = distance
                    nearestProjection = projection
                    nearestTangent = endTangent

        resultPoint[0] = nearestProjection
        resultTangent[0] = nearestTangent


    # Trimming
    #############################################

    def getTrimmedCopy(self, float start = 0.0, float end = 1.0):
        if not self.isEvaluable():
            raise Exception("spline is not evaluable")
        if start < 0 or end < 0 or start > 1 or end > 1:
            raise ValueError("start and end have to be between 0 and 1")

        cdef float _start, _end
        if start < end:
            _start, _end = start, end
        else:
            _start, _end = start, start
        cdef Spline trimmedSpline = self.getTrimmedCopy_LowLevel(_start, _end)
        return trimmedSpline

    cdef Spline getTrimmedCopy_LowLevel(self, float start, float end):
        raise NotImplementedError()


    # Length
    #############################################

    def getLength(self, int resolution = 0):
        return self.getPartialLength(0.0, 1.0, resolution)

    def getPartialLength(self, float start, float end, int resolution = 100):
        if not self.isEvaluable(): return 0.0
        start = min(max(start, 0), 1)
        end = min(max(end, 0), 1)
        return distanceSumOfVector3DList(self.getDistributedPoints(resolution, start, end))


    # Misc
    #############################################

    def __repr__(self):
        return "<{} object at {}>".format(type(self).__name__, hex(id(self)))


# Float Range
######################################################

ctypedef fused EvaluateFunction:
    EvaluateVector
    EvaluateFloat

cdef evaluateDistributed(Spline spline, Py_ssize_t amount, EvaluateFunction evaluate, float start, float end, str distributionType, void *target):
    spline.checkEvaluability()
    if amount < 0:
        raise ValueError("amount has to be >= 0")
    if not (0 <= start <= 1 and 0 <= end <= 1):
        raise ValueError("start and end values have to be between 0 and 1")
    if distributionType not in ("RESOLUTION", "UNIFORM"):
        raise ValueError("expected 'RESOLUTION' or 'UNIFORM' as distribution type")
    if distributionType == "UNIFORM":
        spline.checkUniformConverter()

    if amount == 0:
        return
    if amount == 1:
        if EvaluateFunction is EvaluateVector:
            evaluate(spline, (start + end) / 2, <Vector3*>target)
        elif EvaluateFunction is EvaluateFloat:
            (<float*>target)[0] = evaluate(spline, (start + end) / 2)
        return

    cdef float step
    if spline.cyclic and start == 0 and end == 1:
        step = (end - start) / amount
    else:
        step = (end - start) / (amount - 1)

    cdef Py_ssize_t i
    cdef float t
    cdef bint convertToUniform = distributionType == "UNIFORM"
    for i in range(amount):
        t = start + i * step
        if t > 1: t = 1
        elif t < 0: t = 0
        if convertToUniform:
            t = spline.convertToUniform(t)
        if EvaluateFunction is EvaluateVector:
            evaluate(spline, t, <Vector3*>target + i)
        elif EvaluateFunction is EvaluateFloat:
            (<float*>target)[i] = evaluate(spline, t)


# Evaluate Functions with PyObject Result
######################################################

cdef evaluateFunction_PyResult(Spline spline, EvaluateFunction evaluate, float t):
    if t < 0 or t > 1:
        raise ValueError("parameter has to be between 0 and 1")
    if not spline.isEvaluable():
        raise Exception("spline is not evaluable")

    cdef Vector3 result
    if EvaluateFunction is EvaluateVector:
        evaluate(spline, t, &result)
        return toPyVector3(&result)

    if EvaluateFunction is EvaluateFloat:
        return evaluate(spline, t)


# Evaluate Function on Array
######################################################

cdef evaluateVectorFunction_Array(Spline spline, EvaluateVector evaluate,
                                  float *ts, Vector3 *results, Py_ssize_t amount):
    cdef Py_ssize_t i
    for i in range(amount):
        evaluate(spline, ts[i], results + i)

cdef evaluateFloatFunction_Array(Spline spline, EvaluateFloat evaluate,
                                 float *ts, float *results, Py_ssize_t amount):
    cdef Py_ssize_t i
    for i in range(amount):
        results[i] = evaluate(spline, ts[i])
