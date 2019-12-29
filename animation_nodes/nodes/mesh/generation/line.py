import bpy
from bpy.props import *
from .... data_structures import Mesh
from .... base_types import AnimationNode
from .... algorithms.mesh_generation.line import getLineMesh, getLinesMesh

lineModeItems = [
    ("START_END", "Start-End", "Line from start-end", "NONE", 0),    
    ("POINTS", "Points", "Line from vector list", "NONE", 1)
]

class LineMeshNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_LineMeshNode"
    bl_label = "Line Mesh"
    errorHandlingType = "EXCEPTION"

    lineMode: EnumProperty(name = "Line Mode", default = "START_END",
        items = lineModeItems, update = AnimationNode.refresh)

    def create(self):
        if self.lineMode == "START_END":
            self.newInput("Vector", "Start", "start")
            self.newInput("Vector", "End", "end", value = [5, 0, 0])
            self.newInput("Integer", "Steps", "steps", value = 2, minValue = 2)
        elif self.lineMode == "POINTS":
            self.newInput("Vector List", "Points", "points")
            self.newInput("Boolean", "Cyclic", "cyclic", value = False)

        self.newOutput("Mesh", "Mesh", "mesh")

    def draw(self, layout):
        layout.prop(self, "lineMode", text = "")

    def getExecutionFunctionName(self):
        if self.lineMode == "START_END":
            return "execute_StartEndLine"
        elif self.lineMode == "POINTS":
            return "execute_PointsLine"

    def execute_StartEndLine(self, start, end, steps):
        steps = max(steps, 2)
        return getLineMesh(start, end, steps)

    def execute_PointsLine(self, points, cyclic):
        if len(points) < 2:
            self.raiseErrorMessage("Points list should have atleast two points.")
        return getLinesMesh(points, cyclic)
        
        