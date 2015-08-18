import bpy
from ... base_types.node import AnimationNode

class ObjectAttributeInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectAttributeInputNode"
    bl_label = "Object Attribute Input"

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object", "object").showName = False
        self.inputs.new("an_StringSocket", "Path", "path")
        self.outputs.new("an_GenericSocket", "Value", "value")

    def execute(self, object, path):
        try:
            if path.startswith("["):
                return eval("object" + path)
            else:
                return eval("object." + path)
        except:
            return None
