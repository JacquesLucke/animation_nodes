import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_GetSplinePoints(Node, AnimationNode):
    bl_idname = "mn_GetSplinePoints"
    bl_label = "Get Spline Points"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_SplineSocket", "Spline").showName = False
        self.outputs.new("mn_VectorListSocket", "Points")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Spline" : "spline"}

    def getOutputSocketNames(self):
        return {"Points" : "points"}

    def execute(self, spline):
        return spline.getPoints()
