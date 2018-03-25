import bpy
import traceback
from ... base_types import AnimationNode
from bpy.props import IntProperty, BoolProperty
from ... data_structures import Mesh, DoubleList
from ... algorithms.lsystem import calculateLSystem

class LSystemNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_LSystemNode"
    bl_label = "LSystem"
    errorHandlingType = "EXCEPTION"
    bl_width_default = 180

    useSymbolLimit = BoolProperty(name = "Use Symbol Limit", default = True)

    symbolLimit = IntProperty(name = "Symbol Limit", default = 100000,
        description = "To prevent freezing Blender when trying to calculate too many generations.",
        min = 0)

    def create(self):
        self.newInput("Text", "Axiom", "axiom")
        self.newInput("Text List", "Rules", "rules")
        self.newInput("Float", "Generations", "generations", minValue = 0)
        self.newInput("Float", "Step Size", "stepSize", value = 1)
        self.newInput("Float", "Angle", "angle", value = 90)
        self.newInput("Integer", "Seed", "seed")

        self.newInput("Float", "Scale Width", "scaleWidth", value = 0.8, hide = True)
        self.newInput("Float", "Scale Step Size", "scaleStepSize", value = 0.9, hide = True)
        self.newInput("Float", "Gravity", "gravity", value = 0, hide = True)
        self.newInput("Float", "Random Angle", "randomAngle", value = 180, hide = True)
        self.newInput("Boolean", "Only Partial Moves", "onlyPartialMoves", value = True, hide = True)

        self.newOutput("Mesh", "Mesh", "mesh")
        self.newOutput("Float List", "Edge Widths", "edgeWidths")

    def drawAdvanced(self, layout):
        row = layout.row(align = True)
        subrow = row.row(align = True)
        subrow.active = self.useSymbolLimit
        subrow.prop(self, "symbolLimit")
        icon = "LAYER_ACTIVE" if self.useSymbolLimit else "LAYER_USED"
        row.prop(self, "useSymbolLimit", text = "", icon = icon)

    def execute(self, axiom, rules, generations, stepSize, angle, seed, scaleWidth, scaleStepSize, gravity, randomAngle, onlyPartialMoves):
        defaults = {
            "Step Size" : stepSize,
            "Angle" : angle,
            "Random Angle" : randomAngle,
            "Scale Step Size" : scaleStepSize,
            "Gravity" : gravity,
            "Scale Width" : scaleWidth
        }

        rules = [rule.strip() for rule in rules if len(rule.strip()) > 0]
        limit = self.symbolLimit if self.useSymbolLimit else None

        try:
            vertices, edges, widths = calculateLSystem(
                axiom, rules, generations, seed, defaults,
                onlyPartialMoves, limit
            )
        except Exception as e:
            self.raiseErrorMessage(str(e))

        mesh = Mesh(vertices, edges, skipValidation = True)
        widths = DoubleList.fromValues(widths)
        return mesh, widths
