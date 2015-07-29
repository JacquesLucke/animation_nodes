import bpy
import mathutils
from ... base_types.node import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_VectorLengthNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_VectorLengthNode"
    bl_label = "Vector Length"
    isDetermined = True
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_VectorSocket", "Vector")
        self.outputs.new("mn_FloatSocket", "Length")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Vector" : "vector"}
    def getOutputSocketNames(self):
        return {"Length" : "length"}
        
    def execute(self, vector):
        return vector.length
