import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_SplineInfo(Node, AnimationNode):
    bl_idname = "mn_SplineInfo"
    bl_label = "Spline Info"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_SplineSocket", "Spline").showName = False
        self.outputs.new("mn_VectorListSocket", "Points")
        self.outputs.new("mn_BooleanSocket", "Cyclic")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Spline" : "spline"}

    def getOutputSocketNames(self):
        return {"Points" : "points",
                "Cyclic" : "cyclic"}

    def execute(self, spline):
        spline.update()
        return spline.getPoints(), spline.isCyclic
