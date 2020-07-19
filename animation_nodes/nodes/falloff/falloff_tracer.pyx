import bpy
from bpy.props import *
from mathutils.bvhtree import BVHTree
from ... events import propertyChanged
from ... base_types import AnimationNode
from . falloff_tracer_utils import (
    curlOfFalloff2D,
    curlOfFalloff3D,
    gradientOfFalloff3D,
    getCurvesPerVectors,
    getCurvesPerIterations,
    curlOfFalloff3DOnMesh,
    gradientOfFalloff3DOnMesh,
)
from ... data_structures cimport(
    Mesh,
    Falloff,
    Vector3DList,
    FalloffEvaluator,
    PolygonIndicesList,
)

tracerModeItems = [
    ("CURL2D", "Curl 2D", "", "", 0),
    ("CURL3D", "Curl 3D", "", "", 1),
    ("GRADIENT3D", "Gradient 3D", "", "", 2)
]

dataStyleItems = [
    ("PERVECTOR", "Per Vector", "Output a curve for each vector", "", 0),
    ("PERITERATION", "Per Iterartion", "Output a curve for each iteration", "", 1)
]

dataTypeItems = [
    ("STROKE", "Stroke", "Output gp strokes", "", 0),
    ("SPLINE", "Spline", "Output splines", "", 1),
    ("MESH", "Mesh", "", "Output mesh(s)", 2)
]

class FalloffTracerNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FalloffTracerNode"
    bl_label = "Falloff Tracer"
    bl_width_default = 160
    errorHandlingType = "EXCEPTION"

    __annotations__ = {}

    __annotations__["tracerMode"] = EnumProperty(name = "Mode", default = "CURL2D",
        items = tracerModeItems, update = AnimationNode.refresh)

    __annotations__["dataStyle"] = EnumProperty(name = "Output Style Mode", default = "PERVECTOR",
        items = dataStyleItems, update = AnimationNode.refresh)

    __annotations__["dataType"] = EnumProperty(name = "Output Mode", default = "SPLINE",
        items = dataTypeItems, update = AnimationNode.refresh)

    __annotations__["vectorsOnMesh"] = BoolProperty(name = "Vectors on Mesh", default = False,
        update = AnimationNode.refresh)

    __annotations__["joinMeshes"] = BoolProperty(name = "Join Meshes", default = True,
        update = AnimationNode.refresh)

    def create(self):
        self.newInput("Vector List", "Vectors", "vectors")

        self.newInput("Integer", "Iterations", "iterations", value = 50, minValue = 0)
        self.newInput("Float", "Step", "step", value = 0.1, minValue = 0.00001)
        if self.tracerMode == "CURL2D":
            self.newInput("Integer", "Style", "style", value = 1, minValue = 1, maxValue = 4)
        elif self.tracerMode in ["CURL3D", "GRADIENT3D"] and self.vectorsOnMesh:
            self.newInput("Mesh", "Mesh", "mesh")
        elif self.tracerMode == "GRADIENT3D" and not self.vectorsOnMesh:
            self.newInput("Vector", "Axis Scale", "axisScale", value = (1, 1, 1), hide = True)
        self.newInput("Falloff", "Falloff", "falloff")
        if self.dataStyle == "PERITERATION":
            self.newInput("Boolean", "Cyclic", "cyclic", value = False)
        if self.tracerMode in ["CURL3D", "GRADIENT3D"] and self.vectorsOnMesh:
            self.newInput("Float", "Epsilon", "epsilon", value = 0, minValue = 0, hide = True)
            self.newInput("Float", "Max Distance", "maxDistance", value = 1e+6, minValue = 0, hide = True)

        if self.dataType == "MESH":
            if not self.joinMeshes:
                self.newOutput("Mesh List", "Meshes", "meshes")
            else:
                self.newOutput("Mesh", "Mesh", "meshOut")
        elif self.dataType == "SPLINE":
            self.newOutput("Spline List", "Splines", "splines")
        elif self.dataType == "STROKE":
            self.newOutput("GPStroke List", "Strokes", "strokes")
        self.newOutput("Vector List", "Vectors", "vectorsOut", hide = True)

    def draw(self, layout):
        layout.prop(self, "tracerMode", text = "")
        row = layout.row(align = True)
        row.prop(self, "dataStyle", text = "")
        row.prop(self, "dataType", text = "")
        if self.tracerMode in ["CURL3D", "GRADIENT3D"]:
            layout.prop(self, "vectorsOnMesh")
        if self.dataType == "MESH":
            layout.prop(self, "joinMeshes")

    def getExecutionFunctionName(self):
        if self.tracerMode == "CURL2D":
            return "execute_curlOfFalloff2D"
        elif self.tracerMode == "CURL3D":
            if self.vectorsOnMesh:
                return "execute_curlOfFalloff3DOnMesh"
            else:
                return "execute_curlOfFalloff3D"
        elif self.tracerMode == "GRADIENT3D":
            if self.vectorsOnMesh:
                return "execute_gradientOfFalloff3DOnMesh"
            else:
                return "execute_gradientOfFalloff3D"

    def execute_curlOfFalloff2D(self, vectors, *settings):
        newSettings = [*settings]
        cdef Falloff falloff = newSettings[3]
        cdef FalloffEvaluator evaluator = self.getFalloffEvaluator(falloff)

        curlNoiseSettings = newSettings[:3]
        if curlNoiseSettings[0] <= 0: return self.emptyOutput()

        vectorsOut = curlOfFalloff2D(vectors, *curlNoiseSettings, "", None, evaluator)
        cdef bint cyclic = False
        if self.dataStyle == "PERITERATION":
            cyclic = newSettings[4]
        return self.outputData(len(vectors), curlNoiseSettings[0], vectorsOut, cyclic)

    def execute_curlOfFalloff3D(self, vectors, *settings):
        newSettings = [*settings]
        cdef Falloff falloff = newSettings[2]
        cdef FalloffEvaluator evaluator = self.getFalloffEvaluator(falloff)

        curlNoiseSettings = newSettings[:2]
        if curlNoiseSettings[0] <= 0: return self.emptyOutput()

        vectorsOut = curlOfFalloff3D(vectors, *curlNoiseSettings, "", None, evaluator)
        cdef bint cyclic = False
        if self.dataStyle == "PERITERATION":
            cyclic = newSettings[3]
        return self.outputData(len(vectors), curlNoiseSettings[0], vectorsOut, cyclic)

    def execute_curlOfFalloff3DOnMesh(self, vectors, *settings):
        newSettings = [*settings]
        cdef Falloff falloff = newSettings[3]
        cdef FalloffEvaluator evaluator = self.getFalloffEvaluator(falloff)

        curlNoiseSettings = newSettings[:3]
        if curlNoiseSettings[0] <= 0: return self.emptyOutput()

        bvhTree = self.buildBVHTree(curlNoiseSettings[2], newSettings[-2])
        if bvhTree is None: return self.emptyOutput()

        curlNoiseSettings[2] = bvhTree
        curlNoiseSettings.append(newSettings[-1])

        cdef bint cyclic = False
        if self.dataStyle == "PERITERATION":
            cyclic = newSettings[-3]
        vectorsOut = curlOfFalloff3DOnMesh(vectors, *curlNoiseSettings, "", None, evaluator)
        return self.outputData(len(vectors), curlNoiseSettings[0], vectorsOut, cyclic)

    def execute_gradientOfFalloff3D(self, vectors, *settings):
        newSettings = [*settings]
        cdef Falloff falloff = newSettings[3]
        cdef FalloffEvaluator evaluator = self.getFalloffEvaluator(falloff)

        curlNoiseSettings = newSettings[:3]
        if curlNoiseSettings[0] <= 0: return self.emptyOutput()

        vectorsOut = gradientOfFalloff3D(vectors, *curlNoiseSettings, "", None, evaluator)
        cdef bint cyclic = False
        if self.dataStyle == "PERITERATION":
            cyclic = newSettings[4]
        return self.outputData(len(vectors), curlNoiseSettings[0], vectorsOut, cyclic)

    def execute_gradientOfFalloff3DOnMesh(self, vectors, *settings):
        newSettings = [*settings]
        cdef Falloff falloff = newSettings[3]
        cdef FalloffEvaluator evaluator = self.getFalloffEvaluator(falloff)

        curlNoiseSettings = newSettings[:3]
        if curlNoiseSettings[0] <= 0: return self.emptyOutput()

        bvhTree = self.buildBVHTree(curlNoiseSettings[2], newSettings[-2])
        if bvhTree is None: return self.emptyOutput()

        curlNoiseSettings[2] = bvhTree
        curlNoiseSettings.append(newSettings[-1])

        vectorsOut = gradientOfFalloff3DOnMesh(vectors, *curlNoiseSettings, "", None, evaluator)
        cdef bint cyclic = False
        if self.dataStyle == "PERITERATION":
            cyclic = newSettings[-3]
        return self.outputData(len(vectors), curlNoiseSettings[0], vectorsOut, cyclic)

    def getFalloffEvaluator(self, falloff):
        try: return falloff.getEvaluator("LOCATION", True)
        except: self.raiseErrorMessage("This falloff cannot be evaluated for vectors.")

    def buildBVHTree(self, mesh, epsilon):
        cdef Vector3DList vertices = mesh.vertices
        cdef PolygonIndicesList polygons = mesh.polygons
        if (vertices.length == 0 or len(polygons) == 0 or
            (len(polygons) > 0 and polygons.getMaxIndex() >= vertices.length)): return None
        return BVHTree.FromPolygons(vertices, polygons, epsilon = max(epsilon, 0))

    def outputData(self, long amount, long iterations, Vector3DList vectorsOut, bint cyclic):
        if self.dataStyle == "PERVECTOR":
            curves = getCurvesPerVectors(amount, iterations, vectorsOut, self.dataType)
        else:
            curves = getCurvesPerIterations(amount, iterations, vectorsOut, self.dataType, cyclic)
        if self.dataType == "MESH":
            if self.joinMeshes:
                return Mesh.join(*curves), vectorsOut
            else:
                return curves, vectorsOut
        return curves, vectorsOut

    def emptyOutput(self):
        if self.joinMeshes and self.dataType == "MESH":
            return Mesh(), Vector3DList()
        else:
            return [], Vector3DList()
