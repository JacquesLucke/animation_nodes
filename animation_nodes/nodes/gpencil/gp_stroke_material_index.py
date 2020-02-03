import bpy
from ... data_structures import VirtualLongList
from ... base_types import AnimationNode, VectorizedSocket

class GPStrokeMaterialIndexNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPStrokeMaterialIndexNode"
    bl_label = "GP Stroke Material Index"

    useStrokeList: VectorizedSocket.newProperty()
    useIntegerList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")), dataIsModified = True)
        self.newInput(VectorizedSocket("Integer", "useIntegerList",
            ("Material Index", "materialIndex"), ("Material Indices", "materialIndices")))
        self.newOutput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")))

    def getExecutionFunctionName(self):
        if self.useStrokeList and self.useIntegerList:
            return "executeListList"
        elif self.useStrokeList:
            return "executeList"
        else:
            return "executeSingle"

    def executeSingle(self, stroke, materialIndex):
        stroke.materialIndex = materialIndex
        return stroke

    def executeList(self, strokes, materialIndex):
        if len(strokes) == 0: return strokes
        for stroke in strokes:
            stroke.materialIndex = materialIndex
        return strokes

    def executeListList(self, strokes, materialIndices):
        if len(strokes) == 0 or len(materialIndices) == 0: return strokes
        materialIndices = VirtualLongList.create(materialIndices, 0)
        for i, stroke in enumerate(strokes):
            stroke.materialIndex = materialIndices[i]
        return strokes
