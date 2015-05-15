import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.curve import *

class mn_BezierPointInfo(Node, AnimationNode):
    bl_idname = "mn_BezierPointInfo"
    bl_label = "Bezier Point Info"

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_BezierPointSocket", "Bezier Point")
        self.outputs.new("mn_VectorSocket", "Location")
        self.outputs.new("mn_VectorSocket", "Left Handle")
        self.outputs.new("mn_VectorSocket", "Right Handle")
        allowCompiling()

    def getInputSocketNames(self):
        return {"Bezier Point" : "point"}

    def getOutputSocketNames(self):
        return {"Location" : "location",
                "Left Handle" : "leftHandle", 
                "Right Handle" : "rightHandle"}

    def execute(self, point):
        return point.location, point.leftHandle, point.rightHandle
