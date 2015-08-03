import bpy
from ... base_types.node import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_TransformSpline(bpy.types.Node, AnimationNode):
    bl_idname = "mn_TransformSpline"
    bl_label = "Transform Spline"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_SplineSocket", "Spline").showName = False
        self.inputs.new("mn_MatrixSocket", "Transformation")
        self.outputs.new("mn_SplineSocket", "Spline")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Spline" : "spline",
                "Transformation" : "transformation"}

    def getOutputSocketNames(self):
        return {"Spline" : "spline"}

    def execute(self, spline, transformation):
        spline.transform(transformation)
        spline.isChanged = True
        return spline
