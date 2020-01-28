import bpy
from bpy.props import *
from ... data_structures import Mesh
from ... base_types import AnimationNode
from ... algorithms.mesh_generation.find_shortest_path import getShortestPath

class FindShortestPathNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FindShortestPathNode"
    bl_label = "Find Shortest Path"
    errorHandlingType = "EXCEPTION"

    joinMeshes: BoolProperty(name = "Join Meshes", default = True,
        update = AnimationNode.refresh)

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh")
        self.newInput("Integer List", "Sources", "sources")

        if not self.joinMeshes:
            self.newOutput("Mesh List", "Meshes", "outMeshes")
        else:
            self.newOutput("Mesh", "Mesh", "outMesh")

    def draw(self, layout):
        layout.prop(self, "joinMeshes")

    def execute(self, mesh, sources):
        if mesh is None or len(sources) == 0:
            if self.joinMeshes:
                return Mesh()
            else:
                return []

        if sources.getMinValue() < 0 or sources.getMaxValue() >= len(mesh.vertices):
            self.raiseErrorMessage("Some indices is out of range.")

        if self.joinMeshes:
            return Mesh.join(*getShortestPath(mesh, sources))
        else:
            return getShortestPath(mesh, sources)
