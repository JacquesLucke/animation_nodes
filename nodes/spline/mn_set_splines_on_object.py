import bpy
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.splines.to_blender import setSplinesOnBlenderObject

class mn_SetSplinesOnObject(bpy.types.Node, AnimationNode):
    bl_idname = "mn_SetSplinesOnObject"
    bl_label = "Set Splines on Object"
    
    def init(self, context):
        forbidCompiling()
        socket = self.inputs.new("mn_ObjectSocket", "Object")
        socket.showName = False
        socket.objectCreationType = "CURVE"
        self.inputs.new("mn_SplineListSocket", "Splines").showObjectInput = False
        self.outputs.new("mn_ObjectSocket", "Object")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Object" : "object",
                "Splines" : "splines"}

    def getOutputSocketNames(self):
        return {"Object" : "object"}

    def execute(self, object, splines):
        setSplinesOnBlenderObject(object, splines)
        return object
