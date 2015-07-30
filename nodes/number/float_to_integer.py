import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... events import executionCodeChanged

items = [("ROUND", "Round", ""),
         ("CEILING", "Ceiling", "The smallest integer that is larger than the input (4.3 -> 5)"),
         ("FLOOR", "Floor", "The largest integer that is smaller than the input (5.8 -> 5)")]

class FloatToInteger(bpy.types.Node, AnimationNode):
    bl_idname = "mn_FloatToInteger"
    bl_label = "Float To Integer"
    isDetermined = True
    
    inputNames = { "Float" : "float" }
    outputNames = { "Integer" : "integer" }
    
    type = EnumProperty(name = "Conversion Type", items = items, default = "FLOOR", update = executionCodeChanged)
    
    def create(self):
        self.inputs.new("mn_FloatSocket", "Float")
        self.outputs.new("mn_IntegerSocket", "Integer")
        
    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "type", text = "")

    def getExecutionCode(self):
        if self.type == "ROUND": return "$integer$ = int(round(%float%))"
        if self.type == "CEILING": return "$integer$ = int(math.ceil(%float%))"
        if self.type == "FLOOR": return "$integer$ = int(math.floor(%float%))"
        
    def getModuleList(self):
        return ["math"]