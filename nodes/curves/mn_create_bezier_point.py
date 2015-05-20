import bpy, bmesh
from bpy.types import Node
from bpy.props import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.curve import BezierPoint

class mn_CreateBezierPoint(Node, AnimationNode):
    bl_idname = "mn_CreateBezierPoint"
    bl_label = "Create Bezier Point"
    
    def settingChanged(self, context):
        self.inputs["Left Handle"].hide = not self.customHandles
        self.inputs["Right Handle"].hide = not self.customHandles
        nodePropertyChanged(self, context)
    
    customHandles = BoolProperty(name = "Custom Handles", default = False, update = settingChanged)
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_VectorSocket", "Location").showObjectInput = False
        self.inputs.new("mn_VectorSocket", "Left Handle")
        self.inputs.new("mn_VectorSocket", "Right Handle")
        self.outputs.new("mn_BezierPointSocket", "Bezier Point")
        self.settingChanged(context)
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "customHandles")
        
    def getInputSocketNames(self):
        return {"Location" : "location",
                "Left Handle" : "leftHandle",
                "Right Handle" : "rightHandle"}
    def getOutputSocketNames(self):
        return {"Bezier Point" : "point"}
        
    def execute(self, location, leftHandle, rightHandle):
        point = BezierPoint()
        point.location = location
        if self.customHandles:
            point.leftHandle = leftHandle
            point.rightHandle = rightHandle
        else:
            point.leftHandle = location.copy()
            point.rightHandle = location.copy()
        return point