import bpy
from ... data_structures import GPStroke
from ... base_types import AnimationNode, VectorizedSocket

class ChangeGPStrokeDirectionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ChangeGPStrokeDirectionNode"
    bl_label = "Change GP Stroke Direction"
    codeEffects = [VectorizedSocket.CodeEffect]

    useStrokeList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "stroke"), ("Strokes", "strokes")))

        self.newOutput(VectorizedSocket("GPStroke", "useStrokeList",
            ("Stroke", "newStroke"), ("Strokes", "newStrokes")))

    def getExecutionCode(self, required):
        return "newStroke = self.changeStrokeDirection(stroke)"

    def changeStrokeDirection(self, stroke):
        vertices = stroke.vertices.reversed()
        strengths = stroke.strengths.reversed()
        pressures = stroke.pressures.reversed()
        uvRotations = stroke.uvRotations.reversed()
        vertexColors = stroke.vertexColors.reversed()
        return GPStroke(vertices, strengths, pressures, uvRotations, vertexColors, stroke.lineWidth,
                        stroke.hardness, stroke.drawCyclic, stroke.startCapMode, stroke.endCapMode,
                        stroke.vertexColorFill, stroke.materialIndex, stroke.displayMode)
