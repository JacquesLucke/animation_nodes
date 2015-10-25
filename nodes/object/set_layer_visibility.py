import bpy
from bpy.props import *
from ... utils.layout import writeText
from ... base_types.node import AnimationNode

layerChoosingTypeItems = [
    ("SINGLE", "Single", ""),
    ("MULTIPLE", "Multiple", "") ]

class ObjectLayerVisibilityOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectLayerVisibilityOutputNode"
    bl_label = "Object Layer Visibility Output"

    def layerChoosingTypeChanged(self, context):
        self.recreateLayerInputSockets()

    errorMessage = StringProperty()

    layerChoosingType = EnumProperty(name = "Layer Choosing Type", default = "MULTIPLE",
        items = layerChoosingTypeItems, update = layerChoosingTypeChanged)

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.outputs.new("an_ObjectSocket", "Object", "object")
        self.recreateLayerInputSockets()

    def draw(self, layout):
        layout.prop(self, "layerChoosingType", text = "Type")
        if self.errorMessage != "":
            writeText(layout, self.errorMessage, icon = "ERROR", width = 20)

    def getExecutionCode(self):
        yield "if object:"
        if self.layerChoosingType == "MULTIPLE":
            yield "    visibilities = [{}]".format(", ".join("layer" + str(i + 1) for i in range(20)))
            yield "    object.layers = visibilities"
            yield "    self.errorMessage = '' if any(visibilities) else 'The target has to be visible on at least one layer'"

        if self.layerChoosingType == "SINGLE":
            yield "    if 0 <= layerIndex <= 19:"
            yield "        self.errorMessage = ''"
            yield "        layers = [False] * 20"
            yield "        layers[layerIndex] = True"
            yield "        object.layers = layers"
            yield "    else:"
            yield "        self.errorMessage = 'The layer index has to be between 0 and 19'"

    def recreateLayerInputSockets(self):
        self.clearLayerInputNodes()
        if self.layerChoosingType == "MULTIPLE":
            for i in range(20):
                self.inputs.new("an_BooleanSocket", "Layer " + str(i + 1), "layer" + str(i + 1)).value = False
            for socket in self.inputs[4:]:
                socket.hide = True
            self.inputs[1].value = True
        if self.layerChoosingType == "SINGLE":
            self.inputs.new("an_IntegerSocket", "Layer Index", "layerIndex")

    def clearLayerInputNodes(self):
        for socket in self.inputs[1:]:
            socket.remove()
