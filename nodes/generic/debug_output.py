import bpy
from bpy.props import *
from ... base_types.node import AnimationNode

class DebugOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_DebugOutputNode"
    bl_label = "Debug Output"
    
    inputNames = { "Data" : "data" }
    outputNames = {}
    
    # just a random sequence
    lineSeparator = "je2c4nw"
    
    printDebugString = BoolProperty(default = False, description = "Print to the console")
    showIterableInRows = BoolProperty(default = False, description = "Display individual elements in rows")
    startRow = IntProperty(default = 0, name = "Start Rows", min = 0)
    maxRowAmount = IntProperty(default = 10, name = "Maximum Rows", min = 1)
    
    debugOutputString = StringProperty(default = "")
    
    def create(self):
        self.inputs.new("mn_GenericSocket", "Data")
        self.bl_width_max = 10000
        
    def draw_buttons(self, context, layout):
        if self.showIterableInRows:
            elements = self.debugOutputString.split(self.lineSeparator)
            if self.startRow > 0: layout.label("--- {} elements above ---".format(min(self.startRow, len(elements))))
            col = layout.column(align = True)
            endRow = self.startRow + self.maxRowAmount
            for i, element in enumerate(elements):
                if self.startRow <= i < endRow:
                    col.label("{}: {}".format(i, element))
            if endRow < len(elements): layout.label("--- {} elements below ---".format(len(elements) - endRow))
        else:
            layout.label(self.debugOutputString)
        
    def draw_buttons_ext(self, context, layout):
        col = layout.column()
        col.prop(self, "showIterableInRows", text = "Show in Rows")
        subcol = col.column(align = True)
        subcol.active = self.showIterableInRows
        subcol.prop(self, "startRow")
        subcol.prop(self, "maxRowAmount")
            
        layout.prop(self, "printDebugString", text = "Print")
        layout.prop(self, "bl_width_max", text = "Max Node Width")
        
    def execute(self, data):
        if self.showIterableInRows and hasattr(data, "__iter__"):
            self.debugOutputString = self.lineSeparator.join([str(element) for element in data])
        else:
            self.debugOutputString = str(data)
        if self.printDebugString: print(str(data))
