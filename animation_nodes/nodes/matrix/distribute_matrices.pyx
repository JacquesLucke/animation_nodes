import bpy
from bpy.props import *
from libc.limits cimport INT_MAX
from ... base_types.node import AnimationNode
from ... data_structures cimport Matrix4x4List
from ... math cimport Matrix4, Vector3, setTranslationMatrix

modeItems = [
    ("GRID", "Grid", "", "", 0)
]

distanceModeItems = [
    ("STEP", "Step", "Define the distance between two points", 0),
    ("SIZE", "Size", "Define how large the grid will be in total", 1)
]

class DistributeMatricesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DistributeMatricesNode"
    bl_label = "Distribute Matrices"

    mode = EnumProperty(name = "Mode", default = "GRID",
        items = modeItems, update = AnimationNode.refresh)

    distanceMode = EnumProperty(name = "Distance Mode", default = "STEP",
        items = distanceModeItems, update = AnimationNode.refresh)

    def create(self):
        if self.mode == "GRID":
            self.newInput("Integer", "X Divisions", "xDivisions", value = 3, minValue = 0)
            self.newInput("Integer", "Y Divisions", "yDivisions", value = 3, minValue = 0)
            self.newInput("Integer", "Z Divisions", "zDivisions", value = 1, minValue = 0)
            if self.distanceMode == "STEP":
                self.newInput("Float", "X Distance", "xDistance", value = 1)
                self.newInput("Float", "Y Distance", "yDistance", value = 1)
                self.newInput("Float", "Z Distance", "zDistance", value = 1)
            elif self.distanceMode == "SIZE":
                self.newInput("Float", "Width", "width", value = 5)
                self.newInput("Float", "Length", "length", value = 5)
                self.newInput("Float", "Height", "height", value = 5)

        self.newOutput("Matrix List", "Matrices", "matrices")

    def draw(self, layout):
        col = layout.column()
        layout.prop(self, "mode")
        if self.mode == "GRID":
            layout.prop(self, "distanceMode")

    def getExecutionFunctionName(self):
        if self.mode == "GRID":
            return "execute_Grid"

    def execute_Grid(self, xDivisions, yDivisions, zDivisions, size1, size2, size3):
        cdef:
            int xDiv = limitAmount(xDivisions)
            int yDiv = limitAmount(yDivisions)
            int zDiv = limitAmount(zDivisions)
            double xDis, yDis, zDis
            double xOffset, yOffset
            long x, y, z, index
            Vector3 vector
            Matrix4x4List matrices = Matrix4x4List(length = xDiv * yDiv * zDiv)

        if self.distanceMode == "STEP":
            xDis, yDis, zDis = size1, size2, size3
        elif self.distanceMode == "SIZE":
            xDis = size1 / max(xDiv - 1, 1)
            yDis = size2 / max(yDiv - 1, 1)
            zDis = size3 / max(zDiv - 1, 1)

        xOffset = xDis * (xDiv - 1) / 2
        yOffset = yDis * (yDiv - 1) / 2

        for x in range(xDiv):
            for y in range(yDiv):
                for z in range(zDiv):
                    index = x * yDiv * zDiv + y * zDiv + z
                    vector.x = x * xDis - xOffset
                    vector.y = y * yDis - yOffset
                    vector.z = z * zDis
                    setTranslationMatrix(matrices.data + index, &vector)

        return matrices

cdef int limitAmount(n):
    return max(min(n, INT_MAX), 0)
