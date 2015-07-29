import bpy
from ... base_types.node import AnimationNode

class ConditionNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_ConditionNode"
    bl_label = "Condition"
    
    def create(self):
        self.inputs.new("mn_BooleanSocket", "Condition")
        self.inputs.new("mn_GenericSocket", "If True")
        self.inputs.new("mn_GenericSocket", "If False")
        self.outputs.new("mn_GenericSocket", "Output")
        self.outputs.new("mn_GenericSocket", "Other")
        
    def getInputSocketNames(self):
        return {"Condition" : "condition",
                "If True" : "ifTrue",
                "If False" : "ifFalse"}
                
    def getOutputSocketNames(self):
        return {"Output" : "output",
                "Other" : "other"}
        
    def useInLineExecution(self):
        return True
    def getInLineExecutionString(self, outputUse):
        return "$output$ = %ifTrue% if %condition% else %ifFalse%\n" + \
            "$other$ = %ifFalse% if %condition% else %ifTrue%"
