import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

class mn_CombineVector(bpy.types.Node, AnimationNode):
    bl_idname = "mn_CombineVector"
    bl_label = "Combine Vector"
    isDetermined = True
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_FloatSocket", "X")
        self.inputs.new("mn_FloatSocket", "Y")
        self.inputs.new("mn_FloatSocket", "Z")
        self.outputs.new("mn_VectorSocket", "Vector")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"X" : "x",
                "Y" : "y",
                "Z" : "z"}
    def getOutputSocketNames(self):
        return {"Vector" : "vector"}

    def useInLineExecution(self):
        return True
    def getInLineExecutionString(self, outputUse):
        return "$vector$ = mathutils.Vector((%x%, %y%, %z%))"
    def getModuleList(self):
        return ["mathutils"]
