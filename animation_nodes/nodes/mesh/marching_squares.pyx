import bpy
from bpy.props import *
from ... base_types import AnimationNode, VectorizedSocket
from ... algorithms.mesh_generation.marching_squares import marchingSquares
from ... data_structures cimport Falloff, FalloffEvaluator, VirtualDoubleList

distanceModeItems = [
    ("STEP", "Step", "Define the distance between two points", "NONE", 0),
    ("SIZE", "Size", "Define how large the grid will be in total", "NONE", 1)
]

class MarchingSquaresNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MarchingSquaresNode"
    bl_label = "Marching Squares"
    errorHandlingType = "EXCEPTION"

    __annotations__ = {}

    __annotations__["distanceMode"] = EnumProperty(name = "Distance Mode", default = "SIZE",
        items = distanceModeItems, update = AnimationNode.refresh)
    __annotations__["clampFalloff"] = BoolProperty(name = "Clamp Falloff", default = False)
    __annotations__["useToleranceList"] = VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Integer", "X Divisions", "xDivisions", value = 3, minValue = 2)
        self.newInput("Integer", "Y Divisions", "yDivisions", value = 3, minValue = 2)
        if self.distanceMode == "STEP":
            self.newInput("Float", "X Distance", "xSize", value = 1)
            self.newInput("Float", "Y Distance", "ySize", value = 1)
        elif self.distanceMode == "SIZE":
            self.newInput("Float", "Width", "xSize", value = 5)
            self.newInput("Float", "Length", "ySize", value = 5)
        self.newInput("Falloff", "Falloff", "falloff")
        self.newInput(VectorizedSocket("Float", "useToleranceList",
            ("Threshold", "thresholds"), ("Thresholds", "thresholds")), value = 0.25)
        self.newInput("Vector", "Grid Offset", "offset", hide = True)

        self.newOutput("Mesh", "Mesh", "mesh")
        self.newOutput("Vector List", "Grid Points", "points", hide = True)

    def draw(self, layout):
        col = layout.column()
        col.prop(self, "distanceMode", text = "")

    def execute(self, xDivisions, yDivisions, xSize, ySize, falloff, thresholds, offset):
        cdef VirtualDoubleList _thresholds = VirtualDoubleList.create(thresholds, 0)
        cdef long amountThreshold

        if not self.useToleranceList:
            amountThreshold = 1
        else:
            amountThreshold = _thresholds.getRealLength()

        cdef FalloffEvaluator falloffEvaluator = self.getFalloffEvaluator(falloff)
        return marchingSquares(xDivisions, yDivisions, xSize, ySize, falloffEvaluator,
                               amountThreshold, _thresholds, offset, self.distanceMode)

    def getFalloffEvaluator(self, falloff):
        try: return falloff.getEvaluator("LOCATION", self.clampFalloff)
        except: self.raiseErrorMessage("This falloff cannot be evaluated for vectors")
