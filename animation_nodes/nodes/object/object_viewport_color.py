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
            ("Objects", "objects"),
            codeProperties = dict(allowListExtension = False)))

        self.newInput(VectorizedSocket("Color", "useColorList",
            ("Color", "color"), ("Colors", "colors")))

        self.newOutput(VectorizedSocket("Object", "useObjectList",
            ("Object", "object", dict(defaultDrawType = "PROPERTY_ONLY")),
            ("Objects", "objects")))

    def getExecutionCode(self, required):
        return "if object is not None: object.color = color"
