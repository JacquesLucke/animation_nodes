import bpy
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_MakeSplineCyclic(bpy.types.Node, AnimationNode):
    bl_idname = "mn_MakeSplineCyclic"
    bl_label = "Make Spline Cyclic"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_SplineSocket", "Spline").showName = False
        self.inputs.new("mn_BooleanSocket", "Cyclic").value = True
        self.outputs.new("mn_SplineSocket", "Spline")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Spline" : "spline",
                "Cyclic" : "cyclic"}

    def getOutputSocketNames(self):
        return {"Spline" : "spline"}

    def execute(self, spline, cyclic):
        spline.isCyclic = cyclic
        spline.isChanged = True
        return spline
