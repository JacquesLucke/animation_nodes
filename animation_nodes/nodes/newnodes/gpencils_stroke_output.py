from itertools import chain
import bpy
from ... data_structures import Stroke, DoubleList
from ... base_types import AnimationNode

class GPencilStrokeOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPencilStrokeOutputNode"
    bl_label = "GPencil Stroke Output"

    def create(self):
        self.newInput("Vector List", "Points", "vectors")
        self.newInput("Float List", "Strengths", "strengths")
        self.newInput("Float List", "Pressures", "pressures")
        self.newInput("Float List", "UV-Rotations", "uvRotations")
        self.newInput("Float", "Line Width", "lineWidth", value = 250)
        self.newInput("Boolean", "Cyclic", "drawCyclic", value = False)
        self.newInput("Boolean", "Start Cap", "startCapMode", value = False)
        self.newInput("Boolean", "End Cap", "endCapMode", value = False)
        self.newInput("Integer", "Material Index", "materialIndex", value = 0) 
        self.newOutput("Stroke", "Stroke", "stroke")

        visibleInputs = ("Vectors", "Strengths", "Pressures", "Line Width", "Material Index")
        for socket in self.inputs:
            socket.hide = socket.name not in visibleInputs

    def execute(self, vectors, strengths, pressures, uvRotations, lineWidth, drawCyclic, startCapMode, endCapMode, materialIndex):
        lenPoints = len(vectors)
        lenVectors = lenPoints
        lenStrengths = len(strengths)
        lenPressures = len(pressures)
        lenUVRoations = len(uvRotations)
        lenStrengths = len(strengths)
        lenPressures = len(pressures)
        lenUVRoations = len(uvRotations)
        stroke = Stroke()
        if lenVectors != 0 and lenPoints == lenVectors: stroke.vectors = vectors
        if lenStrengths != 0 and lenPoints == lenStrengths: stroke.strength = strengths
        if lenPressures != 0 and lenPoints == lenPressures: stroke.pressure = pressures
        if lenUVRoations != 0 and lenPoints == lenUVRoations: stroke.uv_rotation = uvRotations
        if lenVectors != 0: stroke.line_width = lineWidth
        if lenVectors != 0: stroke.draw_cyclic = drawCyclic
        if lenVectors != 0 and startCapMode:
            stroke.start_cap_mode = 'FLAT'
        else:
            stroke.start_cap_mode = 'ROUND'

        if lenVectors != 0 and endCapMode:
            stroke.end_cap_mode = 'FLAT'
        else:
            stroke.end_cap_mode = 'ROUND'
        if lenVectors != 0: stroke.material_index = materialIndex
        return stroke

    def flatList(self, vectors):
        return list(chain.from_iterable(vectors))