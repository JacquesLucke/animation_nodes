import bpy
from bpy.props import *
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
    
    def create(self):
        self.newInput("Float", "Value", "input", value = 0)
        self.newInput("Boolean", "Clamp", "clamp", value = True)
        self.newInput("Float", "Input Min", "imin", value = 0)
        self.newInput("Float", "Input Max", "imax", value = 1)
        self.newInput("Float", "Output Min", "omin", value = 0)
        self.newInput("Float", "Output Max", "omax", value = 1)
        self.newInput("Float", "Size", "size", value = 0.1)
        self.newInput("Float", "Offset", "offset", value = 0.0)
        self.newOutput("Float", "Value", "output")
    
    def getExecutionCode(self):
        yield "self.errorMessage = self.rampInOutValidInput(imin, imax, size)"
        yield "if self.errorMessage == '':"
        yield "    output = self.rampInOut(input, imin, imax, omin, omax, clamp, size, offset)"
        yield "else:"
        yield "    output = input"
    
    def rampInOutValidInput(self, imin, imax, size):
        if imin == imax:
            return 'Expected Input Min different from Input Max'
        if size == 0.0:
            return 'Expected Size greater than 0'
        return ''
        
    def rampInOut(self, input, imin, imax, omin, omax, clamp, size, offset):
        delta_i = imax-imin
        delta_o = omax-omin
        offset = min(offset, 0.5)
        interval_input = abs((input / delta_i) - 0.5)
        interval_ramp = 0.5 - offset
        ramp = (interval_ramp - interval_input) / size
        if interval_input < interval_ramp or clamp:
            ramp = max(0.0, min(ramp, 1.0))
        return omin + ramp * delta_o
