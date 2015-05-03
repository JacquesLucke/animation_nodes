import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_SeparateVector(Node, AnimationNode):
    bl_idname = "mn_SeparateVector"
    bl_label = "Separate Vector"
    isDetermined = True
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_VectorSocket", "Vector")
        self.outputs.new("mn_FloatSocket", "X")
        self.outputs.new("mn_FloatSocket", "Y")
        self.outputs.new("mn_FloatSocket", "Z")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Vector" : "vector"}
    def getOutputSocketNames(self):
        return {"X" : "x",
                "Y" : "y",
                "Z" : "z"}
        
    def execute(self, vector):
        return vector[0], vector[1], vector[2]
