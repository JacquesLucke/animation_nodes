import bpy
from ... base_types.node import AnimationNode

class ConditionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConditionNode"
    bl_label = "Condition"
    
    inputNames = { "Condition" : "condition",
                   "If True" : "ifTrue",
                   "If False" : "ifFalse" }
                   
    outputNames = { "Output" : "output",
                    "Other" : "other" }                  
    
    def create(self):
        self.inputs.new("an_BooleanSocket", "Condition")
        self.inputs.new("an_GenericSocket", "If True")
        self.inputs.new("an_GenericSocket", "If False")
        self.outputs.new("an_GenericSocket", "Output")
        self.outputs.new("an_GenericSocket", "Other")
        
    def getExecutionCode(self):
        return "$output$ = %ifTrue% if %condition% else %ifFalse%" + "\n" + \
               "$other$ = %ifFalse% if %condition% else %ifTrue%"