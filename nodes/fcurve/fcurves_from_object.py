import bpy
from ... base_types.node import AnimationNode

class FCurvesFromObjectNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FCurvesFromObjectNode"
    bl_label = "FCurves from Object"

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.outputs.new("an_FCurveListSocket", "FCurves", "fCurves")

    def execute(self, object):
        try: return list(object.animation_data.action.fcurves)
        except: return []
