import bpy
from math import isclose
from collections import namedtuple
from ... base_types import AnimationNode

Attribute = namedtuple("Attribute", ("socketType", "name", "attr"))
attributes = (
    Attribute("Color", "Color", "diffuse_color"),
    Attribute("Float", "Roughness", "roughness"),
    Attribute("Float", "Metallic", "metallic"),
    Attribute("Integer", "Pass Index", "pass_index"),
    Attribute("Boolean", "Screen Space Refraction", "use_screen_refraction"),
    Attribute("Float", "Refraction Depth", "refraction_depth"),
    Attribute("Boolean", "SSS Translucency", "use_sss_translucency"),
)

class MaterialOutputNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_MaterialOutputNode"
    bl_label = "Material Output"

    def create(self):
        self.newInput("Material", "Material", "material", defaultDrawType = "PROPERTY_ONLY")

        for attr in attributes:
            socket = self.newInput(*attr)
            socket.useIsUsedProperty = True
            socket.isUsed = False
        for socket in self.inputs[4:]:
            socket.hide = True

        self.newOutput("Material", "Material", "material")

    def getExecutionCode(self, required):
        yield "if material is not None:"
        yield "    pass"
        for i, (socketType, name, attr) in enumerate(attributes, 1):
            setFunction = "setAttribute_" + ('Color' if socketType == 'Color' else 'Numeric')
            if self.inputs[i].isUsed: yield f"    self.{setFunction}(material, '{attr}', {attr})"

    def setAttribute_Color(self, material, attribute, color):
        oldColor = list(getattr(material, attribute))
        if not all(isclose(a, b) for a, b in zip(oldColor, color)):
            setattr(material, attribute, color)

    def setAttribute_Numeric(self, material, attribute, value):
        oldValue = getattr(material, attribute)
        if not isclose(value, oldValue): setattr(material, attribute, value)
