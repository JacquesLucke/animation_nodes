import bpy
from ... base_types import AnimationNode, VectorizedSocket

class ObjectViewportColorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectViewportColorNode"
    bl_label = "Object Viewport Color"
    codeEffects = [VectorizedSocket.CodeEffect]

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

    def getExecutionCode(self, required):
        return "newSpline = self.execute_object_color(object, color)"

    def execute_object_color(self, object, color):
        if object is None: return None
        object.color = color
        return object
