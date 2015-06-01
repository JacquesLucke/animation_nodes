import bpy
import math
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

class mn_Math3DCoordinatesCartesianToCylindrical(Node, AnimationNode):
    bl_idname = "mn_Math3DCoordinatesCartesianToCylindrical"
    bl_label = "Cartesian To Cylindrical"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_FloatSocket", "X")
        self.inputs.new("mn_FloatSocket", "Y")
        self.inputs.new("mn_FloatSocket", "Z")
        self.outputs.new("mn_FloatSocket", "Radius")
        self.outputs.new("mn_FloatSocket", "Azimuth")
        self.outputs.new("mn_FloatSocket", "Z")
        allowCompiling()

    def getInputSocketNames(self):
        return {"X" : "x",
                "Y" : "y",
                "Z" : "z"}

    def getOutputSocketNames(self):
        return {"Radius" : "radius",
                "Azimuth" : "azimuth",
                "Z" : "zOut"}

    def execute(self, x, y, z):
        radius = 0.0
        azimuth = 0.0
        
        try:
            radius = math.sqrt(x*x + y*y)
            azimuth = math.atan2(y, x)  # in range [-pi .. pi]
        except: pass
        
        return radius, azimuth, z

