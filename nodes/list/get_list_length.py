import bpy
from ... base_types.node import AnimationNode

class GetListLengthNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetListLengthNode"
    bl_label = "Get List Length"
    
    inputNames = { "List" : "list" }
    outputNames = { "Length" : "length" }
    
    def create(self):
        self.inputs.new("an_GenericSocket", "List")
        self.outputs.new("an_IntegerSocket", "Length")
        
    def getExecutionCode(self):
        return ("try: $length$ = len(%list%) \n"
                "except: $length$ = 0")
