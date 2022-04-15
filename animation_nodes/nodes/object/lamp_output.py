import bpy
from ... base_types import AnimationNode, VectorizedSocket

class LampOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_LampOutputNode"
    bl_label = "Lamp Output"
    codeEffects = [VectorizedSocket.CodeEffect]

    useObjectList: VectorizedSocket.newProperty()
    useColorList: VectorizedSocket.newProperty()
    useFloatList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Object", "useObjectList",
            ("Object", "object", dict(defaultDrawType = "PROPERTY_ONLY")),
            ("Objects", "objects"),
            codeProperties = dict(allowListExtension = False)))

        self.newInput(VectorizedSocket("Color", "useColorList",
            ("Color", "color"), ("Colors", "colors")))
        self.newInput(VectorizedSocket("Float", "useFloatList",
            ("Energy", "energy"), ("Energies", "energies")))

        self.newOutput(VectorizedSocket("Object", "useObjectList",
            ("Object", "object", dict(defaultDrawType = "PROPERTY_ONLY")),
            ("Objects", "objects")))

        for socket in self.inputs[1:]:
            socket.useIsUsedProperty = True
            socket.isUsed = False

    def getExecutionCode(self, required):
        useColor = self.inputs[1].isUsed
        useEnergy = self.inputs[2].isUsed

        if any([useColor, useEnergy]):
            yield "if object is not None and object.type == 'LIGHT':"
            if useColor:    yield "        object.data.color = color[:3]"
            if useEnergy:   yield "        object.data.energy = energy"
