import bpy
from bpy.props import *
from ... data_structures import Mesh
from ... base_types import AnimationNode
from ... algorithms.mesh_generation.find_shortest_path import getShortestPath

pathTypeItems = [
    ("MESH", "Mesh", "Paths as line meshs", 0),
    ("SPLINE", "Spline", "Paths as poly splines", 1),
    ("STROKE", "Stroke", "Paths as gp strokes", 2)
]

class FindShortestPathNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FindShortestPathNode"
    bl_label = "Find Shortest Path"
    errorHandlingType = "EXCEPTION"

    pathType: EnumProperty(name = "Path Type", default = "MESH",
        items = pathTypeItems, update = AnimationNode.refresh)

    joinMeshes: BoolProperty(name = "Join Meshes", default = True,
        update = AnimationNode.refresh)

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh")
        self.newInput("Integer List", "Sources", "sources")
        if self.pathType == "MESH":
            if not self.joinMeshes:
                self.newOutput("Mesh List", "Meshes", "outMeshes")
            else:
                self.newOutput("Mesh", "Mesh", "outMesh")
        elif self.pathType == "SPLINE":
            self.newOutput("Spline List", "Splines", "outSplines")
        elif self.pathType == "STROKE":
            self.newOutput("GPStroke List", "Strokes", "outStrokes")

    def draw(self, layout):
        layout.prop(self, "pathType", text = "")
        if self.pathType == "MESH":
            layout.prop(self, "joinMeshes")

    def execute(self, mesh, sources):
        if mesh is None or len(sources) == 0:
            if self.joinMeshes and self.pathType == "MESH":
                return Mesh()
            else:
                return []

        if sources.getMinValue() < 0 or sources.getMaxValue() >= len(mesh.vertices):
            self.raiseErrorMessage("Some indices is out of range.")

        if self.pathType == "MESH":
            if self.joinMeshes:
                return Mesh.join(*getShortestPath(mesh, sources, "MESH"))
            else:
                return getShortestPath(mesh, sources, "MESH")
        elif self.pathType == "SPLINE":
            return getShortestPath(mesh, sources, "SPLINE")
        elif self.pathType == "STROKE":
            return getShortestPath(mesh, sources, "STROKE")
