import bpy
from bpy.types import Node
from mathutils import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling


class mn_ScaleMatrix(bpy.types.Node, AnimationNode):
    bl_idname = "mn_ScaleMatrix"
    bl_label = "Scale Matrix"
    isDetermined = True
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_VectorSocket", "Scale").vector = [1, 1, 1]
        self.outputs.new("mn_MatrixSocket", "Matrix")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Scale" : "scale"}
    def getOutputSocketNames(self):
        return {"Matrix" : "matrix"}

    def useInLineExecution(self):
        return True
    def getInLineExecutionString(self, outputUse):
        return "$matrix$ = mathutils.Matrix.Scale(%scale%[0], 4, [1, 0, 0]) * mathutils.Matrix.Scale(%scale%[1], 4, [0, 1, 0]) * mathutils.Matrix.Scale(%scale%[2], 4, [0, 0, 1])"
        
    def getModuleList(self):
        return ["mathutils"]
        
    def copy(self, node):
        self.inputs[0].vector = [1, 1, 1]
