cimport cython
from ... utils.lists cimport findListSegment_LowLevel
from ... math.vector cimport distanceSquaredVec3
from ... math.conversion cimport toPyVector3, toVector3
from ... math.geometry cimport findNearestLineParameter
from ... math.list_operations cimport distanceSumOfVector3DList

ctypedef void (*EvaluateVector)(Spline, float, Vector3*)
ctypedef float (*EvaluateFloat)(Spline, float)

cdef class Spline:

    # Generic
    #############################################

    cpdef bint isEvaluable(self):
        raise NotImplementedError()

    cpdef void markChanged(self):
        self.uniformParameters = None

    def copy(self):
        raise NotImplementedError()

    def transform(self, matrix):
        raise NotImplementedError()


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
            result.data[i] = toUniformParameter_LowLevel(parameters.data[i])
        return result

    cdef float toUniformParameter_LowLevel(self, float t):
        cdef float factor
        cdef long indices[2]
        findListSegment_LowLevel(self.uniformParameters.length, False, t, indices, &factor)
        return self.uniformParameters.data[indices[0]] * (1 - factor) + \
               self.uniformParameters.data[indices[1]] * factor


    # Get Multiple Samples
    #############################################

    def Vector3DList getDistributedPoints(self, Py_ssize_t amount,
                                          float start = 0, float end = 1,
                                          str distributionType = "RESOLUTION"):
        parameters = calcSampleList(amount, start, end, self.cyclic)
        return self.samplePoints(parameters, False, distributionType)

    def Vector3DList getDistributedTangents(self, Py_ssize_t amount,
                                            float start = 0, float end = 1,
                                            str distributionType = "RESOLUTION"):
        parameters = calcSampleList(amount, start, end, self.cyclic)
        return self.sampleTangents(parameters, False, distributionType)

    def FloatList getDistributedRadii(self, Py_ssize_t amount,
                                      float start = 0, float end = 1,
                                      str distributionType = "RESOLUTION"):
        parameters = calcSampleList(amount, start, end, self.cyclic)
        return self.sampleRadii(parameters, False, distributionType)


    def Vector3DList samplePoints(self, FloatList parameters,
                                  bint checkRange = True, parameterType = "RESOLUTION"):
        cdef FloatList _parameters = self._prepareParameters(parameter, checkRange, parameterType)
        cdef Vector3DList result = Vector3DList(length = parameters.length)
        evaluateVectorFunction_Array(self, self.evaluatePoint_LowLevel,
            _parameters.data, result.data, _parameters.length)
        return result

    def Vector3DList sampleTangents(self, FloatList parameters,
                                    bint checkRange = True, parameterType = "RESOLUTION"):
        cdef FloatList _parameters = self._prepareParameters(parameter, checkRange, parameterType)
        cdef Vector3DList result = Vector3DList(length = parameters.length)
        evaluateVectorFunction_Array(self, self.evaluateTangent_LowLevel,
            _parameters.data, result.data, _parameters.length)
        return result

    def FloatList sampleRadii(self, FloatList parameters,
                              bint checkRange = True, parameterType = "RESOLUTION"):
        cdef FloatList _parameters = self._prepareParameters(parameter, checkRange, parameterType)
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
        return evaluateVectorFunction_PyResult(self, self.evaluatePoint_LowLevel, t)

    def evaluateTangent(self, float t):
        return evaluateVectorFunction_PyResult(self, self.evaluateTangent_LowLevel, t)

    def evaluateRadius(self, float t):
        return evaluateFloatFunction_PyResult(self, self.evaluatePoint_LowLevel, t)

    cdef void evaluatePoint_LowLevel(self, float, t, Vector3 *result):
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
        Vector3 _point = toVector3(point)
        Vector3 nearestPoint, nearestTangent
        self.projectExtended_LowLevel(_point, &nearestPoint, &nearestTangent)
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

cdef FloatList calcSampleList(Py_ssize_t length, float start, float end, bint cyclic):
    if length < 0:
        raise Exception("length has to be >= 0")
    if not (0 <= start <= 1 and 0 <= end <= 1):
        raise Exception("start and end values have to be between 0 and 1")

    if length == 0:
        return FloatList()
    if length == 1:
        return FloatList.fromValue((start + end) / 2)

    cdef float step
    if cyclic and start == 0 and end == 1:
        step = (end - start) / amount
    else:
        step = (end - start) / (amount - 1)

    cdef Py_ssize_t i
    cdef float t
    cdef FloatList result = FloatList(length = length)
    for i in range(amount):
        t = start + i * step
        if t > 1: t = 1
        if t < 0: t = 0
        result.data[i] = t
    return result



# Evaluate Functions with PyObject Result
######################################################

cdef evaluateVectorFunction_PyResult(Spline spline, EvaluateVector evaluate, float t):
    if t < 0 or t > 1:
        raise ValueError("parameter has to be between 0 and 1")
    if not spline.isEvaluable():
        raise Exception("spline is not evaluable")
    cdef Vector3 result
    evaluate(spline, t, &result)
    return toPyVector3(&result)

cdef evaluateFloatFunction_PyResult(Spline spline, EvaluateFloat evaluate, float t):
    if t < 0 or t > 1:
        raise ValueError("parameter has to be between 0 and 1")
    if not spline.isEvaluable():
        raise Exception("spline is not evaluable")
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
