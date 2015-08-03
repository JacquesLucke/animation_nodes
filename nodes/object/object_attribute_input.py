import bpy
from ... base_types.node import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_ObjectAttributeInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_ObjectAttributeInputNode"
    bl_label = "Object Attribute Input"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ObjectSocket", "Object").showName = False
        self.inputs.new("mn_StringSocket", "Attribute").value = ""
        self.outputs.new("mn_GenericSocket", "Value")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Object" : "object",
                "Attribute" : "attribute"}
    def getOutputSocketNames(self):
        return {"Value" : "value"}
        
    def execute(self, object, attribute):
        try:
            if attribute.startswith("["):
                return eval("object" + attribute)
            else:
                return eval("object." + attribute)
        except:
            return None
