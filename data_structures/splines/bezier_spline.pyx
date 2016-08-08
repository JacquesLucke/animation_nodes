cdef class BezierSpline(Spline):

    def __cinit__(self, Vector3DList points,
                        Vector3DList leftHandles,
                        Vector3DList rightHandles):
        if points is None: points = Vector3DList()
        if leftHandles is None: leftHandles = Vector3DList()
        if rightHandles is None: rightHandles = Vector3DList()

        if not (points.getLength() == leftHandles.getLength() == points.getLength()):
            raise ValueError("list lengths have to be equal")

        self.points = points
        self.leftHandles = leftHandles
        self.rightHandles = rightHandles
