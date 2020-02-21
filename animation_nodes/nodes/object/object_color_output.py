import bpy
from ... data_structures import Color, VirtualColorList
from ... base_types import AnimationNode, VectorizedSocket

class ObjectViewportColorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectViewportColorNode"
    bl_label = "Object Viewport Color"

    useObjectList: VectorizedSocket.newProperty()
    useColorList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Object", "useObjectList",
            ("Object", "object", dict(defaultDrawType = "PROPERTY_ONLY")),
            ("Objects", "objects")))

        self.newInput(VectorizedSocket("Color", ["useObjectList", "useColorList"],
            ("Color", "color"), ("Colors", "colors")))

        self.newOutput(VectorizedSocket("Object", "useObjectList",
            ("Object", "object", dict(defaultDrawType = "PROPERTY_ONLY")),
            ("Objects", "objects")))

    def getExecutionFunctionName(self):
        if self.useObjectList:
            if self.useColorList:
                return "execute_Objects_ColorsList"
            else:
                return "execute_Objects_SingleColor"
        else:
            return "execute_Object_Color"

    def execute_Object_Color(self, object, color):
        if object is None: return None
        object.color = color
        return object

    def execute_Objects_SingleColor(self, objects, color):
        amount = len(objects)
        if amount == 0: return objects
        colors = VirtualColorList.create(color, Color((1, 1, 1, 1)))
        for i, object in enumerate(objects):
            if object is None: pass
            object.color = colors[i]
        return objects

    def execute_Objects_ColorsList(self, objects, colors):
        amount = len(objects)
        if amount == 0 or len(colors) == 0: return objects
        colors = VirtualColorList.create(colors, Color((1, 1, 1, 1)))
        for i, object in enumerate(objects):
            if object is None: pass
            object.color = colors[i]
        return objects
