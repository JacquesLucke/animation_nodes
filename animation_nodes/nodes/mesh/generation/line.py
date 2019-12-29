import bpy
from bpy.props import *
from .... data_structures import Mesh
from .... base_types import AnimationNode
from .... algorithms.mesh_generation.line import getLineMesh, edges

lineModeItems = [
    ("STARTEND", "Start-End", "Line from start-end", "NONE", 0),    
    ("POINTS", "Points", "Line from vector list", "NONE", 1)
]

class LineMeshNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_LineMeshNode"
    bl_label = "Line Mesh"

    lineMode: EnumProperty(name = "Line Mode", default = "STARTEND",
        items = lineModeItems, update = AnimationNode.refresh)

    def create(self):
        if self.lineMode == "STARTEND":
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
        if self.lineMode == "STARTEND":
            return "execute_StartEndLine"
        elif self.lineMode == "POINTS":
            return "execute_PointsLine"

    def execute_StartEndLine(self, start, end, steps):
        steps = max(steps, 2)
        return getLineMesh(start, end, steps)

    def execute_PointsLine(self, points, cyclic):
        if len(points) < 2: return Mesh()
        pointCount = len(points)
        edgeIndices = edges(pointCount)
        if cyclic:
            edgeIndices.append((pointCount - 1, 0))
            return Mesh(points, edgeIndices, skipValidation = True)
        else:    
            return Mesh(points, edgeIndices, skipValidation = True)

