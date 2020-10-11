import bpy
from bpy.props import *
from ... utils.limits cimport INT_MAX
from ... base_types import AnimationNode
from ... math cimport Vector3
from ... data_structures cimport (
    Mesh, Vector3DList, EdgeIndicesList,
    PolygonIndicesList, Falloff, FalloffEvaluator,
    FloatList,
)

class MarchingSquaresNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MarchingSquaresNode"
    bl_label = "Marching Squares"
    errorHandlingType = "EXCEPTION"

    __annotations__ = {}

    __annotations__["clampFalloff"] = BoolProperty(name = "Clamp Falloff", default = False)

    def create(self):
        self.newInput("Integer", "X Divisions", "xDivisions", value = 3, minValue = 2)
        self.newInput("Integer", "Y Divisions", "yDivisions", value = 3, minValue = 2)
        self.newInput("Float", "Size", "size", value = 5)
        self.newInput("Integer", "Cell Index", "index")
        self.newInput("Falloff", "Falloff", "falloff")

        self.newOutput("Mesh", "Mesh", "mesh")

    def execute(self, xDivisions, yDivisions, size, index, falloff):
        cdef double xDis, yDis
        cdef Vector3DList points
        points, xDis, yDis = getGridPoints(xDivisions, yDivisions, 1, size, size, size)

        cdef FloatList strengths = self.getFieldStrengths(points, falloff)
        cdef long nx, ny, amountCell
        nx, ny = limitAmount(xDivisions), limitAmount(yDivisions)

        cdef Py_ssize_t i, j, offset, ia, ib, ic, id
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

                meshes.append(getMesh(points, strengths, _xDis, _yDis, ia, ib, ic, id))

        return Mesh.join(*meshes)

    def getFieldStrengths(self, Vector3DList vectors, falloff):
        cdef FalloffEvaluator falloffEvaluator = self.getFalloffEvaluator(falloff)
        cdef FloatList influences = falloffEvaluator.evaluateList(vectors)
        return influences

    def getFalloffEvaluator(self, falloff):
        try: return falloff.getEvaluator("LOCATION", self.clampFalloff)
        except: self.raiseErrorMessage("This falloff cannot be evaluated for vectors")

def getMesh(Vector3DList points, FloatList strengths, double _xDis, double _yDis,
            Py_ssize_t ia, Py_ssize_t ib, Py_ssize_t ic, Py_ssize_t id):
    cdef int index = binaryToDecimal(strengths.data[ia], strengths.data[ib],
                                     strengths.data[ic], strengths.data[id])

    cdef Vector3DList vertices = Vector3DList(length = 2)
    cdef EdgeIndicesList edges = EdgeIndicesList(length = 1)
    cdef PolygonIndicesList polygons = PolygonIndicesList()

    if index == 0:
        return Mesh()
    elif index == 1:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1
        vertices.data[0] = points.data[id]
        vertices.data[1] = points.data[id]
        vertices.data[0].x += _xDis
        vertices.data[1].y += _yDis
        return Mesh(vertices, edges, polygons)
    elif index == 2:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1
        vertices.data[0] = points.data[ib]
        vertices.data[1] = points.data[ic]
        vertices.data[0].y -= _yDis
        vertices.data[1].x -= _xDis
        return Mesh(vertices, edges, polygons)
    elif index == 3:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1
        vertices.data[0] = points.data[ib]
        vertices.data[1] = points.data[id]
        vertices.data[0].y -= _yDis
        vertices.data[1].y += _yDis
        return Mesh(vertices, edges, polygons)
    elif index == 4:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1
        vertices.data[0] = points.data[ia]
        vertices.data[1] = points.data[ib]
        vertices.data[0].x += _xDis
        vertices.data[1].y -= _yDis
        return Mesh(vertices, edges, polygons)
    elif index == 5:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1
        vertices.data[0] = points.data[ib]
        vertices.data[1] = points.data[ic]
        vertices.data[0].y -= _yDis
        vertices.data[1].x -= _xDis

        edges.append((2,3))
        vertices.append_LowLevel(points.data[id])
        vertices.append_LowLevel(points.data[ia])
        vertices.data[2].y += _yDis
        vertices.data[3].x += _xDis
        return Mesh(vertices, edges, polygons)
    elif index == 6:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1
        vertices.data[0] = points.data[ib]
        vertices.data[1] = points.data[ic]
        vertices.data[0].x -= _xDis
        vertices.data[1].x -= _xDis
        return Mesh(vertices, edges, polygons)
    elif index == 7:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1
        vertices.data[0] = points.data[ia]
        vertices.data[1] = points.data[id]
        vertices.data[0].x += _xDis
        vertices.data[1].y += _yDis
        return Mesh(vertices, edges, polygons)
    elif index == 8:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1
        vertices.data[0] = points.data[ia]
        vertices.data[1] = points.data[id]
        vertices.data[0].x += _xDis
        vertices.data[1].y += _yDis
        return Mesh(vertices, edges, polygons)
    elif index == 9:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1
        vertices.data[0] = points.data[ia]
        vertices.data[1] = points.data[id]
        vertices.data[0].x += _xDis
        vertices.data[1].x += _xDis
        return Mesh(vertices, edges, polygons)
    elif index == 10:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1
        vertices.data[0] = points.data[ia]
        vertices.data[1] = points.data[ib]
        vertices.data[0].x += _xDis
        vertices.data[1].y -= _yDis

        edges.append((2,3))
        vertices.append_LowLevel(points.data[ic])
        vertices.append_LowLevel(points.data[id])
        vertices.data[2].x -= _xDis
        vertices.data[3].y += _yDis
        return Mesh(vertices, edges, polygons)
    elif index == 11:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1
        vertices.data[0] = points.data[ia]
        vertices.data[1] = points.data[ib]
        vertices.data[0].x += _xDis
        vertices.data[1].y -= _yDis
        return Mesh(vertices, edges, polygons)
    elif index == 12:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1
        vertices.data[0] = points.data[ia]
        vertices.data[1] = points.data[ib]
        vertices.data[0].y -= _yDis
        vertices.data[1].y -= _yDis
        return Mesh(vertices, edges, polygons)
    elif index == 13:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1
        vertices.data[0] = points.data[ib]
        vertices.data[1] = points.data[ic]
        vertices.data[0].y -= _yDis
        vertices.data[1].x -= _xDis
        return Mesh(vertices, edges, polygons)
    elif index == 14:
        edges.data[0].v1 = 0
        edges.data[0].v2 = 1
        vertices.data[0] = points.data[ic]
        vertices.data[1] = points.data[id]
        vertices.data[0].x -= _xDis
        vertices.data[1].y += _yDis
        return Mesh(vertices, edges, polygons)
    elif index == 15:
        return Mesh()

cdef int binaryToDecimal(float a, float b, float c, float d):
    # binary order (d, c, b, a)
    if a <= 0.25: a = 0
    else: a = 1

    if b <= 0.25: b = 0
    else: b = 1

    if c <= 0.25: c = 0
    else: c = 1

    if d <= 0.25: d = 0
    else: d = 1

    return <int>(8 * a + 4 * b + 2 * c + d)

cdef getGridPoints(long xDivisions, long yDivisions, long zDivisions, float size1,
                   float size2, float size3, distanceMode = "SIZE"):
    cdef:
        int xDiv = limitAmount(xDivisions)
        int yDiv = limitAmount(yDivisions)
        int zDiv = limitAmount(zDivisions)
        double xDis, yDis, zDis
        double xOffset, yOffset
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
