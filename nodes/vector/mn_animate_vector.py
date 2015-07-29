import bpy
from bpy.types import Node
from ... mn_cache import getUniformRandom
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... algorithms.interpolation import *
from mathutils import Vector

class mn_AnimateVectorNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_AnimateVectorNode"
    bl_label = "Animate Vector"
    outputUseParameterName = "useOutput"
    isDetermined = True
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_VectorSocket", "Start")
        self.inputs.new("mn_VectorSocket", "End")
        self.inputs.new("mn_FloatSocket", "Time")
        self.inputs.new("mn_InterpolationSocket", "Interpolation").showName = False
        self.inputs.new("mn_FloatSocket", "Duration").number = 20.0
        self.inputs.new("mn_FloatSocket", "Delay").number = 0.0
        self.outputs.new("mn_VectorSocket", "Current")
        self.outputs.new("mn_FloatSocket", "New Time")
        self.outputs.new("mn_VectorSocket", "Difference")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        pass
        
    def getInputSocketNames(self):
        return {"Start" : "start", "End" : "end", "Time" : "time", "Interpolation" : "interpolation", "Duration" : "duration", "Delay" : "delay"}
    def getOutputSocketNames(self):
        return {"Current" : "current", "New Time" : "newTime", "Difference" : "difference"}
        
    def execute(self, useOutput, start, end, time, interpolation, duration, delay):
        duration = max(duration, 0.0001)
        influence = interpolation[0](max(min(time / duration, 1.0), 0.0), interpolation[1])
        current = Vector((start[0] * (1 - influence) + end[0] * influence,
                    start[1] * (1 - influence) + end[1] * influence,
                    start[2] * (1 - influence) + end[2] * influence))
        difference = [0, 0, 0]
        if useOutput["Difference"]:
            influence = interpolation[0](max(min((time - 1) / duration, 1.0), 0.0), interpolation[1])
            oldVector = Vector((start[0] * (1 - influence) + end[0] * influence,
                        start[1] * (1 - influence) + end[1] * influence,
                        start[2] * (1 - influence) + end[2] * influence))
            difference = current - oldVector
        return current, time - duration - delay, difference
        
