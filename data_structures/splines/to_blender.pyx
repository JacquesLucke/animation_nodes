from libc.string cimport memcpy
from .. lists.base_lists cimport FloatList
from .. lists.complex_lists cimport Vector3DList

from itertools import chain

def setSplinesOnBlenderObject(object, splines):
    if object is None: return
    if object.type != "CURVE": return

    bSplines = object.data.splines
    bSplines.clear()
    for spline in splines:
        if spline.type == "BEZIER":
            appendBezierSpline(bSplines, spline)
        if spline.type == "POLY":
            appendPolySpline(bSplines, spline)


def appendBezierSpline(bSplines, spline):
    bSpline = bSplines.new("BEZIER")
    bSpline.use_cyclic_u = spline.isCyclic

    # one point is already there
    bSpline.bezier_points.add(len(spline.points) - 1)

    raise NotImplementedError()

def appendPolySpline(bSplines, spline):
    # Blender stores 4 values for each point of a poly spline
    cdef Vector3DList points = spline.getPoints()
    cdef FloatList pointCoordinates = points.base
    cdef FloatList bPoints = FloatList(length = points.getLength() * 4)

    # Insert a one after every vector to match Blenders data format
    # [1, 2, 3, 4, 5, 6] -> [1, 2, 3, (1), 4, 5, 6, (1)]
    cdef long i
    for i in range(points.getLength()):
        memcpy(bPoints.data + i * 4,
               pointCoordinates.data + i * 3,
               sizeof(float) * 3)
        bPoints.data[i * 4 + 3] = 1

    bSpline = bSplines.new("POLY")
    bSpline.use_cyclic_u = spline.cyclic

    # one point is already there
    bSpline.points.add(pointCoordinates.length / 3 - 1)
    bSpline.points.foreach_set("co", bPoints.getMemoryView())
