import bpy
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.splines.operations import connectSplines

class mn_ConnectSplines(bpy.types.Node, AnimationNode):
    bl_idname = "mn_ConnectSplines"
    bl_label = "Connect Splines"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_SplineListSocket", "Splines").showName = False
        self.outputs.new("mn_SplineSocket", "Spline")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Splines" : "splines"}

    def getOutputSocketNames(self):
        return {"Spline" : "spline"}

    def execute(self, splines):
        return connectSplines(splines)
