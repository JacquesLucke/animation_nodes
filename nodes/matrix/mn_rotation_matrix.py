import bpy
from bpy.types import Node
from mathutils import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

axisItems = [("X", "X", ""), ("Y", "Y", ""), ("Z", "Z", "")]

class mn_RotationMatrix(bpy.types.Node, AnimationNode):
    bl_idname = "mn_RotationMatrix"
    bl_label = "Rotation Matrix"
    isDetermined = True
    
    axis = bpy.props.EnumProperty(items = axisItems, update = nodeTreeChanged)
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_FloatSocket", "Angle")
        self.outputs.new("mn_MatrixSocket", "Matrix")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "axis", expand = True)
        
    def getInputSocketNames(self):
        return {"Angle" : "angle"}
    def getOutputSocketNames(self):
        return {"Matrix" : "matrix"}

    def useInLineExecution(self):
        return True
    def getInLineExecutionString(self, outputUse):
        return "$matrix$ = mathutils.Matrix.Rotation(%angle%, 4, '"+ self.axis +"')"
        
    def getModuleList(self):
        return ["mathutils"]
        
    def copy(self, node):
        self.inputs[0].number = 0
