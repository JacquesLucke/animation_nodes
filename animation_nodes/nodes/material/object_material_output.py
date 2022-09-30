import bpy
from bpy.props import *
from ... base_types import AnimationNode, VectorizedSocket

class ObjectMaterialOutputNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_ObjectMaterialOutputNode"
    bl_label = "Object Material Output"

    appendMaterials: BoolProperty(name = "Append Materials", default = False,
        description = "Append input material(s) to the object's materials instead of overwriting them")

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

        if material is None: return object
        self.appendMaterial(objectMaterials, material)
        return object

    def executeList(self, object, materials):
        if object is None or not hasattr(object.data, "materials"): return object

        objectMaterials = object.data.materials
        if not self.appendMaterials: objectMaterials.clear()

        for material in materials:
            if material is None: continue
            self.appendMaterial(objectMaterials, material)
        return object

    def appendMaterial(self, objectMaterials, material):
        if self.appendMaterials:
            if material.name not in objectMaterials: objectMaterials.append(material)
        else:
            objectMaterials.append(material)
