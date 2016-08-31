from libc.string cimport memcpy
from . base_spline cimport Spline
from . poly_spline cimport PolySpline
from . bezier_spline cimport BezierSpline
from .. lists.base_lists cimport FloatList, Vector3DList

def setSplinesOnBlenderObject(object, list splines):
    if object is None: return
    if object.type != "CURVE": return

    bSplines = object.data.splines
    bSplines.clear()
    cdef Spline spline
    for spline in splines:
        if isinstance(spline, BezierSpline):
            appendBezierSpline(bSplines, spline)
        elif isinstance(spline, PolySpline):
            appendPolySpline(bSplines, spline)


cdef appendBezierSpline(object bSplines, BezierSpline spline):
    bSpline = bSplines.new("BEZIER")
    bSpline.use_cyclic_u = spline.cyclic

    # one point is already there
    bSpline.bezier_points.add(len(spline.points) - 1)

    bSpline.bezier_points.foreach_set("co", spline.points.getMemoryView())
    bSpline.bezier_points.foreach_set("handle_left", spline.leftHandles.getMemoryView())
    bSpline.bezier_points.foreach_set("handle_right", spline.rightHandles.getMemoryView())

cdef appendPolySpline(object bSplines, PolySpline spline):
    # Blender stores 4 values for each point of a poly spline
    cdef FloatList pointCoordinates = spline.points.base
    cdef FloatList bPoints = FloatList(length = spline.points.getLength() * 4)

    # Insert a one after every vector to match Blenders data format
    # [1, 2, 3, 4, 5, 6] -> [1, 2, 3, (1), 4, 5, 6, (1)]
    cdef long i
    for i in range(spline.points.getLength()):
        memcpy(bPoints.data + i * 4,
               pointCoordinates.data + i * 3,
               sizeof(float) * 3)
        bPoints.data[i * 4 + 3] = 1

    bSpline = bSplines.new("POLY")
    bSpline.use_cyclic_u = spline.cyclic

    # one point is already there
    points = bSpline.points
    points.add(pointCoordinates.length / 3 - 1)
    points.foreach_set("co", bPoints.getMemoryView())
