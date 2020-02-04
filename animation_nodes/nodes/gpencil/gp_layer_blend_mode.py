import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket

blendModeItems = [
    ("REGULAR", "Regular", "Layer blend mode", "NONE", 0),
    ("OVERLAY", "Overlay", "Layer blend mode", "NONE", 1),
    ("ADD", "Add", "Layer blend mode", "NONE", 2),
    ("SUBTRACT", "Subtract", "Layer blend mode", "NONE", 3),
    ("MULTIPLY", "Multiply", "Layer blend mode", "NONE", 4),
    ("DIVIDE", "Divide", "Layer blend mode", "NONE", 5)
]

class GPLayerBlendModeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPLayerBlendModeNode"
    bl_label = "GP Layer Blend Mode"

    blendMode: EnumProperty(name = "Layer blend mode", default = "REGULAR",
        items = blendModeItems, update = AnimationNode.refresh)

    useLayerList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPLayer", "useLayerList",
            ("Layer", "layer"), ("Layers", "layers")), dataIsModified = True)
        self.newOutput(VectorizedSocket("GPLayer", "useLayerList",
            ("Layer", "layer"), ("Layers", "layers")))

    def draw(self, layout):
        layout.prop(self, "blendMode", text = "")

    def getExecutionFunctionName(self):
        if self.useLayerList:
            return "execute_LayerList"
        else:
            return "execute_Layer"

    def execute_Layer(self, layer):
        layer.blendMode = self.blendMode
        return layer

    def execute_LayerList(self, layers):
        for layer in layers:
            layer.blendMode = self.blendMode
        return layers
