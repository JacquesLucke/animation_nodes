import bpy
import math
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

# http://en.wikipedia.org/wiki/Polar_coordinate_system
class mn_Math2DCoordinatesPolarToCartesianList(Node, AnimationNode):
    bl_idname = "mn_Math2DCoordinatesPolarToCartesianList"
    bl_label = "Polar To Cartesian List"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_FloatListSocket", "List Radius")
        self.inputs.new("mn_FloatListSocket", "List Azimuth")
        self.outputs.new("mn_FloatListSocket", "List X")
        self.outputs.new("mn_FloatListSocket", "List Y")
        allowCompiling()

    def getInputSocketNames(self):
        return {"List Radius" : "listRadius",
                "List Azimuth" : "listAzimuth"}

    def getOutputSocketNames(self):
        return {"List X" : "listX",
                "List Y" : "listY"}

    def canExecute(self, listRadius, listAzimuth):
        if len(listRadius) != len(listAzimuth): return False
            
        return True

    def execute(self, listRadius, listAzimuth):
        listX = []
        listY = []
        if not self.canExecute(listRadius, listAzimuth):
            return listX, listY
        
        try:
            lenLists = len(listRadius)
            for iLists in range(lenLists):
                radius = listRadius[iLists]
                azimuth = listAzimuth[iLists]
                x = math.cos(azimuth) * radius
                y = math.sin(azimuth) * radius
                listX.append(x)
                listY.append(y)
        except: pass
        
        return listX, listY

