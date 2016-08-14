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
        self.newInput("Float", "Input", "input", value = 0)
        self.newInput("Float", "Input min", "imin", value = 0)
        self.newInput("Float", "Input max", "imax", value = 1)
        self.newInput("Float", "Output min", "omin", value = 0)
        self.newInput("Float", "Output max", "omax", value = 1)
        self.newInput("Boolean", "clamp", "clamp", value = True)
        self.newInput("Float", "Ramp size %", "size", value = 10.0)
        self.newInput("Float", "Offset % (+ = interior)", "offset", value = 0.0)
        self.newOutput("Float", "Output", "output")
    
    def getExecutionCode(self):
        yield "output = self.rampInOut(input, imin, imax, omin, omax, clamp, size, offset)"
           
    def rampInOut(self, input, imin, imax, omin, omax, clamp, size, offset):
        no, ns = offset / 100, size / 100
        di = imax-imin
        do = omax-omin
        icur = input
        if clamp:
            if input > imax:
                icur = imax
            if input < imin:
                icur = imin
        ni = icur / di
        if no > 0.5:
            no = 0.5        
        limit = 0.5 - no
        ramp = (limit - abs(ni - 0.5)) / ns 
        return omin + ramp * do
