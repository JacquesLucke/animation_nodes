import bpy
from bpy.props import *
from .. events import propertyChanged
from .. base_types.socket import AnimationNodeSocket
from .. algorithms.interpolation import (linear, expoEaseIn, expoEaseOut,
                                    cubicEaseIn, cubicEaseOut, cubicEaseInOut,
                                    backEaseIn, backEaseOut)

topCategoryItems = [("LINEAR", "Linear", ""),
                    ("EXPONENTIAL", "Exponential", ""),
                    ("CUBIC", "Cubic", ""),
                    ("BACK", "Back", "")]

exponentialCategoryItems = [("IN", "In", ""),
                            ("OUT", "Out", "")]

cubicCategoryItems = [("IN", "In", ""),
                    ("OUT", "Out", ""),
                    ("INOUT", "In / Out", "")]

backCategoryItems = [("IN", "In", ""),
                    ("OUT", "Out", "")]

class InterpolationSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_InterpolationSocket"
    bl_label = "Interpolation Socket"
    dataType = "Interpolation"
    allowedInputTypes = ["Interpolation"]
    drawColor = (0.7, 0.4, 0.3, 1)

    topCategory = EnumProperty(
        name = "Category", default = "LINEAR",
        items = topCategoryItems, update = propertyChanged)

    backCategory = EnumProperty(
        name = "Back", default = "OUT",
        items = backCategoryItems, update = propertyChanged)

    exponentialCategory = EnumProperty(
        name = "Exponential", default = "OUT",
        items = exponentialCategoryItems, update = propertyChanged)

    cubicCategory = EnumProperty(
        name = "Cubic", default = "OUT",
        items = cubicCategoryItems, update = propertyChanged)

    showName = BoolProperty(default = True)

    def drawInput(self, layout, node, text):
        if not self.showName: text = ""
        self.drawAsProperty(layout, text)


    def drawAsProperty(self, layout, text):
        col = layout.column(align = True)
        if text != "": col.label(text)

        row = col.row(align = True)
        row.prop(self, "topCategory", text = "")

        if self.topCategory == "BACK":
            row.prop(self, "backCategory", text = "")
        if self.topCategory == "EXPONENTIAL":
            row.prop(self, "exponentialCategory", text = "")
        if self.topCategory == "CUBIC":
            row.prop(self, "cubicCategory", text = "")

    def getValue(self):
        if self.topCategory == "LINEAR": return (linear, None)
        if self.topCategory == "EXPONENTIAL":
            if self.exponentialCategory == "IN": return (expoEaseIn, None)
            if self.exponentialCategory == "OUT": return (expoEaseOut, None)
        if self.topCategory == "CUBIC":
            if self.cubicCategory == "IN": return (cubicEaseIn, None)
            if self.cubicCategory == "OUT": return (cubicEaseOut, None)
            if self.cubicCategory == "INOUT": return (cubicEaseInOut, None)
        if self.topCategory == "BACK":
            if self.backCategory == "IN": return (backEaseIn, 1.70158)
            if self.backCategory == "OUT": return (backEaseOut, 1.70158)
        return (linear, None)

    def setStoreableValue(self, data):
        self.topCategory, self.backCategory, self.exponentialCategory, self.cubicCategory = data

    def getStoreableValue(self):
        return self.topCategory, self.backCategory, self.exponentialCategory, self.cubicCategory
