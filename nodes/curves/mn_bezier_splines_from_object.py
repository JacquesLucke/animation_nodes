import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.curve import *

class mn_BezierSplinesFromObject(Node, AnimationNode):
    bl_idname = "mn_BezierSplinesFromObject"
    bl_label = "Bezier Splines from Object"
    
    useWorldSpace = bpy.props.BoolProperty(name = "Use World Space", description = "Transform curve to world space", update = nodePropertyChanged)

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ObjectSocket", "Object").showName = False
        self.outputs.new("mn_BezierSplineListSocket", "Bezier Splines")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "useWorldSpace")

    def getInputSocketNames(self):
        return {"Object" : "object"}

    def getOutputSocketNames(self):
        return {"Bezier Splines" : "bezierSplines"}

    def execute(self, object):
        if getattr(object, "type", "") != "CURVE":
            return []
            
        splines = BezierSpline.fromBlenderCurveData(object.data)
        if self.useWorldSpace:
            for spline in splines:
                spline.transform(object.matrix_world)
        return splines