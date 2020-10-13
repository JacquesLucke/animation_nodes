import bpy
from ... base_types import AnimationNode, VectorizedSocket

class CopyObjectModifiersNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CopyObjectModifiersNode"
    bl_label = "Copy Object Modifiers"
    codeEffects = [VectorizedSocket.CodeEffect]

    useFromList: VectorizedSocket.newProperty()
    useToList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Object", ["useFromList", "useToList"],
            ("From", "fromObject"), ("From", "fromObjects")))

        self.newInput(VectorizedSocket("Object", "useToList",
            ("To", "toObject"), ("To", "toObjects"),
            codeProperties = dict(allowListExtension = False)))

        self.newOutput(VectorizedSocket("Object", "useToList",
            ("To", "outObject"), ("To", "outObjects")))

    def getExecutionCode(self, required):
        return "outObject = self.copyObjectModifiers(fromObject, toObject)"

    def copyObjectModifiers(self, fromObject, toObject):
        if fromObject is None or toObject is None: return toObject

        toObject.modifiers.clear()
        for modifier in fromObject.modifiers:
            newModifier = toObject.modifiers.new(modifier.name, modifier.type)

            for rnaProperty in modifier.bl_rna.properties:
                if rnaProperty.is_readonly: continue
                propertyValue = getattr(modifier, rnaProperty.identifier)
                setattr(newModifier, rnaProperty.identifier, propertyValue)

        return toObject
