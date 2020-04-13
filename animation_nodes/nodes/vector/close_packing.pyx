import bpy
from bpy.props import *
from ... base_types import AnimationNode
from ... algorithms.mesh_generation.close_packing import(
    neighbourRadiusSpherePacking,
    dynamicRadiusSpherePacking,
    fixedRadiusSpherePacking,
    spherePackingOnMesh,
    relaxSpherePacking,
)
from ... data_structures cimport(
    Mesh,
    Falloff,
    FloatList,
    DoubleList,
    Vector3DList,
    Matrix4x4List,
    FalloffEvaluator,
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

    __annotations__["neighbourAmount"] = IntProperty(name = "Neighbour Amount", min = 1, max = 10, default = 1)

    def create(self):
        if self.mode == "POINTS":
            self.newInput("Vector List", "Points", "points", dataIsModified = True)
            self.newInput("Float", "Margin", "margin", value = 0.01, minValue = 0)
            self.newInput("Float", "Radius Max", "radiusMax", value = 0.1, minValue = 0)
            if self.methodTypeForPoints in ["DYNAMICRADIUS", "NEIGHBOURRADIUS"]:
                self.newInput("Float", "Radius Step", "radiusStep", value = 0.005, minValue = 0.00001)
            self.newInput("Falloff", "Falloff", "falloff")
            self.newInput("Boolean", "Mask", "mask", value = False, hide = True)
        elif self.mode == "RELAX":
            self.newInput("Vector List", "Points", "points", dataIsModified = True)
            self.newInput("Float", "Margin", "margin", value = 0.01, minValue = 0)
            self.newInput("Float", "Radius Max", "radiusMax", value = 0.1, minValue = 0)
            self.newInput("Float", "Repulsion Factor", "repulsionFactor", value = 0.5, minValue = 0, maxValue = 1)
            self.newInput("Float", "Error Max(%)", "errorMax", value = 2, minValue = 0.001, maxValue = 100, hide = True)
            self.newInput("Integer", "Iterations Max", "iterations", value = 100, minValue = 0, hide = True)
            self.newInput("Falloff", "Falloff", "falloff")
            self.newInput("Boolean", "Mask", "mask", value = False, hide = True)
        elif self.mode == "POLYGONS":
            self.newInput("Mesh", "Mesh", "mesh", dataIsModified = True)
            self.newInput("Falloff", "Falloff", "falloff")
            self.newInput("Boolean", "Align To Normal", "alignToNormal", value = False)

        self.newOutput("Matrix List", "Matrices", "matrices")
        self.newOutput("Float List", "Radii", "radii", hide = True)

    def draw(self, layout):
        col = layout.column()
        col.prop(self, "mode", text = "")
        if self.mode == "POINTS":
            col.prop(self, "methodTypeForPoints", text = "")

    def drawAdvanced(self, layout):
        col = layout.column()
        if self.mode == "RELAX":
            col.prop(self, "neighbourAmount")

    def getExecutionFunctionName(self):
        if self.mode == "POINTS":
            if self.methodTypeForPoints == "DYNAMICRADIUS":
                return "execute_DynamicRadiusSpherePacking"
            elif self.methodTypeForPoints == "NEIGHBOURRADIUS":
                return "execute_NeighbourRadiusSpherePacking"
            elif self.methodTypeForPoints == "FIXEDRADIUS":
                return "execute_FixedSpherePacking"
        elif self.mode == "RELAX":
            return "execute_RelaxSpherePacking"
        elif self.mode == "POLYGONS":
            return "execute_SpherePackingForMesh"

    def execute_DynamicRadiusSpherePacking(self, Vector3DList points, float margin, float radiusMax, float radiusStep,
                                           Falloff falloff, bint mask):
        if points.length == 0: return Matrix4x4List(), DoubleList()

        cdef FalloffEvaluator evaluator = self.getFalloffEvaluator(falloff)
        cdef FloatList influences = evaluator.evaluateList(points)
        return dynamicRadiusSpherePacking(points, margin, radiusMax, radiusStep, influences, mask)

    def execute_NeighbourRadiusSpherePacking(self, Vector3DList points, float margin, float radiusMax, float radiusStep,
                                             Falloff falloff, bint mask):
        if points.length == 0: return Matrix4x4List(), DoubleList()

        cdef FalloffEvaluator evaluator = self.getFalloffEvaluator(falloff)
        cdef FloatList influences = evaluator.evaluateList(points)
        return neighbourRadiusSpherePacking(points, margin, radiusMax, radiusStep, influences, mask)

    def execute_FixedSpherePacking(self, Vector3DList points, float margin, float radiusMax, Falloff falloff, bint mask):
        if points.length == 0: return Matrix4x4List(), DoubleList()

        cdef FalloffEvaluator evaluator = self.getFalloffEvaluator(falloff)
        cdef FloatList influences = evaluator.evaluateList(points)
        return fixedRadiusSpherePacking(points, max(margin, 0), radiusMax, influences, mask)

    def execute_RelaxSpherePacking(self, Vector3DList points, float margin, float radiusMax, float repulsionFactor,
                                   float errorMax, Py_ssize_t iterations, Falloff falloff, bint mask):
        if points.length == 0: return Matrix4x4List(), DoubleList()

        cdef FalloffEvaluator evaluator = self.getFalloffEvaluator(falloff)
        cdef FloatList influences = evaluator.evaluateList(points)
        return relaxSpherePacking(points, margin, radiusMax, repulsionFactor, iterations, errorMax, self.neighbourAmount,
                                  influences, mask)

    def execute_SpherePackingForMesh(self, Mesh mesh, Falloff falloff, bint alignToNormal):
        cdef Vector3DList vertices = mesh.vertices
        cdef PolygonIndicesList polygons = mesh.polygons
        cdef Vector3DList polyNormals = mesh.getPolygonNormals()

        if vertices.length == 0 or polygons.getLength() == 0:
            return Matrix4x4List(), DoubleList()

        if polygons.polyLengths.getMaxValue() > 3:
            self.raiseErrorMessage("Mesh has non-triangular polygons.")

        cdef FalloffEvaluator evaluator = self.getFalloffEvaluator(falloff)
        cdef FloatList influences = evaluator.evaluateList(mesh.getPolygonCenters())
        return spherePackingOnMesh(vertices, polygons, alignToNormal, polyNormals, influences)

    def getFalloffEvaluator(self, falloff):
        try: return falloff.getEvaluator("LOCATION", True)
        except: self.raiseErrorMessage("This falloff cannot be evaluated for vectors.")
