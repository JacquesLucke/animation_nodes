import bpy
from bpy.props import *
from ... math cimport Vector3
from ... utils.limits cimport INT_MAX
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures cimport (
    Mesh,
    Falloff,
    FloatList,
    Vector3DList,
    EdgeIndicesList,
    FalloffEvaluator,
    VirtualDoubleList,
    PolygonIndicesList,
)

class MarchingSquaresNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MarchingSquaresNode"
    bl_label = "Marching Squares"
    errorHandlingType = "EXCEPTION"

    __annotations__ = {}

    __annotations__["clampFalloff"] = BoolProperty(name = "Clamp Falloff", default = False)
    __annotations__["useToleranceList"] = VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Integer", "X Divisions", "xDivisions", value = 3, minValue = 2)
        self.newInput("Integer", "Y Divisions", "yDivisions", value = 3, minValue = 2)
        self.newInput("Float", "Size", "size", value = 5)
        self.newInput("Falloff", "Falloff", "falloff")
        self.newInput(VectorizedSocket("Float", "useToleranceList",
            ("Tolerance", "tolerances"), ("Tolerances", "tolerances")), value = 0.25)

        self.newOutput("Mesh", "Mesh", "mesh")
        self.newOutput("Vector List", "Grid Points", "points", hide = True)

    def execute(self, xDivisions, yDivisions, size, falloff, tolerances):
        cdef VirtualDoubleList _tolerances = VirtualDoubleList.create(tolerances, 0.001)
        cdef long amountTol
        if not self.useToleranceList:
            amountTol = 1
        else:
            amountTol = _tolerances.getRealLength()

        cdef double xDis, yDis
        cdef Vector3DList points
        points, xDis, yDis = getGridPoints(xDivisions, yDivisions, 1, size, size, size)

        cdef FloatList strengths = self.getFieldStrengths(points, falloff)
        cdef long nx, ny, amountCell
        nx, ny = limitAmount(xDivisions), limitAmount(yDivisions)

        cdef Py_ssize_t i, j, k, offset, ia, ib, ic, id
        cdef double _xDis, _yDis
        cdef long _nx, _ny

        _xDis, _yDis = xDis / 2.0, yDis / 2.0
        _nx, _ny = nx - 1, ny - 1
        amountCell = _nx * _ny

        meshes = []
        for i in range(_ny):
            offset = nx * i
            for j in range(_nx):
                # Counter-Clockwise
                ia = nx + offset + j
                ib = ia + 1
                id = j + offset
                ic = id + 1

                for k in range(amountTol):
                    meshes.append(getMeshOfSquare(points, strengths, <float>_tolerances.get(k),
                                                  _xDis, _yDis, ia, ib, ic, id))

        return Mesh.join(*meshes), points

    def getFieldStrengths(self, Vector3DList vectors, falloff):
        cdef FalloffEvaluator falloffEvaluator = self.getFalloffEvaluator(falloff)
        cdef FloatList influences = falloffEvaluator.evaluateList(vectors)
        return influences

    def getFalloffEvaluator(self, falloff):
        try: return falloff.getEvaluator("LOCATION", self.clampFalloff)
        except: self.raiseErrorMessage("This falloff cannot be evaluated for vectors")

