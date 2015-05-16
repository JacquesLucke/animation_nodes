import bpy
import math
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

# http://en.wikipedia.org/wiki/Polar_coordinate_system
class mn_Math3DCoordinatesCartesianToCylindricalList(Node, AnimationNode):
    bl_idname = "mn_Math3DCoordinatesCartesianToCylindricalList"
    bl_label = "Cartesian To Cylindrical List"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_FloatListSocket", "List X")
        self.inputs.new("mn_FloatListSocket", "List Y")
        self.inputs.new("mn_FloatListSocket", "List Z")
        self.outputs.new("mn_FloatListSocket", "List Radius")
        self.outputs.new("mn_FloatListSocket", "List Azimuth")
        self.outputs.new("mn_FloatListSocket", "List Z")
        allowCompiling()

    def getInputSocketNames(self):
        return {"List X" : "listX",
                "List Y" : "listY",
                "List Z" : "listZ"}

    def getOutputSocketNames(self):
        return {"List Radius" : "listRadius",
                "List Azimuth" : "listAzimuth",
                "List Z" : "listZOut"}

    def canExecute(self, listX, listY, listZ):
        if len(listX) != len(listY): return False
        if len(listY) != len(listZ): return False
            
        return True

    def execute(self, listX, listY, listZ):
        listRadius = []
        listAzimuth = []
        if not self.canExecute(listX, listY, listZ):
            return listRadius, listAzimuth, []
        
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
        
        return listRadius, listAzimuth, listZ

