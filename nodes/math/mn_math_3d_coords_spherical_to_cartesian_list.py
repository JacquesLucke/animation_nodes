import bpy
import math
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

class mn_Math3DCoordinatesSphericalToCartesianList(Node, AnimationNode):
    bl_idname = "mn_Math3DCoordinatesSphericalToCartesianList"
    bl_label = "Spherical To Cartesian List"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_FloatListSocket", "List Radius")
        self.inputs.new("mn_FloatListSocket", "List Azimuth")       # in [-pi .. pi]
        self.inputs.new("mn_FloatListSocket", "List Elevation")     # in [-pi/2 .. pi/2]
        self.outputs.new("mn_FloatListSocket", "List X")
        self.outputs.new("mn_FloatListSocket", "List Y")
        self.outputs.new("mn_FloatListSocket", "List Z")
        allowCompiling()

    def getInputSocketNames(self):
        return {"List Radius" : "listRadius",
                "List Azimuth" : "listAzimuth",
                "List Elevation" : "listElevation"}

    def getOutputSocketNames(self):
        return {"List X" : "listX",
                "List Y" : "listY",
                "List Z" : "listZ"}

    def canExecute(self, listRadius, listAzimuth, listElevation):
        if len(listRadius) != len(listAzimuth): return False
        if len(listAzimuth) != len(listElevation): return False
            
        return True

    def execute(self, listRadius, listAzimuth, listElevation):
        listX = []
        listY = []
        listZ = []
        if not self.canExecute(listRadius, listAzimuth, listElevation):
            return listX, listY, listZ
        
        try:
            lenLists = len(listRadius)
            for iLists in range(lenLists):
                radius = listRadius[iLists]
                azimuth = listAzimuth[iLists]
                elevation = listElevation[iLists]
                cosElevation = math.cos(elevation)
                x = radius * cosElevation * math.cos(azimuth)
                y = radius * cosElevation * math.sin(azimuth)
                z = radius * math.sin(elevation)
                listX.append(x)
                listY.append(y)
                listZ.append(z)
        except: pass
        
        return listX, listY, listZ
