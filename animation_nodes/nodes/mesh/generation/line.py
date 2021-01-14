import bpy
from bpy.props import *
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
        self.newOutput("Vector List", "Vertices", "vertices", hide = True)
        self.newOutput("Edge Indices", "Edges", "edges", hide = True)

    def draw(self, layout):
        layout.prop(self, "lineMode", text = "")

    def getExecutionFunctionName(self):
        if self.lineMode == "START_END":
            return "execute_StartEndLine"
        elif self.lineMode == "POINTS":
            return "execute_PointsLine"

    def execute_StartEndLine(self, start, end, steps):
        steps = max(steps, 2)
        mesh = getLineMesh(start, end, steps)
        return mesh, mesh.vertices, mesh.edges

    def execute_PointsLine(self, points, cyclic):
        pointAmount = len(points)
        if pointAmount < 2:
            self.raiseErrorMessage("Points list should have at least two points.")
        if pointAmount < 3 and cyclic:
            self.raiseErrorMessage("For cyclic, Points list should have at least three points.")
        mesh = getLinesMesh(points, cyclic)
        return mesh, mesh.vertices, mesh.edges
