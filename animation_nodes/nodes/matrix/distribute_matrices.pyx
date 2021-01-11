import bpy
from bpy.props import *
from math import pi as _pi
from libc.math cimport sin, cos
from ... utils.limits cimport INT_MAX
from ... events import propertyChanged
from ... base_types import AnimationNode
from ... data_structures cimport Mesh, Matrix4x4List, Vector3DList, Spline, Interpolation
from ... algorithms.rotations.rotation_and_direction cimport directionToMatrix_LowLevel
from ... math cimport (Matrix4, Vector3, setTranslationMatrix,
    setMatrixTranslation, setRotationZMatrix, toVector3, scaleMatrix3x3Part)
cdef double PI = _pi # cimporting pi does not work for some reason...

modeItems = [
    ("LINEAR", "Linear", "", "NONE", 0),
    ("GRID", "Grid", "", "NONE", 1),
    ("CIRCLE", "Circle", "", "NONE", 2),
    ("MESH", "Mesh", "", "NONE", 3),
    ("SPIRAL", "Spiral", "", "NONE", 4),
    ("SPLINE", "Spline", "", "NONE", 5),
]

distanceModeItems = [
    ("STEP", "Step", "Define the distance between two points", "NONE", 0),
    ("SIZE", "Size", "Define how large the grid will be in total", "NONE", 1)
]

meshModeItems = [
    ("VERTICES", "Vertices", "","NONE", 0),
    ("POLYGONS", "Polygons", "", "NONE", 1)
]

splineDistributionMethodItems = (
    ("UNIFORM", "Uniform", "", "NONE", 0),
    ("STEP", "Step", "", "NONE", 1),
    ("RESOLUTION", "Resolution", "","NONE", 2),
    ("VERTICES", "Vertices", "", "NONE", 3),
)

searchItems = {
    "Distribute Linear" : "LINEAR",
    "Distribute Grid" : "GRID",
    "Distribute Circle" : "CIRCLE",
    "Distribute MESH" : "MESH",
    "Distribute Spiral" : "SPIRAL",
    "Distribute Spline" : "SPLINE",
}

directionAxisItems = [(axis, axis, "") for axis in ("X", "Y", "Z")]

class DistributeMatricesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DistributeMatricesNode"
    bl_label = "Distribute Matrices"
    searchTags = [(name, {"mode" : repr(op)}) for name, op in searchItems.items()]

    __annotations__ = {}

    __annotations__["mode"] = EnumProperty(name = "Mode", default = "GRID",
        items = modeItems, update = AnimationNode.refresh)

    __annotations__["distanceMode"] = EnumProperty(name = "Distance Mode", default = "SIZE",
        items = distanceModeItems, update = AnimationNode.refresh)

    __annotations__["meshMode"] = EnumProperty(name = "Mesh Mode", default = "VERTICES",
        items = meshModeItems, update = AnimationNode.refresh)

    __annotations__["splineDistributionMethod"] = EnumProperty(name = "Distribution Method",
        default = "UNIFORM", items = splineDistributionMethodItems, update = AnimationNode.refresh)

    __annotations__["centerAlongX"] = BoolProperty(name = "Center Along X", default = True,
        description = "Center the grid along the x axis", update = propertyChanged)
    __annotations__["centerAlongY"] = BoolProperty(name = "Center Along Y", default = True,
        description = "Center the grid along the y axis", update = propertyChanged)
    __annotations__["centerAlongZ"] = BoolProperty(name = "Center Along Z", default = False,
        description = "Center the grid along the z axis", update = propertyChanged)

    __annotations__["exactCircleSegment"] = BoolProperty(name = "Exact Circle Segment", default = False,
        update = propertyChanged)

    __annotations__["splineResolution"] = IntProperty(name = "Spline Resolution", min = 2, default = 20,
        description = "Increase to have a more accurate evaluation if the type is set to Uniform",
        update = propertyChanged)
    
    __annotations__["centerSpiral"] =  BoolProperty(name = "Center Spiral",
        description = "Center the spiral along Z axis",
        default = False, update = propertyChanged)
    
    __annotations__["centerLinear"] =  BoolProperty(name = "Center Linear",
        description = "Center the linear along the axis",
        default = False, update = propertyChanged)

    __annotations__["directionAxis"] = EnumProperty(items = directionAxisItems, update = propertyChanged, default = "X")

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
            self.newInput("Float", "Height", "spiralHeight", value = 0)
            self.newInput("Interpolation", "Radius Interpolation", "radiusInterpolation", defaultDrawType = "PROPERTY_ONLY", hide = True)
            self.newInput("Interpolation", "Height Interpolation", "heightInterpolation", defaultDrawType = "PROPERTY_ONLY", hide = True)
        elif self.mode == "SPLINE":
            self.newInput("Spline", "Spline", "spline", defaultDrawType = "PROPERTY_ONLY")
            if self.splineDistributionMethod == "STEP":
                self.newInput("Float", "Step", "step", value = 0.1, minValue = 0)
            elif self.splineDistributionMethod in ("RESOLUTION", "UNIFORM"):
                self.newInput("Integer", "Count", "count", value = 50, minValue = 0)
            if self.splineDistributionMethod != "VERTICES":
                self.newInput("Float", "Start", "start", value = 0.0).setRange(0.0, 1.0)
                self.newInput("Float", "End", "end", value = 1.0).setRange(0.0, 1.0)

        self.newOutput("Matrix List", "Matrices", "matrices")
        self.newOutput("Vector List", "Vectors", "vectors")

    def draw(self, layout):
        col = layout.column()
        col.prop(self, "mode", text = "")
        if self.mode in ("LINEAR", "GRID"):
            col.prop(self, "distanceMode", text = "")
        if self.mode == "LINEAR":
            layout.prop(self, "directionAxis", expand = True)
            layout.prop(self, "centerLinear", toggle = True)
        if self.mode == "MESH":
            col.prop(self, "meshMode", text = "")
        if self.mode == "GRID":
            row = col.row(align = True)
            row.prop(self, "centerAlongX", text = "X", toggle = True)
            row.prop(self, "centerAlongY", text = "Y", toggle = True)
            row.prop(self, "centerAlongZ", text = "Z", toggle = True)
        if self.mode == "SPLINE":
            col.prop(self, "splineDistributionMethod", text = "")
        if self.mode == "SPIRAL":
            layout.prop(self, "centerSpiral", toggle = True)

    def drawAdvanced(self, layout):
        if self.mode == "CIRCLE":
            layout.prop(self, "exactCircleSegment")
        if self.mode == "SPLINE":
            if self.splineDistributionMethod in ("UNIFORM", "STEP"):
                layout.prop(self, "splineResolution")

    def getExecutionCode(self, required):
        if self.mode == "LINEAR":
            if self.distanceMode == "STEP":
                yield "matrices = self.execute_Linear(amount, distance)"
            else:
                yield "matrices = self.execute_Linear(amount, size)"
        elif self.mode == "GRID":
            if self.distanceMode == "STEP":
                yield "matrices = self.execute_Grid(xDivisions, yDivisions, zDivisions, xDistance, yDistance, zDistance)"
            else:
                yield "matrices = self.execute_Grid(xDivisions, yDivisions, zDivisions, width, length, height)"
        elif self.mode == "CIRCLE":
            yield "matrices = self.execute_Circle(amount, radius, segment)"
        elif self.mode == "MESH":
            if self.meshMode == "VERTICES":
                yield "matrices = self.execute_Vertices(mesh)"
            elif self.meshMode == "POLYGONS":
                yield "matrices = self.execute_Polygons(mesh)"
        elif self.mode == "SPIRAL":
            yield "matrices = self.execute_Spiral(amount, startRadius, endRadius, startSize, endSize, startAngle, endAngel,\
                                                  spiralHeight, radiusInterpolation, heightInterpolation)"
        elif self.mode == "SPLINE":
            if self.splineDistributionMethod == "STEP":
                yield "matrices = self.execute_SplineStep(spline, step, start, end)"
            elif self.splineDistributionMethod in ("RESOLUTION", "UNIFORM"):
                yield "matrices = self.execute_SplineCount(spline, count, start, end)"
            else:
                yield "matrices = self.execute_SplineVertices(spline)"

        if "vectors" in required:
            yield "vectors = AN.nodes.matrix.c_utils.extractMatrixTranslations(matrices)"

    def execute_Linear(self, amount, size):
        if self.directionAxis == "X":
            self.centerAlongX = self.centerLinear
            return self.execute_Grid(amount, 1, 1, size, 0, 0)
        elif self.directionAxis == "Y":
            self.centerAlongY = self.centerLinear
            return self.execute_Grid(1, amount, 1, 0, size, 0)
        else:
            self.centerAlongZ = self.centerLinear
            return self.execute_Grid(1, 1, amount, 0, 0, size)

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

        xOffset = xDis * (xDiv - 1) / 2 * int(self.centerAlongX)
        yOffset = yDis * (yDiv - 1) / 2 * int(self.centerAlongY)
        zOffset = zDis * (zDiv - 1) / 2 * int(self.centerAlongZ)

        for x in range(xDiv):
            for y in range(yDiv):
                for z in range(zDiv):
                    index = z * xDiv * yDiv + y * xDiv + x
                    vector.x = <float>(x * xDis - xOffset)
                    vector.y = <float>(y * yDis - yOffset)
                    vector.z = <float>(z * zDis - zOffset)
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

    def execute_Spiral(self, Py_ssize_t _amount, float startRadius, float endRadius,
                             float startSize, float endSize, float startAngle, float endAngle,
                             float spiralHeight, Interpolation radiusInterpolation, Interpolation heightInterpolation):
        cdef Py_ssize_t i
        cdef Vector3 position
        cdef float iCos, iSin, stepCos, stepSin, f, size
        cdef int amount = limitAmount(_amount)
        cdef Matrix4x4List matrices = Matrix4x4List(length = amount)
        cdef float factor = 1 / <float>(amount - 1) if amount > 1 else 0
        cdef float angleStep = (endAngle - startAngle) / (amount - 1) if amount > 1 else 0

        iCos = cos(startAngle)
        iSin = sin(startAngle)
        stepCos = cos(angleStep)
        stepSin = sin(angleStep)
        
        zOffset = (spiralHeight / 2) * self.centerSpiral
        
        for i in range(amount):
            f = <float>i * factor

            size = f * (endSize - startSize) + startSize
            radius = (endRadius - startRadius) * radiusInterpolation.evaluate(f) + startRadius

            position.x = iCos * radius
            position.y = iSin * radius
            position.z = spiralHeight * heightInterpolation.evaluate(f) - zOffset

            setTranslationMatrix(matrices.data + i, &position)
            setMatrixCustomZRotation(matrices.data + i, iCos, iSin)
            scaleMatrix3x3Part(matrices.data + i, size)

            rotateStep(&iCos, &iSin, stepCos, stepSin)

        return matrices

    def execute_SplineStep(self, Spline spline, float step, float start, float end):
        if not spline.isEvaluable(): return Matrix4x4List()
        spline.ensureUniformConverter(self.splineResolution)
        cdef float uniformStart = spline.toUniformParameter(min(max(start, 0), 1))
        cdef float uniformEnd = spline.toUniformParameter(min(max(end, 0), 1))
        cdef float length = spline.getPartialLength(uniformStart, uniformEnd, self.splineResolution)
        cdef Py_ssize_t count = <Py_ssize_t>(length / step) if step > 0 else 0
        return self.execute_SplineCount(spline, count, start, end)

    def execute_SplineCount(self, Spline spline, Py_ssize_t count, float start, float end):
        if not spline.isEvaluable(): return Matrix4x4List()
        if self.splineDistributionMethod == "UNIFORM":
            spline.ensureUniformConverter(self.splineResolution)
        start = min(max(start, 0), 1)
        end = min(max(end, 0), 1)
        spline.ensureNormals()
        count = max(count, 0)
        distributionType = "UNIFORM" if self.splineDistributionMethod != "RESOLUTION" else "RESOLUTION"
        return spline.getDistributedMatrices(count, start, end, distributionType)

    def execute_SplineVertices(self, Spline spline):
        if not spline.isEvaluable(): return Matrix4x4List()
        spline.ensureNormals()
        count = len(spline.points)
        return spline.getDistributedMatrices(count, 0, 1, "RESOLUTION")

cdef int limitAmount(n):
    return max(min(n, INT_MAX), 0)

cdef inline void setMatrixCustomZRotation(Matrix4* m, double iCos, double iSin):
    m.a11 = m.a22 = iCos
    m.a12, m.a21 = -iSin, iSin

cdef inline void rotateStep(float *iCos, float *iSin, float stepCos, float stepSin):
    cdef float newCos = stepCos * iCos[0] - stepSin * iSin[0]
    iSin[0] = stepSin * iCos[0] + stepCos * iSin[0]
    iCos[0] = newCos
