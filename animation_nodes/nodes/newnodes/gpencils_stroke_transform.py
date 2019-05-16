from itertools import chain
import bpy
from ... data_structures import Stroke
from . c_utils import combineVectorList
from ... data_structures import DoubleList, VirtualDoubleList
from ... base_types import AnimationNode, VectorizedSocket

class GPencilStrokeTransformNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPencilStrokeTransformNode"
    bl_label = "GPencil Stroke Transform"
    bl_width_default = 165

    useStrokeList: VectorizedSocket.newProperty()
    useMatrixList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Stroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")))
        self.newInput(VectorizedSocket("Matrix", "useMatrixList",
            ("Matrix", "matrix"), ("Matices", "matrices")))
        self.newOutput(VectorizedSocket("Stroke", "useStrokeList",
            ("Stroke", "outStroke"), ("Strokes", "outStrokes")))

    def getExecutionFunctionName(self):
        if self.useStrokeList and self.useMatrixList:
            return "executeListList"
        elif self.useStrokeList:
            return "executeList"
        else:
            return "executeSingle"

    def executeSingle(self, stroke, matrix):
        if stroke is None: return None
        outStroke = self.copyStroke(stroke)
        if matrix is not None:
            self.strokeTransfom(outStroke, matrix)
        return outStroke

    def executeList(self, strokes, matrix):
        outStrokes = []
        if len(strokes) == 0: return strokes
        for stroke in strokes:
            if stroke is not None:
                outStroke = self.copyStroke(stroke)
                if matrix is not None:
                    self.strokeTransfom(outStroke, matrix)
                outStrokes.append(outStroke)    
        return outStrokes

    def executeListList(self, strokes, matrices):
        if len(strokes) == 0 or len(matrices) == 0 or len(strokes) != len(matrices): return strokes
        outStrokes = []
        for i, stroke in enumerate(strokes):
            if stroke is not None:
                outStroke = self.copyStroke(stroke)
                if matrices[i] is not None:
                    self.strokeTransfom(outStroke, matrices[i])
                outStrokes.append(outStroke)
        return outStrokes

    def copyStroke(self, stroke):
        return Stroke(stroke.vectors, stroke.strength, stroke.pressure, stroke.uv_rotation,
        stroke.line_width, stroke.draw_cyclic, stroke.start_cap_mode, stroke.end_cap_mode,
        stroke.material_index, stroke.display_mode, stroke.frame_number)

    def strokeTransfom(self, outStroke, matrix):
        vectors = outStroke.vectors
        flatVectors = self.flatList(vectors)
        xVectors = flatVectors[0::3]
        yVectors = flatVectors[1::3]
        zVectors = flatVectors[2::3] 
        newVectors = self.createVectorList(DoubleList.fromValues(xVectors), DoubleList.fromValues(yVectors), DoubleList.fromValues(zVectors))
        newVectors.transform(matrix)
        outStroke.vectors = newVectors
        return outStroke

    def createVectorList(self, x, y, z):
        x, y, z = VirtualDoubleList.createMultiple((x, 0), (y, 0), (z, 0))
        amount = VirtualDoubleList.getMaxRealLength(x, y, z)
        return combineVectorList(amount, x, y, z)

    def flatList(self, vectors):
        return list(chain.from_iterable(vectors))
