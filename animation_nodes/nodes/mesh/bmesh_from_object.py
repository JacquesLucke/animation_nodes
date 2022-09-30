import bpy
import bmesh
from ... base_types import AnimationNode
from ... utils.depsgraph import getActiveDepsgraph, getEvaluatedID

class BMeshFromObjectNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_BMeshFromObjectNode"
    bl_label = "BMesh from Object"

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Boolean", "Use World Space", "useWorldSpace", value = True)
        self.newOutput("BMesh", "BMesh", "bm")

    def execute(self, object, useWorldSpace):
        bm = bmesh.new()
        if getattr(object, "type", "") != "MESH": return bm
        bm.from_object(object, getActiveDepsgraph())
        if useWorldSpace:
            evaluatedObject = getEvaluatedID(object)
            bm.transform(evaluatedObject.matrix_world)
        return bm
