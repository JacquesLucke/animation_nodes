import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.splines.from_blender import createSplinesFromBlenderObject

class mn_SplinesFromObject(Node, AnimationNode):
    bl_idname = "mn_SplinesFromObject"
    bl_label = "Splines from Object"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ObjectSocket", "Object").showName = False
        self.outputs.new("mn_SplineListSocket", "Splines")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Object" : "object"}

    def getOutputSocketNames(self):
        return {"Splines" : "splines"}

    def execute(self, object):
        splines = createSplinesFromBlenderObject(object)
        return splines