def getMeshOfSquare(Vector3DList points, FloatList strengths, float tolerance, double _xDis,
                    double _yDis, Py_ssize_t ia, Py_ssize_t ib, Py_ssize_t ic, Py_ssize_t id):
    cdef float a, b, c, d
    a, b, c, d = strengths.data[ia], strengths.data[ib], strengths.data[ic], strengths.data[id]

    cdef Vector3 va, vb, vc, vd, v1, v2
    va, vb, vc, vd = points.data[ia], points.data[ib], points.data[ic], points.data[id]

    cdef Vector3DList vertices = Vector3DList(length = 2)
    cdef EdgeIndicesList edges = EdgeIndicesList(length = 1)
    cdef PolygonIndicesList polygons = PolygonIndicesList()

    cdef long index = binaryToDecimal(tolerance, a, b, c, d)
    v1.z = 0.
    v2.z = 0.
    if index == 0:
        return Mesh()
    elif index == 1:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = lerp(tolerance, vd.x, vc.x, d, c)
        v1.y = vc.y
        v2.x = vd.x
        v2.y = lerp(tolerance, vd.y, va.y, d, a)
        vertices.data[0] = v1
        vertices.data[1] = v2
        return Mesh(vertices, edges, polygons)
    elif index == 2:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = lerp(tolerance, vc.x, vd.x, c, d)
        v1.y = vc.y
        v2.x = vc.x
        v2.y = lerp(tolerance, vc.y, vb.y, c, b)
        vertices.data[0] = v1
        vertices.data[1] = v2
        return Mesh(vertices, edges, polygons)
    elif index == 3:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = vc.x
        v1.y = lerp(tolerance, vc.y, vb.y, c, b)
        v2.x = vd.x
        v2.y = lerp(tolerance, vd.y, va.y, d, a)
        vertices.data[0] = v1
        vertices.data[1] = v2
        return Mesh(vertices, edges, polygons)
    elif index == 4:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = lerp(tolerance, vb.x, va.x, b, a)
        v1.y = vb.y
        v2.x = vb.x
        v2.y = lerp(tolerance, vb.y, vc.y, b, c)
        vertices.data[0] = v1
        vertices.data[1] = v2
        return Mesh(vertices, edges, polygons)
    elif index == 5:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = vb.x
        v1.y = lerp(tolerance, vb.y, vc.y, b, c)
        v2.x = lerp(tolerance, vd.x, vc.x, d, c)
        v2.y = vd.y
        vertices.data[0] = v1
        vertices.data[1] = v2

        edges.append((2,3))

        v1.x = lerp(tolerance, vb.x, va.x, b, a)
        v1.y = vb.y
        v2.x = vd.x
        v2.y = lerp(tolerance, vd.y, va.y, d, a)
        vertices.append_LowLevel(v1)
        vertices.append_LowLevel(v2)
        return Mesh(vertices, edges, polygons)
    elif index == 6:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = lerp(tolerance, vb.x, va.x, b, a)
        v1.y = vb.y
        v2.x = lerp(tolerance, vc.x, vd.x, c, d)
        v2.y = vc.y
        vertices.data[0] = v1
        vertices.data[1] = v2
        return Mesh(vertices, edges, polygons)
    elif index == 7:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = lerp(tolerance, vb.x, va.x, b, a)
        v1.y = vb.y
        v2.x = vd.x
        v2.y = lerp(tolerance, vd.y, va.y, d, a)
        vertices.data[0] = v1
        vertices.data[1] = v2
        return Mesh(vertices, edges, polygons)
    elif index == 8:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = lerp(tolerance, va.x, vb.x, a, b)
        v1.y = va.y
        v2.x = va.x
        v2.y = lerp(tolerance, va.y, vd.y, a, d)
        vertices.data[0] = v1
        vertices.data[1] = v2
        return Mesh(vertices, edges, polygons)
    elif index == 9:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = lerp(tolerance, va.x, vb.x, a, b)
        v1.y = va.y
        v2.x = lerp(tolerance, vd.x, vc.x, d, c)
        v2.y = vd.y
        vertices.data[0] = v1
        vertices.data[1] = v2
        return Mesh(vertices, edges, polygons)
    elif index == 10:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = lerp(tolerance, va.x, vb.x, a, b)
        v1.y = va.y
        v2.x = vc.x
        v2.y = lerp(tolerance, vc.y, vb.y, c, b)
        vertices.data[0] = v1
        vertices.data[1] = v2

        edges.append((2,3))

        v1.x = va.x
        v1.y = lerp(tolerance, va.y, vd.y, a, d)
        v2.x = lerp(tolerance, vc.x, vd.x, c, d)
        v2.y = vc.y
        vertices.append_LowLevel(v1)
        vertices.append_LowLevel(v2)
        return Mesh(vertices, edges, polygons)
    elif index == 11:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = lerp(tolerance, va.x, vb.x, a, b)
        v1.y = va.y
        v2.x = vc.x
        v2.y = lerp(tolerance, vc.y, vb.y, c, b)
        vertices.data[0] = v1
        vertices.data[1] = v2
        return Mesh(vertices, edges, polygons)
    elif index == 12:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = va.x
        v1.y = lerp(tolerance, va.y, vd.y, a, d)
        v2.x = vb.x
        v2.y = lerp(tolerance, vb.y, vc.y, b, c)
        vertices.data[0] = v1
        vertices.data[1] = v2
        return Mesh(vertices, edges, polygons)
    elif index == 13:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = vb.x
        v1.y = lerp(tolerance, vb.y, vc.y, b, c)
        v2.x = lerp(tolerance, vd.x, vc.x, d, c)
        v2.y = vd.y
        vertices.data[0] = v1
        vertices.data[1] = v2
        return Mesh(vertices, edges, polygons)
    elif index == 14:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1

        v1.x = va.x
        v1.y = lerp(tolerance, va.y, vd.y, a, d)
        v2.x = lerp(tolerance, vc.x, vd.x, c, d)
        v2.y = vc.y
        vertices.data[0] = v1
        vertices.data[1] = v2
        return Mesh(vertices, edges, polygons)
    elif index == 15:
        return Mesh()

cdef long binaryToDecimal(float t, float a, float b, float c, float d):
    # binary order (d, c, b, a)
    if a <= t: a = 0
    else: a = 1

    if b <= t: b = 0
    else: b = 1

    if c <= t: c = 0
    else: c = 1

    if d <= t: d = 0
    else: d = 1

    return <long>(8.0 * a + 4.0 * b + 2.0 * c + d)

cdef float lerp(float tolerance, float t1, float t2, float f1, float f2):
    return t1 + (tolerance - f1) * (t2 - t1) / (f2 - f1)

cdef getGridPoints(long xDivisions, long yDivisions, long zDivisions, float size1,
                   float size2, float size3, distanceMode = "SIZE"):
    cdef:
        int xDiv = limitAmount(xDivisions)
        int yDiv = limitAmount(yDivisions)
        int zDiv = limitAmount(zDivisions)
        double xOffset, yOffset, zOffset
        double xDis, yDis, zDis
        long x, y, z, index
        Vector3 vector
        Vector3DList points = Vector3DList(length = xDiv * yDiv * zDiv)

    if distanceMode == "STEP":
        xDis, yDis, zDis = size1, size2, size3
    elif distanceMode == "SIZE":
        xDis = size1 / max(xDiv - 1, 1)
        yDis = size2 / max(yDiv - 1, 1)
        zDis = size3 / max(zDiv - 1, 1)

    xOffset = xDis * (xDiv - 1) / 2 * int(1)
    yOffset = yDis * (yDiv - 1) / 2 * int(1)
    zOffset = zDis * (zDiv - 1) / 2 * int(0)

    for x in range(xDiv):
        for y in range(yDiv):
            for z in range(zDiv):
                index = z * xDiv * yDiv + y * xDiv + x
                vector.x = <float>(x * xDis - xOffset)
                vector.y = <float>(y * yDis - yOffset)
                vector.z = <float>(z * zDis - zOffset)
                points.data[index] = vector

    return points, xDis, yDis

cdef int limitAmount(n):
    return max(min(n, INT_MAX), 0)
