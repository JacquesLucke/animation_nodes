import bpy
from bpy.types import Node
from mathutils import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling


class mn_ComposeMatrix(Node, AnimationNode):
    bl_idname = "mn_ComposeMatrix"
    bl_label = "Compose Matrix"
    isDetermined = True
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_VectorSocket", "Position")
        self.inputs.new("mn_VectorSocket", "Rotation")
        self.inputs.new("mn_VectorSocket", "Scale").vector = [1, 1, 1]
        self.outputs.new("mn_MatrixSocket", "Matrix")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Position" : "position",
                "Rotation" : "rotation",
                "Scale" : "scale"}
    def getOutputSocketNames(self):
        return {"Matrix" : "matrix"}

    def useInLineExecution(self):
        return True
    def getInLineExecutionString(self, outputUse):
        return "$matrix$ = animation_nodes.utils.math.composeMatrix(%position%, %rotation%, %scale%)"
        
    def getModuleList(self):
        return []
