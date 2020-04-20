import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode

class TriangulateMeshNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TriangulateMeshNode"
    bl_label = "Triangulate Mesh"

    methodType: BoolProperty(name = "Use Advanced Method", default = False,
                             description = "Use advanced method for Mesh Triangulation",
                             update = propertyChanged)

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh")

        self.newOutput("Mesh", "Mesh", "meshOut")

    def draw(self, layout):
        layout.prop(self, "methodType", text = "Use Advanced Method")

    def execute(self, mesh):
        meshOut = mesh.copy()
        if self.methodType:
            meshOut.triangulateMesh(method = "EAR")
        else:
            meshOut.triangulateMesh(method = "FAN")
        return meshOut
