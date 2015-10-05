import bpy
import itertools
from bpy.props import *
from ... base_types.node import AnimationNode

class SetVerticesOnObjectNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetVerticesOnObjectNode"
    bl_label = "Set Vertices on Object"

    errorMessage = StringProperty()

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.inputs.new("an_VectorListSocket", "Vertices", "vertices")
        self.outputs.new("an_ObjectSocket", "Object", "object")

    def draw(self, layout):
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def execute(self, object, vertices):
        if getattr(object, "type", "") != "MESH": return object
        mesh = object.data
        if len(mesh.vertices) != len(vertices):
            self.errorMessage = "The vertices amounts are not equal"
            return object
        self.errorMessage = ""

        flatVertices = list(itertools.chain.from_iterable(vertices))
        mesh.vertices.foreach_set("co", flatVertices)
        mesh.update()
        return object
