import bpy
from ... base_types import AnimationNode, VectorizedSocket

class EvaluateObjectNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_EvaluateObjectNode"
    bl_label = "Evaluate Object"

    useObjectList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Object", "useObjectList",
            ("Object", "object", dict(defaultDrawType = "PROPERTY_ONLY")),
            ("Objects", "objects")))
        self.newOutput(VectorizedSocket("Object", "useObjectList",
            ("Object", "object"),
            ("Objects", "objects")))

    def getExecutionCode(self, required):
        yield "AN.utils.depsgraph.getActiveDepsgraph().update()"
