import bpy
from ... base_types.node import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_GetListLengthNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_GetListLengthNode"
    bl_label = "Get List Length"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_GenericSocket", "List")
        self.outputs.new("mn_IntegerSocket", "Length")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"List" : "list"}
    def getOutputSocketNames(self):
        return {"Length" : "length"}
        
    def useInLineExecution(self):
        return True
    def getInLineExecutionString(self, outputUse):
        return """
try: $length$ = len(%list%)
except: $length$ = 0 """
