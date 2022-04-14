import bpy
from ... data_structures import Color, ColorList
from ... base_types import AnimationNode, VectorizedSocket

class LampColorInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_LampColorInputNode"
    bl_label = "Lamp Color Input"
    useObjectList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Object", "useObjectList",
            ("Object", "object", dict(defaultDrawType = "PROPERTY_ONLY")),
            ("Objects", "objects"),
            codeProperties = dict(allowListExtension = False)))

        self.newOutput(VectorizedSocket("Color", "useObjectList",
            ("Color", "color"), ("Colors", "color")))

    def getExecutionFunctionName(self):
        if self.useObjectList:
            return "execute_LampColors"
        else:
            return "execute_LampColor"

    def execute_LampColor(self, object):
        if object is None: return Color((0, 0, 0, 0))
        color = object.data.color
        return Color(tuple([color[0], color[1], color[2], 0]))

    def execute_LampColors(self, objects):
        amount = len(objects)
        colors = ColorList(length = amount)
        for i, object in enumerate(objects):
            colors[i] = self.execute_LampColor(object)
        return colors
