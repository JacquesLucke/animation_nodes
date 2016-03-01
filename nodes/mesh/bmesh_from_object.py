import bpy
import bmesh
from ... events import isRendering
from ... base_types.node import AnimationNode

class BMeshFromObjectNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_BMeshFromObjectNode"
    bl_label = "BMesh from Object"

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.inputs.new("an_BooleanSocket", "Use World Space", "useWorldSpace").value = True
        self.inputs.new("an_SceneSocket", "Scene", "scene").hide = True
        self.outputs.new("an_BMeshSocket", "BMesh", "bm")

    def execute(self, object, useWorldSpace, scene):
        bm = bmesh.new()
        if getattr(object, "type", "") != "MESH" or scene is None: return bm
        # Seems like the deform and render parameters don't work..
        bm.from_object(object, scene, deform = True, render = False)
        if useWorldSpace: bm.transform(object.matrix_world)
        return bm
