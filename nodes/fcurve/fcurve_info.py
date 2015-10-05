import bpy
from ... base_types.node import AnimationNode

class FCurveInfoNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FCurveInfoNode"
    bl_label = "FCurve Info"

    def create(self):
        self.inputs.new("an_FCurveSocket", "FCurve", "fCurve")
        self.outputs.new("an_StringSocket", "Data Path", "dataPath")
        self.outputs.new("an_IntegerSocket", "Array Index", "arrayIndex")

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return

        yield "if fCurve is not None:"
        if isLinked["dataPath"]: yield "    dataPath = fCurve.data_path"
        if isLinked["arrayIndex"]: yield "    arrayIndex = fCurve.array_index"
        yield "else: dataPath = arrayIndex = ''"
