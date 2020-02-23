import bpy
from ... data_structures import DoubleList, Vector3DList
from ... base_types import AnimationNode, VectorizedSocket

class GPStrokeInfoNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPStrokeInfoNode"
    bl_label = "GP Stroke Info"

    def create(self):
        self.newInput("GPStroke", "Stroke", "stroke")

        self.newOutput("Vector List", "Points", "vertices")
        self.newOutput("Float List", "Strengths", "strengths")
        self.newOutput("Float List", "Pressures", "pressures")
        self.newOutput("Float List", "UV-Rotations", "uvRotations", hide = True)
        self.newOutput("Float", "Line Width", "lineWidth")
        self.newOutput("Boolean", "Cyclic", "drawCyclic", hide = True)
        self.newOutput("Text", "Start Cap Mode", "startCapMode", hide = True)
        self.newOutput("Text", "End Cap Mode", "endCapMode", hide = True)
        self.newOutput("Integer", "Material Index", "materialIndex")
        self.newOutput("Text", "Display Mode", "displayMode", hide = True)

    def execute(self, stroke):
        strengths = DoubleList.fromValues(stroke.strengths)
        pressures = DoubleList.fromValues(stroke.pressures)
        uvRotations = DoubleList.fromValues(stroke.uvRotations)
        return (stroke.vertices, strengths, pressures, uvRotations, stroke.lineWidth,
                stroke.drawCyclic, stroke.startCapMode, stroke.endCapMode, stroke.materialIndex,
                stroke.displayMode)
