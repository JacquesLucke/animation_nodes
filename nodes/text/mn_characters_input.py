import bpy
from ... base_types.node import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_CharactersNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_CharactersNode"
    bl_label = "Characters"
    
    def init(self, context):
        forbidCompiling()
        self.outputs.new("mn_StringSocket", "Lower Case")
        self.outputs.new("mn_StringSocket", "Upper Case")
        self.outputs.new("mn_StringSocket", "Digits")
        self.outputs.new("mn_StringSocket", "Special")
        self.outputs.new("mn_StringSocket", "All")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {}
    def getOutputSocketNames(self):
        return {"Lower Case" : "lower",
                "Upper Case" : "upper",
                "Digits" : "digits",
                "Special" : "special",
                "All" : "all"}
        
    def execute(self):
        lower = "abcdefghijklmnopqrstuvwxyz"
        upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        digits = "0123456789"
        special = "!$%&/()=?*+#'-_.:,;" + '"'
        all = lower + upper + digits + special
        return lower, upper, digits, special, all
