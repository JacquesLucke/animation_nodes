import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode

noBaseMatMessage = "No Base Material"
noPrefixMatMessage = "No Prefix Name"


class MaterialInstancerNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MaterialInstancerNode"
    bl_label = "Material Instancer"
    options = {"NOT_IN_SUBPROGRAM"}
    
    instMaterialBool: BoolProperty(name="Instance Material",
                      description = "Only use when it is required, otherwise keep it off",
                      default=False, update=propertyChanged)
    removeMaterialBool: BoolProperty(name="Remove Materials",
                        description = "It removes material which has prefix name. Only use when it is required, otherwise keep it off",
                        default=False, update=propertyChanged)
    prefixName: StringProperty(default="New", description = "Prefix Name for Instanced Materials", update=propertyChanged)
    errorMessage: StringProperty()

    def create(self):
        self.newInput("Material", "", "baseMaterial")
        self.newInput("Integer", "Amount", "amount")
        self.newOutput("Material List", "Instanced Materials", "instMaterials")

    def draw(self, layout):
        layout.prop(self, "instMaterialBool")
        layout.prop(self, "removeMaterialBool")
        layout.prop(self, "prefixName", text = "")
        if self.errorMessage != "":
            layout.label(text = self.errorMessage, icon="ERROR")

    def execute(self, baseMaterial, amount):
        self.errorMessage = ""
        
        if self.prefixName == "":
            self.errorMessage = noPrefixMatMessage
            return []

        if self.removeMaterialBool: self.removeMaterials()
        
        if baseMaterial is None:
            self.errorMessage = noBaseMatMessage
            return self.getInstMaterials()

        if self.instMaterialBool: self.copyMaterial(baseMaterial, amount)

        return self.getInstMaterials()


    def copyMaterial(self, baseMaterial, amount):
        for i in range(amount):
            if i <= 9:
                material = self.prefixName + '.00' + str(i)
            elif i > 9 and i <= 99:
                material = self.prefixName + '.0' + str(i)
            elif i > 99:
                material = self.prefixName + '.' + str(i)

            if material not in bpy.data.materials:
                mat = bpy.data.materials[baseMaterial.name].copy()
                mat.name = material

    def removeMaterials(self):
        if len(bpy.data.materials) > 0:
            for material in bpy.data.materials:
                if material.name.startswith(self.prefixName):
                    bpy.data.materials.remove(material)

    def getInstMaterials(self):
        instMaterials = []
        if len(bpy.data.materials) == 0: return instMaterials
        for material in bpy.data.materials:
            if material.name.startswith(self.prefixName):
                instMaterials.append(material)
        return instMaterials