import bpy
import math
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

# http://en.wikipedia.org/wiki/Polar_coordinate_system
class mn_Math3DCoordinatesCylindricalToCartesian(Node, AnimationNode):
    bl_idname = "mn_Math3DCoordinatesCylindricalToCartesian"
    bl_label = "Cylindrical To Cartesian"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_FloatSocket", "Radius")
        self.inputs.new("mn_FloatSocket", "Azimuth")
        self.inputs.new("mn_FloatSocket", "Z")
        self.outputs.new("mn_FloatSocket", "X")
        self.outputs.new("mn_FloatSocket", "Y")
        self.outputs.new("mn_FloatSocket", "Z")
        allowCompiling()

    def getInputSocketNames(self):
        return {"Radius" : "radius",
                "Azimuth" : "azimuth",
                "Z" : "z"}

    def getOutputSocketNames(self):
        return {"X" : "x",
                "Y" : "y",
                "Z" : "zOut"}

    def execute(self, radius, azimuth, z):
        x = 0.0
        y = 0.0
        
        try:
            x = math.cos(azimuth) * radius
            y = math.sin(azimuth) * radius
        except: pass
        
        return x, y, z

