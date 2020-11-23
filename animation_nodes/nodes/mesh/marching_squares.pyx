import bpy
from bpy.props import *
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures.meshes.mesh_data import calculatePolygonNormals
from ... algorithms.mesh_generation.marching_squares import marchingSquaresOnGrid, marchingSquaresOnMesh
from ... data_structures cimport (
    Mesh,
    Falloff,
    Vector3DList,
    FalloffEvaluator,
    VirtualDoubleList,
    PolygonIndicesList,
)

modeItems = [
    ("GRID", "Grid", "Grid points for marching", "NONE", 0),
    ("MESH", "Mesh", "Mesh surface for marching", "NONE", 1)
]

distanceModeItems = [
    ("STEP", "Step", "Define the distance between two points", "NONE", 0),
    ("SIZE", "Size", "Define how large the grid will be in total", "NONE", 1)
]

class MarchingSquaresNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MarchingSquaresNode"
    bl_label = "Marching Squares"
    errorHandlingType = "EXCEPTION"

    __annotations__ = {}

    __annotations__["mode"] = EnumProperty(name = "Mode", default = "GRID",
        items = modeItems, update = AnimationNode.refresh)

    __annotations__["distanceMode"] = EnumProperty(name = "Distance Mode", default = "SIZE",
        items = distanceModeItems, update = AnimationNode.refresh)
    __annotations__["clampFalloff"] = BoolProperty(name = "Clamp Falloff", default = False)
    __annotations__["useToleranceList"] = VectorizedSocket.newProperty()

    def create(self):
        if self.mode == "GRID":
            self.newInput("Integer", "X Divisions", "xDivisions", value = 3, minValue = 2)
            self.newInput("Integer", "Y Divisions", "yDivisions", value = 3, minValue = 2)
            if self.distanceMode == "STEP":
                self.newInput("Float", "X Distance", "xSize", value = 1)
                self.newInput("Float", "Y Distance", "ySize", value = 1)
            elif self.distanceMode == "SIZE":
                self.newInput("Float", "Width", "xSize", value = 5)
                self.newInput("Float", "Length", "ySize", value = 5)
        else:
            self.newInput("Mesh", "Mesh", "mesh", dataIsModified = True)
        self.newInput("Falloff", "Falloff", "falloff")
        self.newInput(VectorizedSocket("Float", "useToleranceList",
            ("Threshold", "thresholds"), ("Thresholds", "thresholds")), value = 0.25)
        if self.mode == "GRID":
            self.newInput("Vector", "Grid Offset", "offset", hide = True)

        self.newOutput("Mesh", "Mesh", "mesh")
        if self.mode == "GRID":
            self.newOutput("Vector List", "Grid Points", "points", hide = True)
        else:
            self.newOutput("Vector List", "Normals", "normals", hide = True)

    def draw(self, layout):
        layout.prop(self, "mode", text = "")
        if self.mode == "GRID":
            layout.prop(self, "distanceMode", text = "")

    def getExecutionFunctionName(self):
        if self.mode == "GRID":
            return "execute_MarchingSquaresOnGrid"
        else:
            return "execute_MarchingSquaresOnMesh"

    def execute_MarchingSquaresOnGrid(self, xDivisions, yDivisions, xSize, ySize, falloff,
                                      thresholds, offset):
        cdef VirtualDoubleList _thresholds = VirtualDoubleList.create(thresholds, 0)
        cdef long amountThreshold

        if not self.useToleranceList:
            amountThreshold = 1
        else:
            amountThreshold = _thresholds.getRealLength()

        cdef FalloffEvaluator falloffEvaluator = self.getFalloffEvaluator(falloff)
        return marchingSquaresOnGrid(xDivisions, yDivisions, xSize, ySize, falloffEvaluator,
                                     amountThreshold, _thresholds, offset, self.distanceMode)

    def execute_MarchingSquaresOnMesh(self, mesh, falloff, thresholds):
        cdef Vector3DList vertices = mesh.vertices
        cdef PolygonIndicesList polygons = mesh.polygons
        if vertices.length == 0:
            return Mesh(), Vector3DList()
        if polygons.polyLengths.getMinValue() < 4 or polygons.polyLengths.getMaxValue() > 4:
            self.raiseErrorMessage("Mesh has non-quad polygons")

        cdef VirtualDoubleList _thresholds = VirtualDoubleList.create(thresholds, 0)
        cdef long amountThreshold

        if not self.useToleranceList:
            amountThreshold = 1
        else:
            amountThreshold = _thresholds.getRealLength()

        cdef FalloffEvaluator falloffEvaluator = self.getFalloffEvaluator(falloff)
        cdef Vector3DList polyNormals = calculatePolygonNormals(vertices, polygons)
        return marchingSquaresOnMesh(vertices, polygons, polyNormals, falloffEvaluator,
                                     amountThreshold, _thresholds)

    def getFalloffEvaluator(self, falloff):
        try: return falloff.getEvaluator("LOCATION", self.clampFalloff)
        except: self.raiseErrorMessage("This falloff cannot be evaluated for vectors")
