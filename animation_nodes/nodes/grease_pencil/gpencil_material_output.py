import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode

modeTypeItems = [
    ("LINE", "Line", "", "NONE", 0),
    ("DOTS", "Dots", "", "NONE", 1),
    ("BOX", "Boxes", "", "NONE", 2)
]

class GPencilMaterialOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPencilMaterialOutputNode"
    bl_label = "GPencil Material Output"
    bl_width_default = 165

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
        self.newOutput("Material", "Material", "material")

    def draw(self, layout):
        layout.prop(self, "strokeBool")
        layout.prop(self, "modeType", text = "")
        layout.row().separator()
        layout.prop(self, "fillBool")

    def execute(self, material, color, fillColor):
        if material is None: return None
        bpy.data.materials.create_gpencil_data(material)
        gmaterial = material.grease_pencil
        gmaterial.show_stroke = self.strokeBool
        gmaterial.mode = self.modeType
        gmaterial.show_fill = self.fillBool
        if self.strokeBool and  gmaterial.stroke_style == "SOLID":
            gmaterial.color = color
        if self.fillBool and gmaterial.fill_style in ["SOLID", "GRADIENT", "CHECKER_BOARD"]:
            gmaterial.fill_color = fillColor    
        return material