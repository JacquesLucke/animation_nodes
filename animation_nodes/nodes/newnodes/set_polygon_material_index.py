import bpy
from bpy.props import *
from ... events import propertyChanged
from ... data_structures import LongList, VirtualLongList
from ... base_types import AnimationNode, VectorizedSocket

modeItems = [
    ("ALL", "All", "Set material index of every polygon", "NONE", 0),
    ("INDEX", "Index", "Set material index of a specific polygon", "NONE", 1)
]

class SetPolygonMaterialIndexNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetPolygonMaterialIndexNode"
    bl_label = "Set Polygon Material Index"
    errorHandlingType = "EXCEPTION"

    mode: EnumProperty(name = "Mode", default = "ALL",
        items = modeItems, update = AnimationNode.refresh)

    useIndexList: VectorizedSocket.newProperty()
    useMaterialIndexList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")

        if self.mode == "INDEX":
            self.newInput(VectorizedSocket("Integer", "useIndexList",
                ("Polygon Index", "polyIndex"), ("Polygon Indices", "polyIndices")))

        self.newInput(VectorizedSocket("Integer", ["useMaterialIndexList", "useIndexList"],
                ("Material Index", "matIndex"), ("Material Indices", "matIndices")))

        self.newOutput("Object", "Object", "object")

    def draw(self, layout):
        layout.prop(self, "mode", text = "")

    def getExecutionFunctionName(self):
        if self.mode == "INDEX":
            if self.useIndexList:
                if self.useMaterialIndexList:
                    return "execute_PolygonIndices_MaterialIndexList"
                else:
                    return "execute_PolygonIndices_MaterialIndex"
            else:
                return "execute_PolygonIndex_MaterialIndex"

        elif self.mode == "ALL":
            if self.useMaterialIndexList:
                return "execute_All_MaterialIndexList"
            else:
                return "execute_All_MaterialIndex"

    def execute_PolygonIndex_MaterialIndex(self, object, polyIndex, matIndex):
        if object is None: return None

        polygons = self.getPolygons(object)
        if polyIndex < 0 or polyIndex >= len(polygons):
            self.raiseErrorMessage("This polygon index is out of range.")

        if matIndex < 0:
            self.raiseErrorMessage("Material index can't be negative.")

        polygons[polyIndex].material_index = matIndex
        object.data.update()
        return object

    def execute_PolygonIndices_MaterialIndex(self, object, polyIndices, matIndex):
        if object is None: return None
        if len(polyIndices) == 0: return object

        polygons = self.getPolygons(object)
        polygonAmount = len(polygons)
        if len(polyIndices) > polygonAmount:
            self.raiseErrorMessage("Polygon Indices are more than polygons.")
        if min(polyIndices) < 0 or max(polyIndices) >= polygonAmount:
            self.raiseErrorMessage("Some polygon indices are out of range.")

        if matIndex < 0:
            self.raiseErrorMessage("Material index can't be negative.")

        for index in polyIndices:
            polygons[index].material_index = matIndex
        object.data.update()
        return object

    def execute_PolygonIndices_MaterialIndexList(self, object, polyIndices, matIndices):
        if object is None: return None
        if len(polyIndices) == 0: return object

        polygons = self.getPolygons(object)
        polygonAmount = len(polygons)
        if len(polyIndices) > polygonAmount:
            self.raiseErrorMessage("Polygon Indices are more than polygons.")
        if min(polyIndices) < 0 or max(polyIndices) >= polygonAmount:
            self.raiseErrorMessage("Some polygon indices are out of range.")

        if min(matIndices) < 0:
            self.raiseErrorMessage("Material index can't be negative.")

        matIndices = VirtualLongList.create(matIndices, 0)

        for i, index in enumerate(polyIndices):
            polygons[index].material_index = matIndices[i]
        object.data.update()
        return object

    def execute_All_MaterialIndex(self, object, matIndex):
        if object is None: return None
        polygons = self.getPolygons(object)

        if matIndex < 0:
            self.raiseErrorMessage("Material index can't be negative.")

        matIndices = LongList(length = len(polygons))
        matIndices.fill(matIndex)
        polygons.foreach_set("material_index", matIndices)
        object.data.update()
        return object

    def execute_All_MaterialIndexList(self, object, matIndices):
        if object is None: return None
        polygons = self.getPolygons(object)

        if min(matIndices) < 0:
            self.raiseErrorMessage("Material index can't be negative.")

        matIndices = VirtualLongList.create(matIndices, 0).materialize(len(polygons))
        polygons.foreach_set("material_index", matIndices)
        object.data.update()
        return object

    def getPolygons(self, object):
        if object.type != "MESH":
            self.raiseErrorMessage("No mesh object.")

        if object.mode == "EDIT":
            self.raiseErrorMessage("Object is not in object mode.")

        return object.data.polygons
