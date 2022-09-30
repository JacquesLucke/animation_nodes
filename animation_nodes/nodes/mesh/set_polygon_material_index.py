import bpy
from ... data_structures import VirtualLongList
from ... base_types import AnimationNode, VectorizedSocket

class SetPolygonMaterialIndexNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_SetPolygonMaterialIndexNode"
    bl_label = "Set Polygon Material Index"
    errorHandlingType = "EXCEPTION"

    useMaterialIndexList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput(VectorizedSocket("Integer", "useMaterialIndexList",
                ("Material Index", "materialIndex"), ("Material Indices", "materialIndices")))

        self.newOutput("Object", "Object", "object")

    def execute(self, object, materialIndices):
        if object is None: return None

        if object.type != "MESH":
            self.raiseErrorMessage("Object is not a mesh object.")

        if object.mode != "OBJECT":
            self.raiseErrorMessage("Object is not in object mode.")

        if self.useMaterialIndexList:
            if materialIndices.containsValueLowerThan(0):
                self.raiseErrorMessage("Material index can't be negative.")
        else:
            if materialIndices < 0:
                self.raiseErrorMessage("Material index can't be negative.")

        polygons = object.data.polygons
        materialIndices = VirtualLongList.create(materialIndices, 0).materialize(len(polygons))

        polygons.foreach_set("material_index", materialIndices)
        object.data.update()
        return object
