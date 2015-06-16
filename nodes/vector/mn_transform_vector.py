import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodeTreeChanged, allowCompiling, forbidCompiling

class mn_TransformVector(Node, AnimationNode):
    bl_idname = "mn_TransformVector"
    bl_label = "Transform Vector"
    isDetermined = True
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_VectorSocket", "Vector")
        self.inputs.new("mn_MatrixSocket", "Matrix")
        self.outputs.new("mn_VectorSocket", "Vector")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Vector" : "vector", "Matrix" : "matrix"}
    def getOutputSocketNames(self):
        return {"Vector" : "vector"}
        
    def useInLineExecution(self):
        return True
    def getInLineExecutionString(self, outputUse):
        return "$vector$ = %matrix% * mathutils.Vector(%vector%)"
    def getModuleList(self):
        return ["mathutils"]

