import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... algorithms.interpolation import *

class mn_MixInterpolation(Node, AnimationNode):
    bl_idname = "mn_MixInterpolation"
    bl_label = "Mix Interpolation"
    isDetermined = True
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_FloatSocket", "Factor").setMinMax(0, 1)
        self.inputs.new("mn_InterpolationSocket", "Interpolation 1").showName = False
        self.inputs.new("mn_InterpolationSocket", "Interpolation 2").showName = False
        self.outputs.new("mn_InterpolationSocket", "Interpolation")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Factor" : "factor", "Interpolation 1" : "a", "Interpolation 2" : "b"}
    def getOutputSocketNames(self):
        return {"Interpolation" : "interpolation"}
        
    def execute(self, factor, a, b):
        return (mixedInterpolation, (a, b, factor))
