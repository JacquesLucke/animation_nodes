import bpy
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

class mn_VectorFromValue(bpy.types.Node, AnimationNode):
    bl_idname = "mn_VectorFromValue"
    bl_label = "Vector from Value"
    node_category = "Math"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_FloatSocket", "Value")
        self.outputs.new("mn_VectorSocket", "Vector")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Value" : "value"}
    def getOutputSocketNames(self):
        return {"Vector" : "vector"}

    def useInLineExecution(self):
        return True
    def getInLineExecutionString(self, outputUse):
        return "$vector$ = mathutils.Vector((%value%, %value%, %value%))"
    def getModuleList(self):
        return ["mathutils"]
