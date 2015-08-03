import bpy, random
from ... mn_cache import getUniformRandom
from ... base_types.node import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_CopyObjectData(bpy.types.Node, AnimationNode):
    bl_idname = "mn_CopyObjectData"
    bl_label = "Copy Object Data"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ObjectSocket", "From")
        self.inputs.new("mn_ObjectSocket", "To")
        self.outputs.new("mn_ObjectSocket", "To")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"From" : "fromObject", "To" : "toObject"}
    def getOutputSocketNames(self):
        return {"To" : "toObject"}
        
    def execute(self, fromObject, toObject):
        if fromObject is not None and toObject is not None:
            if toObject.data != fromObject.data:
                if toObject.type == fromObject.type:
                    toObject.data = fromObject.data
        return toObject
        
