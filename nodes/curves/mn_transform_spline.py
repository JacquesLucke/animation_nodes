import bpy, bmesh
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.curve import BezierPoint

class mn_TransformSpline(Node, AnimationNode):
    bl_idname = "mn_TransformSpline"
    bl_label = "Transform Spline"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_SplineSocket", "Spline")
        self.inputs.new("mn_MatrixSocket", "Transformation")
        self.outputs.new("mn_SplineSocket", "Spline")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        pass
        
    def getInputSocketNames(self):
        return {"Spline" : "spline",
                "Transformation" : "transformation"}
    def getOutputSocketNames(self):
        return {"Spline" : "spline"}
        
    def execute(self, spline, transformation):
        spline.transform(transformation)
        return spline