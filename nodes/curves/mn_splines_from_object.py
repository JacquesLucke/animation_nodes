import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.curve import getSplinesFromBlenderCurveData

class mn_SplinesFromObject(Node, AnimationNode):
    bl_idname = "mn_SplinesFromObject"
    bl_label = "Splines from Object"
    
    useWorldSpace = bpy.props.BoolProperty(name = "Use World Space", description = "Transform curve to world space", update = nodePropertyChanged)

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ObjectSocket", "Object").showName = False
        self.outputs.new("mn_SplineListSocket", "Splines")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "useWorldSpace")

    def getInputSocketNames(self):
        return {"Object" : "object"}

    def getOutputSocketNames(self):
        return {"Splines" : "splines"}

    def execute(self, object):
        if getattr(object, "type", "") != "CURVE":
            return []
            
        splines = getSplinesFromBlenderCurveData(object.data)
        if self.useWorldSpace:
            for spline in splines:
                spline.transform(object.matrix_world)
        return splines