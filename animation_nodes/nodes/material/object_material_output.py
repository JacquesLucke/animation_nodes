import bpy
from bpy.props import *
from ... base_types import AnimationNode, VectorizedSocket

class ObjectMaterialOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectMaterialOutputNode"
    bl_label = "Object Material Output"

    appendMaterials: BoolProperty(name = "Append Materials", default = False,
        description = "This option allow to add custom materials",
        update = AnimationNode.refresh)

    useMaterialList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput(VectorizedSocket("Material", "useMaterialList",
            ("Material", "material"),
            ("Materials", "materials")), defaultDrawType = "PROPERTY_ONLY")

        self.newOutput("Object", "Object", "object")

    def drawAdvanced(self, layout):
        row = layout.row(align = True)
        row.prop(self, "appendMaterials")

    def getExecutionFunctionName(self):
        if self.useMaterialList:
            return "executeList"
        else:
            return "executeSingle"

    def executeSingle(self, object, material):
        if object is None or not hasattr(object.data, "materials"): return object

        objectMaterials = object.data.materials
        if not self.appendMaterials: objectMaterials.clear()

        if object.type == "GPENCIL":
            if material is not None:
                if not material.is_grease_pencil:
                    bpy.data.materials.create_gpencil_data(material)
                self.setObjectMaterial(objectMaterials, material)
            return object

        self.setObjectMaterial(objectMaterials, material)
        return object

    def executeList(self, object, materials):
        if object is None or not hasattr(object.data, "materials"): return object

        objectMaterials = object.data.materials
        if not self.appendMaterials: objectMaterials.clear()

        if object.type == "GPENCIL":
            for material in materials:
                if material is not None:
                    if not material.is_grease_pencil:
                        bpy.data.materials.create_gpencil_data(material)
                    self.setObjectMaterial(objectMaterials, material)
            return object

        for material in materials:
            self.setObjectMaterial(objectMaterials, material)
        return object

    def setObjectMaterial(self, objectMaterials, material):
        if self.appendMaterials:
            if material.name not in objectMaterials: objectMaterials.append(material)
        else:
            objectMaterials.append(material)
