import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket

class GPencilStrokeMaterialIndexNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPencilStrokeMaterialIndexNode"
    bl_label = "GPencil Stroke Material Index"
    bl_width_default = 165

    useStrokeList: VectorizedSocket.newProperty()
    useIntegerList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Stroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")), dataIsModified = True)
        self.newInput(VectorizedSocket("Integer", "useIntegerList",
            ("Material Index", "materialIndex"), ("Material Indices", "materialIndices")))
        self.newOutput(VectorizedSocket("Stroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")), dataIsModified = True)
    
    def getExecutionFunctionName(self):
        if self.useStrokeList and self.useIntegerList:
            return "executeListList"
        elif self.useStrokeList:
            return "executeList"
        else:
            return "executeSingle"

    def executeSingle(self, stroke, materialIndex):
        if stroke is None: return None
        stroke.material_index = materialIndex
        return stroke

    def executeList(self, strokes, materialIndex):
        if len(strokes) == 0: return strokes
        for stroke in strokes:
            if stroke is not None:
                stroke.material_index = materialIndex
        return strokes

    def executeListList(self, strokes, materialIndices):
        if len(strokes) == 0 or len(materialIndices) == 0 or len(strokes) != len(materialIndices): return strokes
        for i, stroke in enumerate(strokes):
            if stroke is not None:
                stroke.material_index = materialIndices[i]
        return strokes