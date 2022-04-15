import bpy
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import Color, ColorList, DoubleList

class LampInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_LampInputNode"
    bl_label = "Lamp Input"

    useObjectList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Object", "useObjectList",
            ("Object", "object", dict(defaultDrawType = "PROPERTY_ONLY")),
            ("Objects", "objects")))

        self.newOutput(VectorizedSocket("Color", "useObjectList",
            ("Color", "color"), ("Colors", "colors")))
        self.newOutput(VectorizedSocket("Float", "useObjectList",
            ("Energy", "energy"), ("Energies", "energies")))

    def getExecutionFunctionName(self):
        if self.useObjectList:
            return "execute_List"
        else:
            return "execute_Single"

    def execute_Single(self, object):
        if object is None or object.type != 'LIGHT': return Color((0, 0, 0, 0)), 0
        color = object.data.color
        return Color(tuple([color[0], color[1], color[2], 0])), object.data.energy

    def execute_List(self, objects):
        amount = len(objects)
        colors = ColorList(length = amount)
        energies = DoubleList(length = amount)
        for i, object in enumerate(objects):
            colors[i], energies[i] = self.execute_Single(object)
        return colors, energies
