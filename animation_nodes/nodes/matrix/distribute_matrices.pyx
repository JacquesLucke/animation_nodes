import bpy
from bpy.props import *
from math import pi as _pi
from libc.math cimport sin, cos
from ... utils.limits cimport INT_MAX
from ... base_types import AnimationNode
from ... data_structures cimport Mesh, Matrix4x4List, Vector3DList
from ... algorithms.rotations.rotation_and_direction cimport directionToMatrix_LowLevel
from ... math cimport (Matrix4, Vector3, setTranslationMatrix,
    setMatrixTranslation, setRotationZMatrix, toVector3, scaleMatrix3x3Part)
cdef double PI = _pi # cimporting pi does not work for some reason...

modeItems = [
    ("LINEAR", "Linear", "", "NONE", 0),
    ("GRID", "Grid", "", "NONE", 1),
    ("CIRCLE", "Circle", "", "NONE", 2),
    ("MESH", "Mesh", "", "NONE", 3),
    ("SPIRAL", "Spiral", "", "NONE", 4)
]

distanceModeItems = [
    ("STEP", "Step", "Define the distance between two points", "NONE", 0),
    ("SIZE", "Size", "Define how large the grid will be in total", "NONE", 1)
]

meshModeItems = [
    ("VERTICES", "Vertices", "","NONE", 0),
    ("POLYGONS", "Polygons", "", "NONE", 1)
]


class DistributeMatricesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DistributeMatricesNode"
    bl_label = "Distribute Matrices"
    bl_width_default = 160

    __annotations__ = {}

    __annotations__["mode"] = EnumProperty(name = "Mode", default = "GRID",
        items = modeItems, update = AnimationNode.refresh)

    __annotations__["distanceMode"] = EnumProperty(name = "Distance Mode", default = "SIZE",
        items = distanceModeItems, update = AnimationNode.refresh)

    __annotations__["meshMode"] = EnumProperty(name = "Mesh Mode", default = "VERTICES",
        items = meshModeItems, update = AnimationNode.refresh)

    __annotations__["exactCircleSegment"] = BoolProperty(name = "Exact Circle Segment", default = False)

    def create(self):
        if self.mode == "LINEAR":
            self.newInput("Integer", "Amount", "amount", value = 5)
            if self.distanceMode == "STEP":
                self.newInput("Float", "Distance", "distance", value = 1)
            elif self.distanceMode == "SIZE":
                self.newInput("Float", "Size", "size", value = 4)
        elif self.mode == "GRID":
            self.newInput("Integer", "X Divisions", "xDivisions", value = 3, minValue = 0)
            self.newInput("Integer", "Y Divisions", "yDivisions", value = 3, minValue = 0)
            self.newInput("Integer", "Z Divisions", "zDivisions", value = 1, minValue = 0)
            if self.distanceMode == "STEP":
                self.newInput("Float", "X Distance", "xDistance", value = 1)
                self.newInput("Float", "Y Distance", "yDistance", value = 1)
                self.newInput("Float", "Z Distance", "zDistance", value = 1)
            elif self.distanceMode == "SIZE":
                self.newInput("Float", "Width", "width", value = 5)
                self.newInput("Float", "Length", "length", value = 5)
                self.newInput("Float", "Height", "height", value = 5)
        elif self.mode == "CIRCLE":
            self.newInput("Integer", "Amount", "amount", value = 10, minValue = 0)
            self.newInput("Float", "Radius", "radius", value = 4)
            self.newInput("Float", "Segment", "segment", value = 1)
        elif self.mode == "MESH":
            self.newInput("Mesh", "Mesh", "mesh")
        elif self.mode == "SPIRAL":
            self.newInput("Integer", "Amount", "amount", value = 100, minValue = 0)
            self.newInput("Float", "Start Radius", "startRadius", value = 0, minValue = 0)
            self.newInput("Float", "End Radius", "endRadius", value = 2 * PI, minValue = 0)
            self.newInput("Float", "Start Size", "startSize", value = 0.1, minValue = 0)
            self.newInput("Float", "End Size", "endSize", value = 0.5, minValue = 0)
            self.newInput("Float", "Start Angle", "startAngle", value = 0)
            self.newInput("Float", "End Angle", "endAngel", value = 6 * PI)

        self.newOutput("Matrix List", "Matrices", "matrices")

    def draw(self, layout):
        col = layout.column()
        col.prop(self, "mode", text = "")
        if self.mode in ("LINEAR", "GRID"):
            col.prop(self, "distanceMode", text = "")
        if self.mode == "MESH":
            col.prop(self, "meshMode", text = "")

    def drawAdvanced(self, layout):
        if self.mode == "CIRCLE":
            layout.prop(self, "exactCircleSegment")

    def getExecutionFunctionName(self):
        if self.mode == "LINEAR":
            return "execute_Linear"
        elif self.mode == "GRID":
            return "execute_Grid"
        elif self.mode == "CIRCLE":
            return "execute_Circle"
        elif self.mode == "MESH":
            if self.meshMode == "VERTICES":
                return "execute_Vertices"
            elif self.meshMode == "POLYGONS":
                return "execute_Polygons"
        elif self.mode == "SPIRAL":
            return "execute_Spiral"

    def execute_Linear(self, amount, size):
        return self.execute_Grid(amount, 1, 1, size, 0, 0)

    def execute_Grid(self, xDivisions, yDivisions, zDivisions, size1, size2, size3):
        cdef:
            int xDiv = limitAmount(xDivisions)
            int yDiv = limitAmount(yDivisions)
            int zDiv = limitAmount(zDivisions)
            double xDis, yDis, zDis
            double xOffset, yOffset
            long x, y, z, index
            Vector3 vector
            Matrix4x4List matrices = Matrix4x4List(length = xDiv * yDiv * zDiv)

        if self.distanceMode == "STEP":
            xDis, yDis, zDis = size1, size2, size3
        elif self.distanceMode == "SIZE":
            xDis = size1 / max(xDiv - 1, 1)
            yDis = size2 / max(yDiv - 1, 1)
            zDis = size3 / max(zDiv - 1, 1)

        xOffset = xDis * (xDiv - 1) / 2
        yOffset = yDis * (yDiv - 1) / 2

        for x in range(xDiv):
            for y in range(yDiv):
                for z in range(zDiv):
                    index = x * yDiv * zDiv + y * zDiv + z
                    vector.x = <float>(x * xDis - xOffset)
                    vector.y = <float>(y * yDis - yOffset)
                    vector.z = <float>(z * zDis)
                    setTranslationMatrix(matrices.data + index, &vector)

        return matrices

    def execute_Circle(self, _amount, float radius, float segment):
        cdef:
            int i
            Vector3 vector
            int amount = limitAmount(_amount)
            float angleStep, iCos, iSin, stepCos, stepSin
            Matrix4x4List matrices = Matrix4x4List(length = amount)

        if self.exactCircleSegment: angleStep = segment * 2 * PI / max(amount - 1, 1)
        else:                       angleStep = segment * 2 * PI / max(amount, 1)

        iCos = 1
        iSin = 0
        stepCos = cos(angleStep)
        stepSin = sin(angleStep)

        for i in range(amount):
            vector.x = iCos * radius
            vector.y = iSin * radius
            vector.z = 0
            setTranslationMatrix(matrices.data + i, &vector)
            setMatrixCustomZRotation(matrices.data + i, iCos, iSin)

            rotateStep(&iCos, &iSin, stepCos, stepSin)

        return matrices

    def execute_Vertices(self, Mesh mesh):
        return self.matricesFromPointsAndNormals(mesh.vertices, mesh.getVertexNormals())

    def execute_Polygons(self, Mesh mesh):
        return self.matricesFromPointsAndNormals(mesh.getPolygonCenters(), mesh.getPolygonNormals())

    def matricesFromPointsAndNormals(self, Vector3DList points, Vector3DList normals):
        assert len(points) == len(normals)
        cdef:
            Py_ssize_t i
            Vector3 *normal
            Vector3 *position
            Vector3 guide = toVector3((0, 0, 1))
            Matrix4x4List matrices = Matrix4x4List(length = len(points))

        for i in range(len(matrices)):
            directionToMatrix_LowLevel(matrices.data + i, normals.data + i, &guide, 2, 0)
            setMatrixTranslation(matrices.data + i, points.data + i)

        return matrices

    def execute_Spiral(self, Py_ssize_t amount, float startRadius, float endRadius,
                             float startSize, float endSize, float startAngle, float endAngle):
        cdef Py_ssize_t i
        cdef Vector3 position
        cdef float iCos, iSin, stepCos, stepSin, f, size
        cdef Matrix4x4List matrices = Matrix4x4List(length = amount)
        cdef float factor = 1 / <float>(amount - 1) if amount > 1 else 0
        cdef float angleStep = (endAngle - startAngle) / (amount - 1)

        iCos = cos(startAngle)
        iSin = sin(startAngle)
        stepCos = cos(angleStep)
        stepSin = sin(angleStep)

        for i in range(amount):
            f = <float>i * factor

            size = f * (endSize - startSize) + startSize
            radius = f * (endRadius - startRadius) + startRadius

            position.x = iCos * radius
            position.y = iSin * radius
            position.z = 0

            setTranslationMatrix(matrices.data + i, &position)
            setMatrixCustomZRotation(matrices.data + i, iCos, iSin)
            scaleMatrix3x3Part(matrices.data + i, size)

            rotateStep(&iCos, &iSin, stepCos, stepSin)

        return matrices

cdef int limitAmount(n):
    return max(min(n, INT_MAX), 0)

cdef inline void setMatrixCustomZRotation(Matrix4* m, double iCos, double iSin):
    m.a11 = m.a22 = iCos
    m.a12, m.a21 = -iSin, iSin

cdef inline void rotateStep(float *iCos, float *iSin, float stepCos, float stepSin):
    cdef float newCos = stepCos * iCos[0] - stepSin * iSin[0]
    iSin[0] = stepSin * iCos[0] + stepCos * iSin[0]
    iCos[0] = newCos
