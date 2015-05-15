import bpy
import math
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

# http://en.wikipedia.org/wiki/Polar_coordinate_system
class mn_Math2DCoordinatesPolarToCartesian(Node, AnimationNode):
    bl_idname = "mn_Math2DCoordinatesPolarToCartesian"
    bl_label = "Polar To Cartesian"
    
    # is this description used anywhere? in the node add menu, eg, would be nice
    bl_description = "Converts a (2D) point in Polar Coordinates to Cartesian Coordinates"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_FloatSocket", "Radius")
        self.inputs.new("mn_FloatSocket", "Azimuth")
        self.outputs.new("mn_FloatSocket", "X")
        self.outputs.new("mn_FloatSocket", "Y")
        allowCompiling()

    def getInputSocketNames(self):
        return {"Radius" : "radius",
                "Azimuth" : "azimuth"}

    def getOutputSocketNames(self):
        return {"X" : "x",
                "Y" : "y"}

    def execute(self, radius, azimuth):
        x = 0.0
        y = 0.0
        
        try:
            x = math.cos(azimuth) * radius
            y = math.sin(azimuth) * radius
        except: pass
        
        return x, y

