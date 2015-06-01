import bpy
import math
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

# http://en.wikipedia.org/wiki/Polar_coordinate_system
class mn_Math2DCoordinatesCartesianToPolar(Node, AnimationNode):
    bl_idname = "mn_Math2DCoordinatesCartesianToPolar"
    bl_label = "Cartesian To Polar"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_FloatSocket", "X")
        self.inputs.new("mn_FloatSocket", "Y")
        self.outputs.new("mn_FloatSocket", "Radius")
        self.outputs.new("mn_FloatSocket", "Azimuth")
        allowCompiling()

    def getInputSocketNames(self):
        return {"X" : "x",
                "Y" : "y"}

    def getOutputSocketNames(self):
        return {"Radius" : "radius",
                "Azimuth" : "azimuth"}

    def execute(self, x, y):
        radius = 0.0
        azimuth = 0.0
        
        try:
            radius = math.sqrt(x*x + y*y)
            azimuth = math.atan2(y, x)  # in range [-pi .. pi]
        except: pass
        
        return radius, azimuth

