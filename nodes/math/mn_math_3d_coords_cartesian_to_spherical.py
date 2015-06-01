import bpy
import math
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

class mn_Math3DCoordinatesCartesianToSpherical(Node, AnimationNode):
    bl_idname = "mn_Math3DCoordinatesCartesianToSpherical"
    bl_label = "Cartesian To Spherical"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_FloatSocket", "X")
        self.inputs.new("mn_FloatSocket", "Y")
        self.inputs.new("mn_FloatSocket", "Z")
        self.outputs.new("mn_FloatSocket", "Radius")
        self.outputs.new("mn_FloatSocket", "Azimuth")       # in [-pi .. pi]
        self.outputs.new("mn_FloatSocket", "Elevation")     # in [-pi/2 .. pi/2]
        allowCompiling()

    def getInputSocketNames(self):
        return {"X" : "x",
                "Y" : "y",
                "Z" : "z"}

    def getOutputSocketNames(self):
        return {"Radius" : "radius",
                "Azimuth" : "azimuth",
                "Elevation" : "elevation"}

    def execute(self, x, y, z):
        radius = 0.0
        azimuth = 0.0
        elevation = 0.0
        
        try:
            radius = math.sqrt(x*x + y*y + z*z)
            azimuth = math.atan2(y, x)  # in range [-pi .. pi]
            elevation = math.asin(z/radius)
        except: pass
        
        return radius, azimuth, elevation
