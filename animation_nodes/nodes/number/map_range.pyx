import bpy
from bpy.props import *
from ... math cimport clamp
from ... data_structures cimport DoubleList, InterpolationBase
from ... base_types import AnimationNode, AutoSelectVectorization

class MapRangeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MapRangeNode"
    bl_label = "Map Range"
    bl_width_default = 170

    clampInput = BoolProperty(name = "Clamp Input", default = True,
        description = "The input will be between Input Min and Input Max",
        update = AnimationNode.refresh)

    useInterpolation = BoolProperty(name = "Use Interpolation", default = False,
        description = "Don't use the normal linear interpolation between Min and Max (only available when clamp is turned on)",
        update = AnimationNode.refresh)

    useValueList = BoolProperty(default = False, update = AnimationNode.refresh)

    def create(self):
        self.newInputGroup(self.useValueList,
            ("Float", "Value", "value"),
            ("Float List", "Values", "values"))

        self.newInput("Float", "Input Min", "inMin", value = 0)
        self.newInput("Float", "Input Max", "inMax", value = 1)
        self.newInput("Float", "Output Min", "outMin", value = 0)
        self.newInput("Float", "Output Max", "outMax", value = 1)

        if self.useInterpolation and self.clampInput:
            self.newInput("Interpolation", "Interpolation", "interpolation", defaultDrawType = "PROPERTY_ONLY")

        self.newOutputGroup(self.useValueList,
            ("Float", "Value", "newValue"),
            ("Float List", "Values", "newValues"))

        vectorization = AutoSelectVectorization()
        vectorization.input(self, "useValueList", self.inputs[0])
        vectorization.output(self, "useValueList", self.outputs[0])
        self.newSocketEffect(vectorization)

    def draw(self, layout):
        col = layout.column(align = True)
        col.prop(self, "clampInput")

        subcol = col.column(align = True)
        subcol.active = self.clampInput
        subcol.prop(self, "useInterpolation")

    def getExecutionCode(self):
        if self.useValueList:
            if self.useInterpolation and self.clampInput:
                yield "newValues = self.execute_Multiple_Interpolated("
                yield "    values, inMin, inMax, outMin, outMax, interpolation)"
            else:
                yield "newValues = self.execute_Multiple(values, inMin, inMax, outMin, outMax)"
        else:
            yield from self.iterExecutionCode_Single()

    def iterExecutionCode_Single(self):
        yield "if inMin == inMax: newValue = 0"
        yield "else:"
        if self.clampInput:
            yield "    _value = min(max(value, inMin), inMax) if inMin < inMax else min(max(value, inMax), inMin)"
            if self.useInterpolation:
                yield "    newValue = outMin + interpolation((_value - inMin) / (inMax - inMin)) * (outMax - outMin)"
            else:
                yield "    newValue = outMin + (_value - inMin) / (inMax - inMin) * (outMax - outMin)"
        else:
            yield "    newValue = outMin + (value - inMin) / (inMax - inMin) * (outMax - outMin)"

    def execute_Multiple(self, DoubleList values,
                         double inMin, double inMax, double outMin, double outMax):
        if inMin == inMax:
            return DoubleList.fromValues([0]) * values.length

        cdef:
            DoubleList newValues = DoubleList(length = values.length)
            double factor = (outMax - outMin) / (inMax - inMin)
            bint clamped = self.clampInput
            double x
            long i

        for i in range(newValues.length):
            x = values.data[i]
            if clamped: x = clamp(x, inMin, inMax)
            newValues.data[i] = outMin + (x - inMin) * factor

        return newValues

    def execute_Multiple_Interpolated(self, DoubleList values,
                                double inMin, double inMax, double outMin, double outMax,
                                InterpolationBase interpolation):
        if inMin == inMax:
            return DoubleList.fromValues([0]) * values.length

        cdef:
            DoubleList newValues = DoubleList(length = values.length)
            double factor1 = 1 / (inMax - inMin)
            double factor2 = outMax - outMin
            bint clamped = self.clampInput
            double x
            long i

        for i in range(newValues.length):
            x = clamp(values.data[i], inMin, inMax)
            newValues.data[i] = outMin + interpolation.evaluate((x - inMin) * factor1) * factor2

        return newValues
