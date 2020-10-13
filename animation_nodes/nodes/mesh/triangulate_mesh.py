import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode
from ... data_structures.meshes.validate import checkMeshData

class TriangulateMeshNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TriangulateMeshNode"
    bl_label = "Triangulate Mesh"
    errorHandlingType = "EXCEPTION"

    methodType: BoolProperty(name = "Use Advanced Method", default = False,
                             description = "Use advanced method for Mesh Triangulation",
                             update = propertyChanged)

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh", dataIsModified = True)

        self.newOutput("Mesh", "Mesh", "meshOut")

    def draw(self, layout):
        layout.prop(self, "methodType", text = "Use Advanced Method")

    def execute(self, mesh):
        if self.methodType:
            mesh.triangulateMesh(method = "EAR")
        else:
            mesh.triangulateMesh(method = "FAN")

        try:
            checkMeshData(mesh.vertices, mesh.edges, mesh.polygons, mesh.materialIndices)
            return mesh
        except Exception as e:
            self.raiseErrorMessage(str(e))
