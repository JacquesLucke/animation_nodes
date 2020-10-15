import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket
from ... algorithms.mesh.close_packing import(
    neighbourRadiusSpherePacking,
    dynamicRadiusSpherePacking,
    fixedRadiusSpherePacking,
    spherePackingOnMesh,
    relaxSpherePacking,
    relaxSpherePackingOnMesh,
)
from ... data_structures cimport(
    Mesh,
    Falloff,
    FloatList,
    DoubleList,
    Vector3DList,
    Matrix4x4List,
    FalloffEvaluator,
    VirtualFloatList,
    VirtualDoubleList,
    PolygonIndicesList,
)

modeItems = [
    ("POINTS", "Sphere Packing using Points", "Sphere packing using points", "NONE", 0),
    ("RELAX", "Sphere Packing using Relaxation", "Sphere packing using relaxation of points", "NONE", 1),
    ("POLYGONS", "Sphere Packing using Polygons", "Sphere packing using mesh polygons", "NONE", 2),
]

methodTypeForPointsItems = [
    ("DYNAMICRADIUS", "Dynamic Radius", "Sphere packing for points with dynamic radius", "NONE", 0),
    ("NEIGHBOURRADIUS", "Neighbour Radius", "Sphere packing for points with neighbour radius", "NONE", 1),
    ("FIXEDRADIUS", "Fixed Radius", "Sphere packing for points with fixed radius", "NONE", 2),
]

class ClosePackingNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ClosePackingNode"
    bl_label = "Close Packing"
    errorHandlingType = "EXCEPTION"

    __annotations__ = {}

    __annotations__["mode"] = EnumProperty(name = "Mode", default = "POINTS",
        items = modeItems, update = AnimationNode.refresh)

    __annotations__["methodTypeForPoints"] = EnumProperty(name = "Method Type", default = "DYNAMICRADIUS",
        items = methodTypeForPointsItems, update = AnimationNode.refresh)

    __annotations__["onlyCompareNewPoints"] = BoolProperty(name = "Only compare new Points", default = False,
        description = "Only compare newly formed points for filtering", update = AnimationNode.refresh)

    __annotations__["pointsOnMesh"] = BoolProperty(name = "Points on Mesh", default = False,
        description = "Keep relaxed points on mesh surface", update = AnimationNode.refresh)

    __annotations__["neighbourAmount"] = IntProperty(name = "Neighbour Amount", min = 1, max = 10,
        default = 1, update = propertyChanged)

    __annotations__["useRadiusList"] = VectorizedSocket.newProperty()
    __annotations__["useObjectRadiusList"] = VectorizedSocket.newProperty()

    def create(self):
        if self.mode == "POINTS":
            self.newInput("Vector List", "Points", "points", dataIsModified = True)
            self.newInput("Float", "Margin", "margin", value = 0.0, minValue = 0, hide = True)
            if self.methodTypeForPoints == "FIXEDRADIUS":
                self.newInput(VectorizedSocket("Float", "useRadiusList",
                             ("Radius", "Radius", dict(value = 1.0, minValue = 0)), ("Radii", "Radius")))
            else:
                self.newInput("Float", "Radius Max", "radiusMax", value = 1.0, minValue = 0)
            if self.methodTypeForPoints in ["DYNAMICRADIUS", "NEIGHBOURRADIUS"]:
                self.newInput("Float", "Radius Step", "radiusStep", value = 0.01, minValue = 0.00001)
            self.newInput("Falloff", "Falloff", "falloff")
            self.newInput("Boolean", "Mask", "mask", value = False, hide = True)
            self.newInput(VectorizedSocket("Float", "useObjectRadiusList",
                         ("Object Radius", "objectRadii", dict(value = 1.0, minValue = 0)),
                         ("Object Radii", "objectRadii")), hide = True)
        elif self.mode == "RELAX":
            self.newInput("Vector List", "Points", "points", dataIsModified = True)
            if self.pointsOnMesh:
                self.newInput("Mesh", "Mesh", "mesh")
            self.newInput("Float", "Margin", "margin", value = 0.0, minValue = 0, hide = True)
            self.newInput(VectorizedSocket("Float", "useRadiusList",
                         ("Radius", "radii", dict(value = 1.0, minValue = 0)), ("Radii", "radii")))
            self.newInput("Float", "Force Magnitude", "forceMagnitude", value = 0.25, minValue = 0, maxValue = 1)
            self.newInput("Float", "Error Max(%)", "errorMax", value = 1, minValue = 0.001, maxValue = 100, hide = True)
            self.newInput("Integer", "Iterations Max", "iterations", value = 200, minValue = 0, hide = True)
            self.newInput("Falloff", "Falloff", "falloff")
            self.newInput("Boolean", "Mask", "mask", value = False, hide = True)
            if self.pointsOnMesh:
                self.newInput("Boolean", "Align To Normal", "alignToNormal", value = False)
            self.newInput(VectorizedSocket("Float", "useObjectRadiusList",
                         ("Object Radius", "objectRadii", dict(value = 1.0, minValue = 0)),
                         ("Object Radii", "objectRadii")), hide = True)
            if self.pointsOnMesh:
                self.newInput("Float", "Epsilon", "epsilon", value = 0, hide = True)
                self.newInput("Float", "Max Distance", "maxDistance", value = 1e6, hide = True)

        elif self.mode == "POLYGONS":
            self.newInput("Mesh", "Mesh", "mesh", dataIsModified = True)
            self.newInput("Falloff", "Falloff", "falloff")
            self.newInput("Boolean", "Align To Normal", "alignToNormal", value = False)
            self.newInput(VectorizedSocket("Float", "useObjectRadiusList",
                         ("Object Radius", "objectRadii", dict(value = 1.0, minValue = 0)),
                         ("Object Radii", "objectRadii")), hide = True)

        self.newOutput("Matrix List", "Matrices", "matrices")
        self.newOutput("Vector List", "Vectors", "vectors")
        self.newOutput("Float List", "Radii", "radii", hide = True)
        if self.mode == "RELAX" and self.pointsOnMesh:
            self.newOutput("Vector List", "Normals", "normals", hide = True)

    def draw(self, layout):
        col = layout.column(align = True)
        col.prop(self, "mode", text = "")
        if self.mode == "POINTS":
            col.prop(self, "methodTypeForPoints", text = "")
            if self.methodTypeForPoints == "FIXEDRADIUS":
                col.prop(self, "onlyCompareNewPoints")
        if self.mode == "RELAX":
            col.prop(self, "pointsOnMesh")

    def drawAdvanced(self, layout):
        if self.mode == "RELAX":
            col = layout.column()
            col.prop(self, "neighbourAmount")
        box = layout.box()
        col = box.column(align = True)
        col.label(text = "Info", icon = "INFO")
        col.label(text = "Object Radius: It is a reference radius that allows to determine the correct scale for matrices from Radius (Radii) input.")

    def getExecutionCode(self, required):
        if self.mode == "POINTS":
            if self.methodTypeForPoints == "DYNAMICRADIUS":
                yield "matrices, radii = self.execute_DynamicRadiusSpherePacking(points, margin, radiusMax, radiusStep, falloff, mask, objectRadii)"
            elif self.methodTypeForPoints == "NEIGHBOURRADIUS":
                yield "matrices, radii = self.execute_NeighbourRadiusSpherePacking(points, margin, radiusMax, radiusStep, falloff, mask, objectRadii)"
            elif self.methodTypeForPoints == "FIXEDRADIUS":
                yield "matrices, radii = self.execute_FixedSpherePacking(points, margin, Radius, falloff, mask, objectRadii)"
        elif self.mode == "RELAX":
            if self.pointsOnMesh:
                yield "matrices, radii, normals = self.execute_RelaxSpherePackingOnMesh(points, mesh, margin, radii, forceMagnitude, errorMax, iterations,\
                                                                                        falloff, mask, alignToNormal, objectRadii, epsilon, maxDistance)"
            else:
                yield "matrices, radii = self.execute_RelaxSpherePacking(points, margin, radii, forceMagnitude, errorMax, iterations, falloff, mask,\
                                                                         objectRadii)"
        elif self.mode == "POLYGONS":
            yield "matrices, radii = self.execute_SpherePackingOnMesh(mesh, falloff, alignToNormal, objectRadii)"

        if "vectors" in required:
            yield "vectors = AN.nodes.matrix.c_utils.extractMatrixTranslations(matrices)"

    def execute_DynamicRadiusSpherePacking(self, Vector3DList points, float margin, float radiusMax,
                                           float radiusStep, Falloff falloff, bint mask, objectRadii):
        cdef Py_ssize_t totalPoints = points.length
        if totalPoints == 0: return Matrix4x4List(), DoubleList()

        cdef FalloffEvaluator evaluator = self.getFalloffEvaluator(falloff)
        cdef FloatList influences = evaluator.evaluateList(points)
        cdef DoubleList _objectRadii = VirtualDoubleList.create(objectRadii, 1).materialize(totalPoints)
        return dynamicRadiusSpherePacking(points, margin, radiusMax, radiusStep, influences, mask, _objectRadii)

    def execute_NeighbourRadiusSpherePacking(self, Vector3DList points, float margin, float radiusMax,
                                             float radiusStep, Falloff falloff, bint mask, objectRadii):
        cdef Py_ssize_t totalPoints = points.length
        if totalPoints == 0: return Matrix4x4List(), DoubleList()

        cdef FalloffEvaluator evaluator = self.getFalloffEvaluator(falloff)
        cdef FloatList influences = evaluator.evaluateList(points)
        cdef DoubleList _objectRadii = VirtualDoubleList.create(objectRadii, 1).materialize(totalPoints)
        return neighbourRadiusSpherePacking(points, margin, radiusMax, radiusStep, influences, mask, _objectRadii)

    def execute_FixedSpherePacking(self, Vector3DList points, float margin, radii, Falloff falloff,
                                   bint mask, objectRadii):
        cdef Py_ssize_t totalPoints = points.length
        if totalPoints == 0: return Matrix4x4List(), DoubleList()

        cdef FalloffEvaluator evaluator = self.getFalloffEvaluator(falloff)
        cdef FloatList influences = evaluator.evaluateList(points)
        cdef DoubleList _objectRadii = VirtualDoubleList.create(objectRadii, 1).materialize(totalPoints)
        cdef DoubleList _radii = VirtualDoubleList.create(radii, 0).materialize(totalPoints)

        return fixedRadiusSpherePacking(points, max(margin, 0), _radii, influences, mask, _objectRadii,
                                        self.onlyCompareNewPoints)

    def execute_RelaxSpherePacking(self, Vector3DList points, float margin, radii, float forceMagnitude,
                                   float errorMax, Py_ssize_t iterations, Falloff falloff, bint mask, objectRadii):
        cdef Py_ssize_t totalPoints = points.length
        if totalPoints == 0: return Matrix4x4List(), DoubleList()

        cdef FalloffEvaluator evaluator = self.getFalloffEvaluator(falloff)
        cdef FloatList influences = evaluator.evaluateList(points)
        cdef DoubleList _radii = VirtualDoubleList.create(radii, 0).materialize(totalPoints)
        cdef DoubleList _objectRadii = VirtualDoubleList.create(objectRadii, 1).materialize(totalPoints)

        if forceMagnitude > 1: forceMagnitude = 1.0
        elif forceMagnitude < 0: forceMagnitude = 0.0

        return relaxSpherePacking(points, max(0, margin), _radii, forceMagnitude, iterations, errorMax,
                                  self.neighbourAmount, influences, mask, _objectRadii)

    def execute_RelaxSpherePackingOnMesh(self, Vector3DList points, Mesh mesh, float margin, radii,
                                         float forceMagnitude, float errorMax, Py_ssize_t iterations,
                                         Falloff falloff, bint mask, bint alignToNormal, objectRadii,
                                         float epsilon, float maxDistance):
        cdef Py_ssize_t totalPoints = points.length
        if totalPoints == 0: return Matrix4x4List(), DoubleList(), Vector3DList()

        cdef FalloffEvaluator evaluator = self.getFalloffEvaluator(falloff)
        cdef FloatList influences = evaluator.evaluateList(points)
        cdef DoubleList _radii = VirtualDoubleList.create(radii, 0).materialize(totalPoints)
        cdef DoubleList _objectRadii = VirtualDoubleList.create(objectRadii, 1).materialize(totalPoints)
        cdef Vector3DList vertices = mesh.vertices
        cdef PolygonIndicesList polygons = mesh.polygons

        if forceMagnitude > 1: forceMagnitude = 1.0
        elif forceMagnitude < 0: forceMagnitude = 0.0
        if vertices.length == 0 or polygons.getLength() == 0:
            return Matrix4x4List(), DoubleList(), Vector3DList()

        if 0 <= polygons.getMinIndex() <= polygons.getMaxIndex() < len(vertices):
            return relaxSpherePackingOnMesh(points, max(0, margin), _radii, forceMagnitude, iterations,
                                            errorMax, self.neighbourAmount, influences, mask, _objectRadii,
                                            vertices, polygons, maxDistance, epsilon, alignToNormal)

    def execute_SpherePackingOnMesh(self, Mesh mesh, Falloff falloff, bint alignToNormal, objectRadii):
        cdef Vector3DList vertices = mesh.vertices
        cdef PolygonIndicesList polygons = mesh.polygons
        cdef Vector3DList polyNormals = mesh.getPolygonNormals()

        if vertices.length == 0 or polygons.getLength() == 0:
            return Matrix4x4List(), DoubleList()

        if polygons.polyLengths.getMaxValue() > 3:
            self.raiseErrorMessage("Mesh has non-triangular polygons.")

        cdef DoubleList _objectRadii = VirtualDoubleList.create(objectRadii, 1).materialize(polygons.getLength())
        cdef FalloffEvaluator evaluator = self.getFalloffEvaluator(falloff)
        cdef FloatList influences = evaluator.evaluateList(mesh.getPolygonCenters())
        return spherePackingOnMesh(vertices, polygons, alignToNormal, polyNormals, influences, _objectRadii)

    def getFalloffEvaluator(self, falloff):
        try: return falloff.getEvaluator("LOCATION", True)
        except: self.raiseErrorMessage("This falloff cannot be evaluated for vectors.")
