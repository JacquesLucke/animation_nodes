import bpy
from ... data_structures import VirtualLongList
from ... base_types import AnimationNode, VectorizedSocket

class GPSetStrokeMaterialIndexNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPSetStrokeMaterialIndexNode"
    bl_label = "GP Set Stroke Material Index"

    useStrokeList: VectorizedSocket.newProperty()
    useIntegerList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")), dataIsModified = True)
        self.newInput(VectorizedSocket("Integer", "useIntegerList",
            ("Material Index", "materialIndex"), ("Material Indices", "materialIndices")))
        self.newOutput(VectorizedSocket("GPStroke", ["useStrokeList", "useIntegerList"],
            ("Stroke", "stroke"), ("Strokes", "strokes")))

    def getExecutionFunctionName(self):
        if self.useStrokeList and self.useIntegerList:
            return "execute_StrokeList_MaterialIndexList"
        elif self.useStrokeList:
            return "execute_StrokeList_MaterialIndex"
        elif self.useIntegerList:
            return "execute_Stroke_MaterialIndexList"
        else:
            return "execute_Stroke_MaterialIndex"

    def execute_Stroke_MaterialIndex(self, stroke, materialIndex):
        stroke.materialIndex = materialIndex
        return stroke

    def execute_Stroke_MaterialIndexList(self, stroke, materialIndices):
        if len(materialIndices) == 0: return [stroke]
        strokes = []
        for materialIndex in materialIndices:
            strokeNew = stroke.copy()
            strokeNew.materialIndex = materialIndex
            strokes.append(strokeNew)
        return strokes

    def execute_StrokeList_MaterialIndex(self, strokes, materialIndex):
        if len(strokes) == 0: return strokes
        for stroke in strokes:
            stroke.materialIndex = materialIndex
        return strokes

    def execute_StrokeList_MaterialIndexList(self, strokes, materialIndices):
        if len(strokes) == 0 or len(materialIndices) == 0: return strokes
        materialIndices = VirtualLongList.create(materialIndices, 0)
        for i, stroke in enumerate(strokes):
            stroke.materialIndex = materialIndices[i]
        return strokes
