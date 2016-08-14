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
        self.newInput("Boolean", "Clamp input", "clamp", value = True)
        self.newInput("Float", "Input Min", "imin", value = 0)
        self.newInput("Float", "Input Max", "imax", value = 1)
        self.newInput("Float", "Output Min", "omin", value = 0)
        self.newInput("Float", "Output Max", "omax", value = 1)
        self.newInput("Float", "Size", "size", value = 10.0)
        self.newInput("Float", "Offset", "offset", value = 0.0)
        self.newOutput("Float", "Value", "output")
    
    def getExecutionCode(self):
        yield "output = self.rampInOut(input, imin, imax, omin, omax, clamp, size, offset)"
           
    def rampInOut(self, input, imin, imax, omin, omax, clamp, size, offset):
        no, ns = offset / 100, size / 100
        delta_i = imax-imin
        delta_o = omax-omin
        icur = input
        if clamp:
            if input > imax:
                icur = imax
            if input < imin:
                icur = imin
        normalized_i = icur / delta_i
        if no > 0.5:
            no = 0.5        
        limit = 0.5 - no
        ramp = (limit - abs(normalized_i - 0.5)) / ns 
        return omin + ramp * delta_o
