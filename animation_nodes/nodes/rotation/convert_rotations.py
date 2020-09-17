import bpy
import math
from bpy.props import *
from ... events import executionCodeChanged
from ... data_structures import Matrix4x4List
from .. matrix.c_utils import createRotationsFromEulers
from ... base_types import AnimationNode, VectorizedSocket
from . c_utils import (
    quaternionsToEulers, eulersToQuaternions,
    quaternionsToMatrices, axises_AnglesToQuaternions,
    quaternionsToAxises_Angles
)

conversionTypeItems = [
    ("QUATERNION_TO_EULER", "Quaternion to Euler", "", "NONE", 0),
    ("EULER_TO_QUATERNION", "Euler to Quaternion", "", "NONE", 1),
    ("QUATERNION_TO_MATRIX", "Quaternion to Matrix", "", "NONE", 2),
    ("MATRIX_TO_QUATERNION", "Matrix to Quaternion", "", "NONE", 3),
    ("EULER_TO_MATRIX", "Euler to Matrix", "", "NONE", 4),
    ("MATRIX_TO_EULER", "Matrix to Euler", "", "NONE", 5),
    ("QUATERNION_TO_AXIS_ANGLE", "Quaternion to Axis Angle", "", "NONE", 6),
    ("AXIS_ANGLE_TO_QUATERNION", "Axis Angle to Quaternion", "", "NONE", 7) ]

class ConvertRotationsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConvertRotationsNode"
    bl_label = "Convert Rotations"
    bl_width_default = 160
    dynamicLabelType = "ALWAYS"

    onlySearchTags = True
    searchTags = [(name, {"conversionType" : repr(type)}) for type, name, _,_,_ in conversionTypeItems]

    conversionType: EnumProperty(name = "Conversion Type", default = "QUATERNION_TO_EULER",
        items = conversionTypeItems, update = AnimationNode.refresh)

    useDegree: BoolProperty(name = "Use Degree", default = False, update = executionCodeChanged)
    useList: VectorizedSocket.newProperty()

    def create(self):
        if self.conversionType == "QUATERNION_TO_EULER":
            self.newInput(VectorizedSocket("Quaternion", "useList",
                ("Quaternion", "quaternion"), ("Quaternions", "quaternions")))
            self.newOutput(VectorizedSocket("Euler", "useList",
                ("Euler", "euler"),("Eulers", "eulers")))
        if self.conversionType == "EULER_TO_QUATERNION":
            self.newInput(VectorizedSocket("Euler", "useList",
                ("Euler", "euler"),("Eulers", "eulers")))
            self.newOutput(VectorizedSocket("Quaternion", "useList",
                ("Quaternion", "quaternion"), ("Quaternions", "quaternions")))

        if self.conversionType == "QUATERNION_TO_MATRIX":
            self.newInput(VectorizedSocket("Quaternion", "useList",
                ("Quaternion", "quaternion"), ("Quaternions", "quaternions")))
            self.newOutput(VectorizedSocket("Matrix", "useList",
                ("Matrix", "matrix"),("Matrices", "matrices")))
        if self.conversionType == "MATRIX_TO_QUATERNION":
            self.newInput(VectorizedSocket("Matrix", "useList",
                ("Matrix", "matrix"),("Matrices", "matrices")))
            self.newOutput(VectorizedSocket("Quaternion", "useList",
                ("Quaternion", "quaternion"), ("Quaternions", "quaternions")))

        if self.conversionType == "EULER_TO_MATRIX":
            self.newInput(VectorizedSocket("Euler", "useList",
                ("Euler", "euler"),("Eulers", "eulers")))
            self.newOutput(VectorizedSocket("Matrix", "useList",
                ("Matrix", "matrix"),("Matrices", "matrices")))
        if self.conversionType == "MATRIX_TO_EULER":
            self.newInput(VectorizedSocket("Matrix", "useList",
                ("Matrix", "matrix"),("Matrices", "matrices")))
            self.newOutput(VectorizedSocket("Euler", "useList",
                ("Euler", "euler"),("Eulers", "eulers")))

        if self.conversionType == "QUATERNION_TO_AXIS_ANGLE":
            self.newInput(VectorizedSocket("Quaternion", "useList",
                ("Quaternion", "quaternion"), ("Quaternions", "quaternions")))
            self.newOutput(VectorizedSocket("Vector", "useList",
                ("Axis", "axis"),("Axises", "axises")))
            self.newOutput(VectorizedSocket("Float", "useList",
                ("Angle", "angle"),("Angles", "angles")))
        if self.conversionType == "AXIS_ANGLE_TO_QUATERNION":
            self.newInput(VectorizedSocket("Vector", "useList",
                ("Axis", "axis"),("Axises", "axises")))
            self.newInput(VectorizedSocket("Float", "useList",
                ("Angle", "angle"),("Angles", "angles")))
            self.newOutput(VectorizedSocket("Quaternion", "useList",
                ("Quaternion", "quaternion"), ("Quaternions", "quaternions")))

        self.inputs[0].defaultDrawType = "PREFER_PROPERTY"

    def draw(self, layout):
        layout.prop(self, "conversionType", text = "")
        if "ANGLE" in self.conversionType: layout.prop(self, "useDegree")

    def drawLabel(self):
        for item in conversionTypeItems:
            if self.conversionType == item[0]:
                if self.useList:
                    if item[4] == 0: return "Quaternions to Eulers"
                    elif item[4] == 1: return "Eulers to Quaternions"
                    elif item[4] == 2: return "Quaternions to Matrices"
                    elif item[4] == 3: return "Matrices to Quaternions"
                    elif item[4] == 4: return "Eulers to Matrices"
                    elif item[4] == 5: return "Matrices to Eulers"
                    elif item[4] == 6: return "Quaternions to Axises Angles"
                    else: return "Axises Angles to Quaternions"
                else:
                    return item[1]

    def getExecutionCode(self, required):
        if self.conversionType == "QUATERNION_TO_EULER":
            if self.useList:
                return "eulers = self.QuaternionsToEulers(quaternions)"
            else:
                return "euler = quaternion.to_euler('XYZ')"
        if self.conversionType == "EULER_TO_QUATERNION":
            if self.useList:
                return "quaternions = self.EulersToQuaternions(eulers)"
            else:
                return "quaternion = euler.to_quaternion()"

        if self.conversionType == "QUATERNION_TO_MATRIX":
            if self.useList:
                return "matrices = self.QuaternionsToMatrices(quaternions)"
            else:
                return "matrix = quaternion.normalized().to_matrix().to_4x4()"
        if self.conversionType == "MATRIX_TO_QUATERNION":
            if self.useList:
                return "quaternions = self.MatricesToQuaternions(matrices)"
            else:
                return "quaternion = matrix.to_quaternion()"

        if self.conversionType == "EULER_TO_MATRIX":
            if self.useList:
                return "matrices = self.EulersToMatrices(eulers)"
            else:
                return "matrix = euler.to_matrix().to_4x4()"
        if self.conversionType == "MATRIX_TO_EULER":
            if self.useList:
                return "eulers = self.MatricesToEulers(matrices)"
            else:
                return "euler = matrix.to_euler('XYZ')"

        if self.conversionType == "QUATERNION_TO_AXIS_ANGLE":
            if self.useDegree:
                if self.useList:
                    return "axises, angles = self.QuaternionsToAxises_Angles(quaternions, True)"
                else:
                    return "axis, angle = quaternion.axis, math.degrees(quaternion.angle)"
            else:
                if self.useList:
                    return "axises, angles = self.QuaternionsToAxises_Angles(quaternions, False)"
                else:
                    return "axis, angle = quaternion.to_axis_angle()"
        if self.conversionType == "AXIS_ANGLE_TO_QUATERNION":
            if self.useDegree:
                if self.useList:
                    return "quaternions = self.Axises_AnglesToQuaternions(axises, angles, True)"
                else:
                    return "quaternion = Quaternion(axis, math.radians(angle))"
            else:
                if self.useList:
                    return "quaternions = self.Axises_AnglesToQuaternions(axises, angles, False)"
                else:
                    return "quaternion = Quaternion(axis, angle)"

    def getUsedModules(self):
        return ["math"]

    def QuaternionsToEulers(self, quaternions):
        return quaternionsToEulers(quaternions)

    def EulersToQuaternions(self, eulers):
        return eulersToQuaternions(eulers)

    def QuaternionsToMatrices(self, quaternions):
        return quaternionsToMatrices(quaternions)

    def MatricesToQuaternions(self, matrices):
        return Matrix4x4List.toQuaternions(matrices)

    def EulersToMatrices(self, eulers):
        return createRotationsFromEulers(eulers)

    def MatricesToEulers(self, matrices):
        return Matrix4x4List.toEulers(matrices)

    def QuaternionsToAxises_Angles(self, q, usedegree):
        return quaternionsToAxises_Angles(q, usedegree)

    def Axises_AnglesToQuaternions(self, a, angles, usedegree):
        return axises_AnglesToQuaternions(a, angles, usedegree)
