import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode

modeTypeItems = [
    ("LINE", "Line", "", "NONE", 0),
    ("DOTS", "Dots", "", "NONE", 1),
    ("BOX", "Boxes", "", "NONE", 2)
]

class GPMaterialOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPMaterialOutputNode"
    bl_label = "GP Material Output"

    modeType: EnumProperty(name = "Mode Type", default = "LINE",
        items = modeTypeItems, update = AnimationNode.refresh)

    strokeBool: BoolProperty(name="Stroke",
                        description = "Stroke Mode for material",
                        default=True, update=propertyChanged)
    fillBool: BoolProperty(name="Fill",
                        description = "Fill Mode for material",
                        default=False, update=propertyChanged)

    def create(self):
        self.newInput("Material", "Material", "material", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Color", "Color", "color")
        self.newInput("Color", "Fill Color", "fillColor")
        self.newInput("Integer", "Pass Index", "passIndex", value = 0, hide = True)
        self.newOutput("Material", "Material", "material")

    def draw(self, layout):
        layout.prop(self, "strokeBool")
        layout.prop(self, "modeType", text = "")
        layout.row().separator()
        layout.prop(self, "fillBool")

    def execute(self, material, color, fillColor, passIndex):
        if material is None: return None
        bpy.data.materials.create_gpencil_data(material)
        gpMaterial = material.grease_pencil
        gpMaterial.show_stroke = self.strokeBool
        gpMaterial.mode = self.modeType
        gpMaterial.show_fill = self.fillBool
        if self.strokeBool and  gpMaterial.stroke_style == "SOLID":
            gpMaterial.color = color
        if self.fillBool and gpMaterial.fill_style in ["SOLID", "GRADIENT", "CHECKER_BOARD"]:
            gpMaterial.fill_color = fillColor
        gpMaterial.pass_index = passIndex
        return material
