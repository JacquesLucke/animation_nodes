from . cimport Vector3

cdef float findNearestLineParameter(Vector3* lineStart, Vector3* lineDirection, Vector3* point);
