import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... base_types.node import AnimationNode

class FloatMapRampInOutNode(bpy.types.Node, AnimationNode):
    """
        map float on a ramp in out range
        input:
        
          /
         /
        /
        
        output:
         _
        / \
        
    """
    bl_idname = "an_FloatMapRampInOutNode"
    bl_label = "Map Ramp In-Out"
    bl_width_default = 170

    def settingChanged(self, context):
        self.recreateInputs()
        
    clampInput = BoolProperty(name = "Clamp Input", default = True,
        description = "The input will be between Input Min and Input Max",
        update = settingChanged)
     
    useInterpolation = BoolProperty(name = "Use Interpolation", default = False,
        description = "Don't use the normal linear interpolation between Min and Max",
        update = settingChanged)
    
    def create(self):
        self.recreateInputs()
        self.newOutput("Float", "Value", "newValue")
        
    @keepNodeState
    def recreateInputs(self):
        self.inputs.clear()
        self.newInput("Float", "Value", "value", value = 0)
        self.newInput("Float", "Input Min", "inMin", value = 0)
        self.newInput("Float", "Input Max", "inMax", value = 1)
        self.newInput("Float", "Output Min", "outMin", value = 0)
        self.newInput("Float", "Output Max", "outMax", value = 1)
        self.newInput("Float", "Size", "size", value = 0.1)
        self.newInput("Float", "Offset", "offset", value = 0.0)
        if self.useInterpolation:
            self.newInput("Interpolation", "Interpolation", "interpolation", defaultDrawType = "PROPERTY_ONLY")
    
    def draw(self, layout):
        col = layout.column(align = True)
        col.prop(self, "useInterpolation")   
        col.prop(self, "clampInput")   
    
    def getExecutionCode(self):
        yield "if inMin == inMax or size == 0: newValue = 0"
        yield "else:"
        yield "    x = ((0.5 - min(offset, 0.5)) - abs(((value - inMin) / (inMax - inMin)) - 0.5)) / size"
        if self.clampInput:
            yield "    x = max(0.0, min(x, 1.0))"
        yield "    if 0 < x < 1:"
        if self.useInterpolation:
            yield "        newValue = outMin + interpolation(x) * (outMax - outMin)"
        else:
            yield "        newValue = outMin + x * (outMax - outMin)"
        yield "    else:"
        yield "        newValue = outMin + x * (outMax - outMin)"
