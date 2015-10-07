import bpy
from bpy.props import *
from ... utils.layout import writeText
from ... base_types.node import AnimationNode

class ObjectLayerVisibilityOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectLayerVisibilityOutputNode"
    bl_label = "Object Layer Visibility Output"

    errorMessage = StringProperty()

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        for i in range(20):
            self.inputs.new("an_BooleanSocket", "Layer " + str(i + 1), "layer" + str(i + 1)).value = False
        for socket in self.inputs[4:]:
            socket.hide = True
        self.inputs[1].value = True
        self.outputs.new("an_ObjectSocket", "Object", "object")

    def draw(self, layout):
        if self.errorMessage != "":
            writeText(layout, self.errorMessage, icon = "ERROR", width = 20)

    def getExecutionCode(self):
        yield "if object:"
        yield "    visibilities = [{}]".format(", ".join("layer" + str(i + 1) for i in range(20)))
        yield "    object.layers = visibilities"
        yield "    self.errorMessage = '' if any(visibilities) else 'The target has to be visible on at least one layer'"
