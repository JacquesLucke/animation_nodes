import bpy
import bmesh
from ... events import isRendering
from ... base_types import AnimationNode
from ... utils.depsgraph import getActiveDepsgraph, getEvaluatedID

class BMeshFromObjectNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_BMeshFromObjectNode"
    bl_label = "BMesh from Object"

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Boolean", "Use World Space", "useWorldSpace", value = True)
        self.newInput("Boolean", "Use Deform Modifiers", "useDeformModifiers", value = False)
        self.newInput("Scene", "Scene", "scene", hide = True)
        self.newOutput("BMesh", "BMesh", "bm")

    def execute(self, object, useWorldSpace, useDeformModifiers, scene):
        bm = bmesh.new()
        if getattr(object, "type", "") != "MESH" or scene is None: return bm
        bm.from_object(object, getActiveDepsgraph(), deform = useDeformModifiers)
        if useWorldSpace:
            evaluatedObject = getEvaluatedID(object)
            bm.transform(evaluatedObject.matrix_world)
        return bm
