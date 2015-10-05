import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

filterTypeItems = [("STARTS_WITH", "Starts With", "All Objects with names starting with"),
                   ("ENDS_WITH", "Ends With", "All Objects with names ending with")]

class ObjectNameFilterNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectNameFilterNode"
    bl_label = "Object Name Filter"

    useCaseSensitive = BoolProperty(default = False, description = "Use Case Sensitive", update = executionCodeChanged)
    filterType = EnumProperty(items = filterTypeItems, default = "STARTS_WITH", update = executionCodeChanged)

    def create(self):
        self.bl_width_default = 160
        self.width = 160
        self.inputs.new("an_ObjectListSocket", "Objects", "objects")
        self.inputs.new("an_StringSocket", "Name", "name")
        self.outputs.new("an_ObjectListSocket", "Objects", "objects")

    def draw(self, layout):
        col = layout.column(align = True)
        row = col.row(align = True)
        row.prop(self, "filterType", text = "Type", expand = True)
        row.prop(self, "useCaseSensitive", text = "", icon = "FONTPREVIEW")

    def getExecutionCode(self):

        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return ""

        lines = []
        lines.append("obList = []")
        lines.append("if objects is not None: obList = objects")

        lines.append("filteredObjects = []")
        if self.useCaseSensitive:
            if self.filterType == "STARTS_WITH":
                lines.append("filteredObjects = [ob for ob in obList if ob.name.startswith(str(name))]")
            if self.filterType == "ENDS_WITH":
                lines.append("filteredObjects = [ob for ob in obList if ob.name.endswith(str(name))]")
        else:
            if self.filterType == "STARTS_WITH":
                lines.append("filteredObjects = [ob for ob in obList if ob.name.lower().startswith(str.lower(name))]")
            if self.filterType == "ENDS_WITH":
                lines.append("filteredObjects = [ob for ob in obList if ob.name.lower().endswith(str.lower(name))]")

        lines.append("objects = filteredObjects")

        return lines
