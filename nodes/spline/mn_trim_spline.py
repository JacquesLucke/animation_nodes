import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_TrimSpline(Node, AnimationNode):
    bl_idname = "mn_TrimSpline"
    bl_label = "Trim Spline"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_SplineSocket", "Spline").showName = False
        self.inputs.new("mn_FloatSocket", "Start").number = 0.0
        self.inputs.new("mn_FloatSocket", "End").number = 1.0
        self.outputs.new("mn_SplineSocket", "Spline")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Spline" : "spline",
                "Start" : "start",
                "End" : "end"}

    def getOutputSocketNames(self):
        return {"Spline" : "spline"}

    def execute(self, spline, start, end):
        spline.update()
        return spline.getTrimmedVersion(start, end)
