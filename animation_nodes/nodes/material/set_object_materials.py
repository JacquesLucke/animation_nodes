import bpy
from ... base_types import AnimationNode, VectorizedSocket

class SetObjectMaterialsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetObjectMaterialsNode"
    bl_label = "Set Object Materials"

    useList = VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput(VectorizedSocket("Material", "useList",
            ("Material", "material"),
            ("Materials", "materials")))

        self.newOutput("Object", "Object", "object")

    def getExecutionFunctionName(self):
        if self.useList:
            return "executeList"
        else:
            return "executeSingle"

    def executeSingle(self, object, material):
        if object == None: return object
        slotCount = len(object.data.materials)

        if slotCount == 0:
            object.data.materials.append(material)
        else:
            object.data.materials[0] = material
            for i in range(slotCount - 1):
                object.data.materials.pop()

        return object

    def executeList(self, object, materials):
        if object == None: return object
        slotCount = len(object.data.materials)

        for i, material in enumerate(materials[:slotCount]):
            object.data.materials[i] = material
        if slotCount < len(materials):
            for i in range(slotCount, len(materials)):
                object.data.materials.append(materials[i])
        else:
            for i in range(slotCount - len(materials)):
                object.data.materials.pop()

        return object
