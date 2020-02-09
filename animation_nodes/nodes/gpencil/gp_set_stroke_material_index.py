import bpy
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import VirtualLongList, VirtualPyList, GPStroke

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
            ("Stroke", "outStroke"), ("Strokes", "outStrokes")))

    def getExecutionFunctionName(self):
        if self.useStrokeList or self.useIntegerList:
            return "execute_StrokeList_MaterialIndexList"
        else:
            return "execute_Stroke_MaterialIndex"

    def execute_Stroke_MaterialIndex(self, stroke, materialIndex):
        stroke.materialIndex = materialIndex
        return stroke

    def execute_StrokeList_MaterialIndexList(self, strokes, materialIndices):
        _strokes = VirtualPyList.create(strokes, GPStroke())
        _materialIndices = VirtualLongList.create(materialIndices, 0)
        amount = VirtualPyList.getMaxRealLength(_strokes, _materialIndices)

        outStrokes = []
        for i in range(amount):
            strokeNew = _strokes[i].copy()
            strokeNew.materialIndex = _materialIndices[i]
            outStrokes.append(strokeNew)
        return outStrokes
