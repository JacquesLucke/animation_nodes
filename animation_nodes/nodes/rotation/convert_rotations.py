import bpy
import math
from bpy.props import *
from ... events import executionCodeChanged
from ... data_structures import Matrix4x4List
from ... base_types import AnimationNode, VectorizedSocket

conversionTypeItems = [
    ("QUATERNION_TO_EULER", "Quaternion to Euler", "", "NONE", 0),
    ("EULER_TO_QUATERNION", "Euler to Quaternion", "", "NONE", 1),
    ("QUATERNION_TO_MATRIX", "Quaternion to Matrix", "", "NONE", 2),
    ("MATRIX_TO_QUATERNION", "Matrix to Quaternion", "", "NONE", 3),
    ("EULER_TO_MATRIX", "Euler to Matrix", "", "NONE", 4),
    ("MATRIX_TO_EULER", "Matrix to Euler", "", "NONE", 5),
    ("QUATERNION_TO_AXIS_ANGLE", "Quaternion to Axis Angle", "", "NONE", 6),
    ("AXIS_ANGLE_TO_QUATERNION", "Axis Angle to Quaternion", "", "NONE", 7) ]

conversionListItems = [
    ("QUATERNIONS_TO_EULERS", "Quaternions to Eulers", "", "NONE", 0),
    ("EULERS_TO_QUATERNIONS", "Eulers to Quaternions", "", "NONE", 1),
    ("QUATERNIONS_TO_MATRICES", "Quaternions to Matrices", "", "NONE", 2),
    ("MATRICES_TO_QUATERNIONS", "Matrices to Quaternions", "", "NONE", 3),
    ("EULERS_TO_MATRICES", "Eulers to Matrices", "", "NONE", 4),
    ("MATRICES_TO_EULERS", "Matrices to Eulers", "", "NONE", 5),
    ("QUATERNIONS_TO_AXISES_ANGLES", "Quaternions to Axises Angles", "", "NONE", 6),
    ("AXISES_ANGLES_TO_QUATERNIONS", "Axises Angles to Quaternions", "", "NONE", 7) ]

class ConvertRotationsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConvertRotationsNode"
    bl_label = "Convert Rotations"
    bl_width_default = 160
    dynamicLabelType = "ALWAYS"

    onlySearchTags = True
    searchTags = [(name, {"conversionType" : repr(type)}) for type, name, _,_,_ in conversionTypeItems]

    conversionType: EnumProperty(name = "Conversion Type", default = "QUATERNION_TO_EULER",
        items = conversionTypeItems, update = AnimationNode.refresh)
        
    listItems: EnumProperty(name = "List Items", default = "QUATERNIONS_TO_EULERS",
        items_1 = conversionListItems, update = AnimationNode.refresh)

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
                    return item_1[1]
                else:
                    return item[1]

    def getExecutionCode(self, required):
        if self.conversionType == "QUATERNION_TO_EULER":
            if self.useList:
                return "eulers = AN.nodes.rotation.c_utils.quaternionsToEulers(quaternions)"
            else:
                return "euler = quaternion.to_euler('XYZ')"
        if self.conversionType == "EULER_TO_QUATERNION":
            if self.useList:
                return "quaternions = AN.nodes.rotation.c_utils.eulersToQuaternions(eulers)"
            else:
                return "quaternion = euler.to_quaternion()"

        if self.conversionType == "QUATERNION_TO_MATRIX":
            if self.useList:
                return "matrices = AN.nodes.rotation.c_utils.quaternionsToMatrices(quaternions)"
            else:
                return "matrix = quaternion.normalized().to_matrix().to_4x4()"
        if self.conversionType == "MATRIX_TO_QUATERNION":
            if self.useList:
                return "quaternions = self.matricesToQuaternions(matrices)"
            else:
                return "quaternion = matrix.to_quaternion()"

        if self.conversionType == "EULER_TO_MATRIX":
            if self.useList:
                return "matrices = AN.nodes.matrix.c_utils.createRotationsFromEulers(eulers)"
            else:
                return "matrix = euler.to_matrix().to_4x4()"
        if self.conversionType == "MATRIX_TO_EULER":
            if self.useList:
                return "eulers = self.matricesToEulers(matrices)"
            else:
                return "euler = matrix.to_euler('XYZ')"

        if self.conversionType == "QUATERNION_TO_AXIS_ANGLE":
            if self.useDegree:
                if self.useList:
                    return "axises, angles = AN.nodes.rotation.c_utils.quaternionsToAxises_Angles(quaternions, True)"
                else:
                    return "axis, angle = quaternion.axis, math.degrees(quaternion.angle)"
            else:
                if self.useList:
                    return "axises, angles = AN.nodes.rotation.c_utils.quaternionsToAxises_Angles(quaternions, False)"
                else:
                    return "axis, angle = quaternion.to_axis_angle()"
        if self.conversionType == "AXIS_ANGLE_TO_QUATERNION":
            if self.useDegree:
                if self.useList:
                    return "quaternions = AN.nodes.rotation.c_utils.axises_AnglesToQuaternions(axises, angles, True)"
                else:
                    return "quaternion = Quaternion(axis, math.radians(angle))"
            else:
                if self.useList:
                    return "quaternions = AN.nodes.rotation.c_utils.axises_AnglesToQuaternions(axises, angles, False)"
                else:
                    return "quaternion = Quaternion(axis, angle)"

    def getUsedModules(self):
        return ["math"]

    def matricesToQuaternions(self, matrices):
        return Matrix4x4List.toQuaternions(matrices)

    def matricesToEulers(self, matrices):
        return Matrix4x4List.toEulers(matrices)
