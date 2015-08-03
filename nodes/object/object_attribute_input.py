import bpy
from ... base_types.node import AnimationNode

class ObjectAttributeInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_ObjectAttributeInputNode"
    bl_label = "Object Attribute Input"

    inputNames = { "Object" : "object",
                   "Path" : "path"}

    outputNames = { "Value" : "value" }

    def create(self):
        self.inputs.new("mn_ObjectSocket", "Object").showName = False
        self.inputs.new("mn_StringSocket", "Path")
        self.outputs.new("mn_GenericSocket", "Value")

    def execute(self, object, path):
        try:
            if path.startswith("["):
                return eval("object" + path)
            else:
                return eval("object." + path)
        except:
            return None
