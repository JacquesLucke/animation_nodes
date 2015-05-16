import bpy
import math
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

class mn_Math3DCoordinatesCartesianToSphericalList(Node, AnimationNode):
    bl_idname = "mn_Math3DCoordinatesCartesianToSphericalList"
    bl_label = "Cartesian To Spherical List"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_FloatListSocket", "List X")
        self.inputs.new("mn_FloatListSocket", "List Y")
        self.inputs.new("mn_FloatListSocket", "List Z")
        self.outputs.new("mn_FloatListSocket", "List Radius")
        self.outputs.new("mn_FloatListSocket", "List Azimuth")       # in [-pi .. pi]
        self.outputs.new("mn_FloatListSocket", "List Elevation")     # in [-pi/2 .. pi/2]
        allowCompiling()

    def getInputSocketNames(self):
        return {"List X" : "listX",
                "List Y" : "listY",
                "List Z" : "listZ"}

    def getOutputSocketNames(self):
        return {"List Radius" : "listRadius",
                "List Azimuth" : "listAzimuth",
                "List Elevation" : "listElevation"}

    def canExecute(self, listX, listY, listZ):
        if len(listX) != len(listY): return False
        if len(listY) != len(listZ): return False
            
        return True

    def execute(self, listX, listY, listZ):
        listRadius = []
        listAzimuth = []
        listElevation = []
        if not self.canExecute(listX, listY, listZ):
            return listRadius, listAzimuth, listElevation
        
        try:
            lenLists = len(listX)
            for iLists in range(lenLists):
                x = listX[iLists]
                y = listY[iLists]
                z = listZ[iLists]
                radius = math.sqrt(x*x + y*y + z*z)
                azimuth = math.atan2(y, x)
                elevation = math.asin(z/radius)
                listRadius.append(radius)
                listAzimuth.append(azimuth)
                listElevation.append(elevation)
        except: pass
        
        return listRadius, listAzimuth, listElevation
