import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... events import propertyChanged


class SetVertexColorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetVertexColorNode"
    bl_label = "Set Vertex Color"

    enabled = BoolProperty(default = True, update = propertyChanged)
    vertexColorName = StringProperty(default = "Col", update = propertyChanged)
    checkIfColorIsSet = BoolProperty(default = True)
    errorMessage = StringProperty()

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.inputs.new("an_ColorSocket", "Color", "color")
        self.outputs.new("an_ObjectSocket", "Object", "outObject")

    def draw(self, layout):
        layout.prop(self, "enabled", text = "Enabled")
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def drawAdvanced(self, layout):
        layout.prop(self, "checkIfColorIsSet", text = "Check Color")
        layout.prop(self, "vertexColorName", text = "Name")

    def execute(self, object, color):
        if not self.enabled: return object
        if object is None: return object
        if object.mode == "EDIT":
            self.errorMessage = "Object is in edit mode"
            return object

        mesh = object.data

        colorLayer = mesh.vertex_colors.get(self.vertexColorName)
        if colorLayer is None:
            colorLayer = mesh.vertex_colors.new(self.vertexColorName)

        color = color[:3]
        if self.checkIfColorIsSet:
            oldColor = colorLayer.data[0].color
            if abs(color[0] * 100 + color[1] * 10 + color[2] - oldColor[0] * 100 - oldColor[1] * 10 - oldColor[2]) < 0.001:
                return object

        for meshColor in colorLayer.data:
            meshColor.color = color

        self.errorMessage = ""
        return object
