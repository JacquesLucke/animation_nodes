import bpy
import math
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

# http://en.wikipedia.org/wiki/Polar_coordinate_system
class mn_Math2DCoordinatesCartesianToPolarList(Node, AnimationNode):
    bl_idname = "mn_Math2DCoordinatesCartesianToPolarList"
    bl_label = "Cartesian To Polar List"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_FloatListSocket", "List X")
        self.inputs.new("mn_FloatListSocket", "List Y")
        self.outputs.new("mn_FloatListSocket", "List Radius")
        self.outputs.new("mn_FloatListSocket", "List Azimuth")
        allowCompiling()

    def getInputSocketNames(self):
        return {"List X" : "listX",
                "List Y" : "listY"}

    def getOutputSocketNames(self):
        return {"List Radius" : "listRadius",
                "List Azimuth" : "listAzimuth"}

    def canExecute(self, listX, listY):
        if len(listX) != len(listY): return False
            
        return True

    def execute(self, listX, listY):
        listRadius = []
        listAzimuth = []
        if not self.canExecute(listX, listY):
            return listRadius, listAzimuth
        
        try:
            lenLists = len(listX)
            for iLists in range(lenLists):
                x = listX[iLists]
                y = listY[iLists]
                radius = math.sqrt(x*x + y*y)
                azimuth = math.atan2(y, x)  # in range [-pi .. pi]
                listRadius.append(radius)
                listAzimuth.append(azimuth)
        except: pass
        
        return listRadius, listAzimuth

