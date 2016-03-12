import bpy
from bpy.props import *
from ... sockets.info import toListIdName
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

dataTypes = ["Object", "Scene", "Object Group", "Text Block"]

filterTypeItems = [("STARTS_WITH", "Starts With", "All Objects with names starting with"),
                   ("ENDS_WITH", "Ends With", "All Objects with names ending with")]

class FilterBlendDataListByNameNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FilterBlendDataListByNameNode"
    bl_label = "Filter Blend Data List By Name"
    dynamicLabelType = "ALWAYS"

    onlySearchTags = True
    searchTags = [("Filter {} List by Name".format(name), {"dataType" : repr(name)}) for name in dataTypes]

    def dataTypeChanged(self, context):
        self.createSockets()
        executionCodeChanged()

    # Should be set only on node creation
    dataType = StringProperty(name = "Data Type", update = dataTypeChanged)

    filterType = EnumProperty(name = "Filter Type", default = "STARTS_WITH",
        items = filterTypeItems, update = executionCodeChanged)

    caseSensitive = BoolProperty(name = "Case Sensitive", default = False,
        update = executionCodeChanged)

    def create(self):
        self.width = 170

    def draw(self, layout):
        layout.prop(self, "filterType", expand = True)
        layout.prop(self, "caseSensitive")

    def drawLabel(self):
        return "Filter {} List".format(self.dataType)

    def createSockets(self):
        self.inputs.clear()
        self.outputs.clear()
        idName = toListIdName(self.dataType)
        self.inputs.new(idName, self.dataType + " List", "sourceList")
        self.inputs.new("an_StringSocket", "Name", "name")
        self.outputs.new(idName, self.dataType + " List", "targetList")

    def getExecutionCode(self):
        operation = "startswith" if self.filterType == "STARTS_WITH" else "endswith"

        if self.caseSensitive:
            return "targetList = [object for object in sourceList if object is not None and getattr(object, 'name', 'NONE').{}(name)]".format(operation)
        else:
            return "targetList = [object for object in sourceList if object is not None and getattr(object, 'name', 'NONE').lower().{}(name.lower())]".format(operation)
