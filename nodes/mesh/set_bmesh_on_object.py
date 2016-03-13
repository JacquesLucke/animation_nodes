import bpy
from bpy.props import *
from ... utils.layout import writeText
from ... base_types.node import AnimationNode

class SetBMeshOnObjectNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetBMeshOnObjectNode"
    bl_label = "Set BMesh on Object"
    bl_width_default = 170

    errorMessage = StringProperty()

    def create(self):
        socket = self.inputs.new("an_ObjectSocket", "Object", "object")
        socket.defaultDrawType = "PROPERTY_ONLY"
        socket.objectCreationType = "MESH"
        self.inputs.new("an_BMeshSocket", "BMesh", "bm")
        self.outputs.new("an_ObjectSocket", "Object", "object")

    def draw(self, layout):
        if self.errorMessage != "":
            writeText(layout, self.errorMessage, icon = "ERROR", width = 20)

    def execute(self, object, bm):
        if object is None: return object
        if object.type != "MESH" or object.mode != "OBJECT":
            self.errorMessage = "Object is not in object mode or is no mesh object"
            return object
        bm.to_mesh(object.data)
        self.errorMessage = ""
        return object
