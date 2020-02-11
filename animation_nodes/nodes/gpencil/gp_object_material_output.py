import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket

class GPObjectMaterialOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GPObjectMaterialOutputNode"
    bl_label = "GP Object Material Output"
    errorHandlingType = "EXCEPTION"

    useMaterialList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput(VectorizedSocket("Material", "useMaterialList",
            ("Material", "material"), ("Materials", "materials")), defaultDrawType = "PROPERTY_ONLY")

        self.newOutput("Object", "Object", "object")

    def getExecutionFunctionName(self):
        if self.useMaterialList:
            return "executeList"
        else:
            return "executeSingle"

    def executeSingle(self, object, material):
        if object is None: return object
        if not hasattr(object.data, "materials"): return object
        if object.type != "GPENCIL": return object
        if material is None: return object

        if material.name not in object.data.materials:
            bpy.data.materials.create_gpencil_data(material)
            object.data.materials.append(material)
        return object

    def executeList(self, object, materials):
        if object is None: return object
        if not hasattr(object.data, "materials"): return object
        if object.type != "GPENCIL": return object

        for material in materials:
            if material is not None:
                bpy.data.materials.create_gpencil_data(material)
                if material.name not in object.data.materials:
                    object.data.materials.append(material)
        return object
