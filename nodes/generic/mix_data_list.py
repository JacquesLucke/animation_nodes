import bpy
from bpy.props import *
from . mix_data import getMixCode
from ... tree_info import keepNodeLinks
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode
from ... sockets.info import toIdName, toListIdName, toListDataType

nodeTypes = {
    "Matrix" : "Mix Matrix List",
    "Vector" : "Mix Vector List",
    "Float" : "Mix Float List",
    "Color" : "Mix Color List",
    "Euler" : "Mix Euler List",
    "Quaternion" : "Mix Quaternion List" }

class MixDataListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MixDataListNode"
    bl_label = "Mix Data List"

    onlySearchTags = True
    searchTags = [(tag, {"dataType" : repr(type)}) for type, tag in nodeTypes.items()]

    def dataTypeChanged(self, context):
        self.recreateSockets()

    dataType = StringProperty(update = dataTypeChanged)
    repeat = BoolProperty(name = "Repeat", default = False,
        description = "Repeat the factor for values above and below 0-1", update = executionCodeChanged)

    def create(self):
        self.dataType = "Float"

    def draw(self, layout):
        layout.prop(self, "repeat")

    def drawLabel(self):
        return nodeTypes[self.outputs[0].dataType]

    def getExecutionCode(self):
        lines = []
        lines.append("length = len(dataList)")
        lines.append("if length > 0:")
        lines.append("    f = (factor{}) * (length - 1)".format(" % 1" if self.repeat else ""))
        lines.append("    before = dataList[max(min(math.floor(f), length - 1), 0)]")
        lines.append("    after = dataList[max(min(math.ceil(f), length - 1), 0)]")
        lines.append("    influence = interpolation(f % 1)")
        lines.append("    " + getMixCode(self.dataType, "before", "after", "influence", "result"))
        lines.append("else: result = self.outputs[0].getValue()")
        return lines

    def getUsedModules(self):
        return ["math"]

    @keepNodeLinks
    def recreateSockets(self):
        self.inputs.clear()
        self.outputs.clear()

        self.inputs.new("an_FloatSocket", "Factor", "factor").setRange(0, 1)
        self.inputs.new(toListIdName(self.dataType), toListDataType(self.dataType), "dataList")
        self.inputs.new("an_InterpolationSocket", "Interpolation", "interpolation").defaultDrawType = "PROPERTY_ONLY"
        self.outputs.new(toIdName(self.dataType), "Result", "result")
