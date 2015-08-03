import bpy
from ... base_types.node import AnimationNode

class ObjectAttributeOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectAttributeOutputNode"
    bl_label = "Object Attribute Output"

    inputNames = { "Object" : "object",
                   "Path" : "path",
                   "Value" : "value" }

    outputNames = { "Object" : "object" }

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object").showName = False
        self.inputs.new("an_StringSocket", "Path")
        self.inputs.new("an_GenericSocket", "Value")
        self.outputs.new("an_ObjectSocket", "Object")

    def execute(self, object, path, value):
        try:
            if path.startswith("["):
                exec("object" + path + "= value")
            else:
                exec("object." + path + "= value")
        except: pass
        return object
