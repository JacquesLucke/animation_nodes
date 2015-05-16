import bpy
import math
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

# http://en.wikipedia.org/wiki/Polar_coordinate_system
class mn_Math3DCoordinatesCylindricalToCartesianList(Node, AnimationNode):
    bl_idname = "mn_Math3DCoordinatesCylindricalToCartesianList"
    bl_label = "Cylindrical To Cartesian List"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_FloatListSocket", "List Radius")
        self.inputs.new("mn_FloatListSocket", "List Azimuth")
        self.inputs.new("mn_FloatListSocket", "List Z")
        self.outputs.new("mn_FloatListSocket", "List X")
        self.outputs.new("mn_FloatListSocket", "List Y")
        self.outputs.new("mn_FloatListSocket", "List Z")
        allowCompiling()

    def getInputSocketNames(self):
        return {"List Radius" : "listRadius",
                "List Azimuth" : "listAzimuth",
                "List Z" : "listZ"}

    def getOutputSocketNames(self):
        return {"List X" : "listX",
                "List Y" : "listY",
                "List Z" : "listZ"}

    def canExecute(self, listRadius, listAzimuth, listZ):
        if len(listRadius) != len(listAzimuth): return False
        if len(listAzimuth) != len(listZ): return False
            
        return True

    def execute(self, listRadius, listAzimuth, listZ):
        listX = []
        listY = []
        if not self.canExecute(listRadius, listAzimuth, listZ):
            return listX, listY, []
        
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
        
        return listX, listY, listZ

