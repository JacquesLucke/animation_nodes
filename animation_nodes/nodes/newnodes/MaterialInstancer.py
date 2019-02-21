import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket

noBaseMatMessage = "No Base Material"
noInstMatMessage = "No Prefix Name"


class MaterialInstancerNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MaterialInstancerNode"
    bl_label = "Material Instancer"
    options = {"NOT_IN_SUBPROGRAM"}
    
    errorMessage: StringProperty()
    useList: VectorizedSocket.newProperty()

    prefixMaterial_bool: BoolProperty(name="Instance Material",
                              default=False, update=propertyChanged)
    rm_mat_bool: BoolProperty(
        name="Remove Materials", default=False, update=propertyChanged)

    def create(self):
        self.newInput("Text", "Base Material", "baseMaterial")
        self.newInput("Text", "Prefix For Instance Materials", "prefixMaterial")
        self.newInput("Integer", "Amount", "amount")

        self.newOutput("Material List", "Instanced Materials", "matlist")

    def draw(self, layout):
        layout.prop(self, "prefixMaterial_bool")
        layout.prop(self, "rm_mat_bool")
        if self.errorMessage != "":
            layout.label(text = self.errorMessage, icon="ERROR")

    def execute(self, baseMaterial, prefixMaterial, amount):
        self.errorMessage = ""

        #Error messages
        if baseMaterial is "":
            self.errorMessage = noBaseMatMessage
            return

        #Materials remover except "the base material"
        if self.rm_mat_bool:
            if len(bpy.data.materials) >= 1:
                for material in bpy.data.materials:
                    if material.name != baseMaterial and material.name.startswith(prefixMaterial):
                        bpy.data.materials.remove(material)
            else:
                return

        #Error message
        if prefixMaterial is "":
            self.errorMessage = noInstMatMessage
            return

        #Material instancer
        if self.prefixMaterial_bool:
            for i in range(amount):
                if i <= 9:
                    material = prefixMaterial + '.00' + str(i)
                elif i > 9 and i <= 99:
                    material = prefixMaterial + '.0' + str(i)
                elif i > 99:
                    material = prefixMaterial + '.' + str(i)

                if material not in bpy.data.materials:
                    mat = bpy.data.materials[baseMaterial].copy()
                    mat.name = material
        
        matlist = []
        for material in bpy.data.materials:
            if material.name.startswith(prefixMaterial):
                matlist.append(material)
        return matlist        
        
