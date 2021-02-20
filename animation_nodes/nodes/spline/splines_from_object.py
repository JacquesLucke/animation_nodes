import bpy
from bpy.props import *
from ... base_types import AnimationNode
from ... utils.depsgraph import getEvaluatedID
from ... data_structures.splines.bezier_spline import BezierSpline
from ... data_structures.splines.from_blender import (
    createSplinesFromBlenderObject,
    createSplineFromBlenderSpline
)

importTypeItems = [
    ("SINGLE", "Single", "Only load one spline from the object", "", 0),
    ("ALL", "All", "Load all splines from the object", "", 1),
]

class SplinesFromObjectNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SplinesFromObjectNode"
    bl_label = "Splines from Object"
    errorHandlingType = "EXCEPTION"

    importType: EnumProperty(name = "Import Type", default = "ALL",
        items = importTypeItems, update = AnimationNode.refresh)

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Boolean", "Use World Space", "useWorldSpace", value = True)
        self.newInput("Boolean", "Apply Modifiers", "applyModifiers", value = False)
        if self.importType == "SINGLE":
            self.newInput("Integer", "Index", "index", minValue = 0)
            self.newOutput("Spline", "Spline", "spline")
        else:
            self.newOutput("Spline List", "Splines", "splines")

    def drawAdvanced(self, layout):
        layout.prop(self, "importType")

    def getExecutionCode(self, required):
        if self.importType == "SINGLE":
            yield "spline = self.getSingleSpline(object, useWorldSpace, applyModifiers, index)"
        elif self.importType == "ALL":
            yield "splines = self.getAllSplines(object, useWorldSpace, applyModifiers)"

    def getSingleSpline(self, bObject, useWorldSpace, applyModifiers, index):
        if bObject is None: return BezierSpline()
        if bObject.type not in ("CURVE", "FONT"):
            self.raiseErrorMessage("Not a curve or a font object")

        evaluatedObject = getEvaluatedID(bObject)
        bSplines = evaluatedObject.an.getCurve(applyModifiers).splines
        if 0 <= index < len(bSplines):
            bSpline = bSplines[index]
            if bSpline.type in ("POLY", "BEZIER"):
                spline = createSplineFromBlenderSpline(bSpline)
                if useWorldSpace:
                    spline.transform(evaluatedObject.matrix_world)
                return spline
            else:
                self.raiseErrorMessage("Spline type not supported: " + bSpline.type)
        else:
            self.raiseErrorMessage("Index out of range")

    def getAllSplines(self, bObject, useWorldSpace, applyModifiers):
        if bObject is None: return []
        if bObject.type not in ("CURVE", "FONT"):
            self.raiseErrorMessage("Not a curve or a font object.")

        evaluatedObject = getEvaluatedID(bObject)
        splines = createSplinesFromBlenderObject(evaluatedObject, applyModifiers)
        if useWorldSpace:
            for spline in splines:
                spline.transform(evaluatedObject.matrix_world)
        return splines
