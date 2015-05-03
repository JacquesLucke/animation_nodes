import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *
from animation_nodes.utils.mn_interpolation_utils import *

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

class mn_InterpolationSocket(mn_BaseSocket, mn_SocketProperties):
    bl_idname = "mn_InterpolationSocket"
    bl_label = "Interpolation Socket"
    dataType = "Interpolation"
    allowedInputTypes = ["Interpolation"]
    drawColor = (0.7, 0.4, 0.3, 1)
    
    topCategory = bpy.props.EnumProperty(items = topCategoryItems, default = "LINEAR", update = nodePropertyChanged, name = "Category")
    backCategory = bpy.props.EnumProperty(items = backCategoryItems, default = "OUT", update = nodePropertyChanged, name = "Back")
    exponentialCategory = bpy.props.EnumProperty(items = exponentialCategoryItems, default = "OUT", update = nodePropertyChanged, name = "Exponential")
    cubicCategory = bpy.props.EnumProperty(items = cubicCategoryItems, default = "OUT", update = nodePropertyChanged, name = "Cubic")
    
    showName = bpy.props.BoolProperty(default = True)
    
    def drawInput(self, layout, node, text):
        col = layout.column(align = True)
        if self.showName: col.label(text)
        row = col.row(align = True)
        row.prop(self, "topCategory", text = "")
        if self.topCategory == "BACK": row.prop(self, "backCategory", text = "")
        if self.topCategory == "EXPONENTIAL": row.prop(self, "exponentialCategory", text = "")
        if self.topCategory == "CUBIC": row.prop(self, "cubicCategory", text = "")
        
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
        return (self.topCategory, self.backCategory, self.exponentialCategory, self.cubicCategory)
        
    def getCurrentMode(self):
        for mode in interpolationEnum:
            if mode.identifier == self.mode:
                return mode
        return None
