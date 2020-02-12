import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode

modeTypeItems = [
    ("LINE", "Line", "Draw for strokes using a continuous line", "NONE", 0),
    ("DOTS", "Dots", "Draw for strokes using separated dots", "NONE", 1),
    ("BOX", "Boxes", "Draw for strokes using separated rectangle boxes", "NONE", 2)
]

class GPMaterialOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPMaterialOutputNode"
    bl_label = "GP Material Output"

    modeType: EnumProperty(name = "Mode Type", default = "LINE",
        items = modeTypeItems, update = propertyChanged)

    def create(self):
        self.newInput("Material", "Material", "material", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Boolean", "Stroke", "strokeBool", value = True)
        self.newInput("Color", "Stroke Color", "strokeColor")
        self.newInput("Boolean", "Fill", "fillBool", value = False)
        self.newInput("Color", "Fill Color", "fillColor")
        self.newInput("Integer", "Pass Index", "passIndex", value = 0, hide = True)

        self.newOutput("Material", "Material", "material")

    def draw(self, layout):
        layout.prop(self, "modeType", text = "")

    def execute(self, material, strokeBool, strokeColor, fillBool, fillColor, passIndex):
        if material is None: return None
        if not material.is_grease_pencil:
            bpy.data.materials.create_gpencil_data(material)

        gpMaterial = material.grease_pencil
        gpMaterial.show_stroke = strokeBool
        gpMaterial.mode = self.modeType
        gpMaterial.show_fill = fillBool

        if strokeBool and  gpMaterial.stroke_style == "SOLID":
            gpMaterial.color = strokeColor
        if fillBool and gpMaterial.fill_style in ["SOLID", "GRADIENT", "CHECKER_BOARD"]:
            gpMaterial.fill_color = fillColor
        gpMaterial.pass_index = passIndex

        return material
