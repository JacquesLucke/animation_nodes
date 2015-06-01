import bpy
import math
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

class mn_Math3DCoordinatesSphericalToCartesian(Node, AnimationNode):
    bl_idname = "mn_Math3DCoordinatesSphericalToCartesian"
    bl_label = "Spherical To Cartesian"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_FloatSocket", "Radius")
        self.inputs.new("mn_FloatSocket", "Azimuth")       # in [-pi .. pi]
        self.inputs.new("mn_FloatSocket", "Elevation")     # in [-pi/2 .. pi/2]
        self.outputs.new("mn_FloatSocket", "X")
        self.outputs.new("mn_FloatSocket", "Y")
        self.outputs.new("mn_FloatSocket", "Z")
        allowCompiling()

    def getInputSocketNames(self):
        return {"Radius" : "radius",
                "Azimuth" : "azimuth",
                "Elevation" : "elevation"}

    def getOutputSocketNames(self):
        return {"X" : "x",
                "Y" : "y",
                "Z" : "z"}

    def execute(self, radius, azimuth, elevation):
        x = 0.0
        y = 0.0
        z = 0.0
        
        try:
            cosElevation = math.cos(elevation)
            x = radius * cosElevation * math.cos(azimuth)
            y = radius * cosElevation * math.sin(azimuth)
            z = radius * math.sin(elevation)
        except: pass
        
        return x, y, z
