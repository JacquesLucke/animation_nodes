import bpy
from bpy.types import Node
from ... mn_cache import getUniformRandom
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... utils.mn_interpolation_utils import *

class mn_AnimateMatrixNode(Node, AnimationNode):
    bl_idname = "mn_AnimateMatrixNode"
    bl_label = "Animate Matrix"
    isDetermined = True
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_MatrixSocket", "Start")
        self.inputs.new("mn_MatrixSocket", "End")
        self.inputs.new("mn_FloatSocket", "Time")
        self.inputs.new("mn_InterpolationSocket", "Interpolation").showName = False
        self.inputs.new("mn_FloatSocket", "Duration").number = 20.0
        self.inputs.new("mn_FloatSocket", "Delay").number = 0.0
        self.outputs.new("mn_MatrixSocket", "Current")
        self.outputs.new("mn_FloatSocket", "New Time")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Start" : "start", "End" : "end", "Time" : "time", "Interpolation" : "interpolation", "Duration" : "duration", "Delay" : "delay"}
    def getOutputSocketNames(self):
        return {"Current" : "current", "New Time" : "newTime"}
        
    def execute(self, start, end, time, interpolation, duration, delay):
        duration = max(duration, 0.0001)
        influence = interpolation[0](max(min(time / duration, 1.0), 0.0), interpolation[1])
        current = start.lerp(end, influence)
        return current, time - duration - delay
        
