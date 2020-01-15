import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket

class GPencilObjectMaterialOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPencilObjectMaterialOutputNode"
    bl_label = "GPencil Object Material Output"
    bl_width_default = 175

    useMaterialList: VectorizedSocket.newProperty()
    removeMaterialBool: BoolProperty(name="Remove Old Materials",
                        description = "It remove all old materials of object and only use when necessary.",
                        default=False, update=propertyChanged)

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput(VectorizedSocket("Material", "useMaterialList",
            ("Material", "material"),
            ("Materials", "materials")), defaultDrawType = "PROPERTY_ONLY")

        self.newOutput("Object", "Object", "object")

    def draw(self, layout):
        layout.prop(self, "removeMaterialBool")

    def getExecutionFunctionName(self):
        if self.useMaterialList:
            return "executeList"
        else:
            return "executeSingle"

    def executeSingle(self, object, material):
        if object is None or not hasattr(object.data, "materials") or object.type != "GPENCIL": return object
        if self.removeMaterialBool: object.data.materials.clear()
        if material is None: return object
        if material.name not in object.data.materials:
            bpy.data.materials.create_gpencil_data(material)
            object.data.materials.append(material)
        return object

    def executeList(self, object, materials):
        if object is None or not hasattr(object.data, "materials") or object.type != "GPENCIL": return object
        if self.removeMaterialBool: object.data.materials.clear()
        for material in materials:
            if material is not None:
                bpy.data.materials.create_gpencil_data(material)
                if material.name not in object.data.materials:
                    object.data.materials.append(material)
        return object
