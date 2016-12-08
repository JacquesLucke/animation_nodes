import bpy
import random
from bpy.props import *
from mathutils import Vector, Matrix
from ... id_keys import setIDKeyData
from ... base_types.node import AnimationNode
from ... utils.blender_ui import executeInAreaType
from ... nodes.container_provider import getMainObjectContainer

idPropertyName = "text separation node id"
indexPropertyName = "text separation node index"

outputTypeItems = [
    ("TEXT", "Text", "", "FONT_DATA", 0),
    ("CURVE", "Curve", "", "CURVE_DATA", 1),
    ("MESH", "Mesh", "", "MESH_DATA", 2) ]

originTypeItems = [
    ("DEFAULT", "Default", "", "NONE", 0),
    ("ORIGIN_GEOMETRY", "Origin to Geometry", "", "NONE", 1),
    ("ORIGIN_CURSOR", "Origin to Cursor", "", "NONE", 2),
    ("ORIGIN_CENTER_OF_MASS", "Origin to Center of Mass", "", "NONE", 3) ]

class SeparateTextObjectNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SeparateTextObjectNode"
    bl_label = "Separate Text Object"
    bl_width_default = 200

    sourceObjectName = StringProperty(name = "Source Object")
    currentID = IntProperty(default = 0)
    objectCount = IntProperty(default = 0)
    parentLetters = BoolProperty(name = "Parent to Main Container", default = True)
    materialName = StringProperty(name = "Material", default = "")
    outputType = EnumProperty(name = "Output Type", items = outputTypeItems, default = "MESH")
    originType = EnumProperty(name = "Origin Type", items = originTypeItems, default = "DEFAULT")

    def create(self):
        self.newOutput("Object List", "Text Objects", "textObjects")

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "sourceObjectName", text = "Source")

        self.invokeFunction(row, "assignActiveObject", icon = "EYEDROPPER")

        source = self.getSourceObject()
        if source is not None:
            row.prop(source, "hide", text = "")

        layout.prop_search(self, "materialName", bpy.data, "materials", text = "Material", icon = "MATERIAL_DATA")
        layout.prop(self, "originType", text = "Origin")
        layout.prop(self, "outputType", expand = True)

        self.invokeFunction(layout, "updateSeparation",
            text = "Update",
            description = "Recreate the individual characters from the source object",
            icon = "FILE_REFRESH")

    def drawAdvanced(self, layout):
        layout.prop(self, "parentLetters")

    def assignActiveObject(self):
        self.sourceObjectName = getattr(bpy.context.active_object, "name", "")

    def execute(self):
        textObjects = [None] * self.objectCount
        for object in bpy.context.scene.objects:
            if self.isObjectPartOfThisNode(object):
                index = getattr(object, '["{}"]'.format(indexPropertyName), -1)
                if 0 <= index < self.objectCount:
                    textObjects[index] = object
        return textObjects

    def updateSeparation(self):
        self.removeExistingObjects()
        self.createNewNodeID()

        source = self.getSourceObject()
        if source is None: return
        if source.data is None: return
        source.hide = False

        objects = splitTextObject(source)
        originalTexts = [object.data.body for object in objects]

        onlySelectList(objects)
        if self.outputType in ("MESH", "CURVE"):
            convertSelectedObjects(self.outputType)

        if self.originType != "DEFAULT":
            setOriginType(self.originType)

        if self.parentLetters:
            parentObjectsToMainControler(objects)

        for i, (object, originalCharacter) in enumerate(zip(objects, originalTexts)):
            object[idPropertyName] = self.currentID
            object[indexPropertyName] = i
            object.id_keys.set("String", "Initial Text", originalCharacter)
            object.id_keys.set("Transforms", "Initial Transforms",
                (object.location, object.rotation_euler, object.scale))
        bpy.ops.an.update_id_keys_list()
        self.objectCount = len(objects)

        material = bpy.data.materials.get(self.materialName)
        if material:
            setMaterialOnObjects(objects, material)

        source.hide = True
        source.hide_render = True

    def removeExistingObjects(self):
        objects = []
        for object in bpy.context.scene.objects:
            if self.isObjectPartOfThisNode(object):
                objects.append(object)
        for object in objects:
            removeObject(object)

    def createNewNodeID(self):
        random.seed()
        self.currentID = round(random.random() * 100000)

    def isObjectPartOfThisNode(self, object):
        return getattr(object, '["'+idPropertyName+'"]', -1) == self.currentID

    def getSourceObject(self):
        source = bpy.data.objects.get(self.sourceObjectName)
        if getattr(source, "type", "") == "FONT": return source
        return None

    def duplicate(self, sourceNode):
        self.createNewNodeID()

def splitTextObject(source):
    text = cleanText(source.data.body)

    splineCounter = 0
    sourceSplinePositions = getSplinePositions(source)
    objects = []

    for i, character in enumerate(text):
        name = source.name + " part " + str(i).zfill(3)
        characterObject = newCharacterObject(name, source.data, character, i)

        characterSplinePositions = getSplinePositions(characterObject)
        test = characterSplinePositions[0]
        setCharacterPosition(characterObject, source, sourceSplinePositions[splineCounter], characterSplinePositions[0])
        splineCounter += len(characterSplinePositions)

        objects.append(characterObject)

    return objects

def cleanText(text):
    for part in [" ", "\n", "\t", "\r"]:
        text = text.replace(part, "")
    return text

def newCharacterObject(name, sourceData, character, i):
    newTextData = sourceData.copy()
    newTextData.body = character
    newTextData.body_format[0].use_bold = sourceData.body_format[i].use_bold
    newTextData.body_format[0].use_italic = sourceData.body_format[i].use_italic
    newTextData.body_format[0].use_underline = sourceData.body_format[i].use_underline
    newTextData.body_format[0].use_small_caps = sourceData.body_format[i].use_small_caps
    characterObject = bpy.data.objects.new(name, newTextData)
    bpy.context.scene.objects.link(characterObject)
    return characterObject

def setCharacterPosition(characterObject, source, sourceSplinePosition, offsetPosition):
    characterOffset = sourceSplinePosition - offsetPosition
    characterObject.matrix_world = source.matrix_world * Matrix.Translation(characterOffset)

def getSplinePositions(textObject):
    onlySelect(textObject)
    curve = newCurveFromActiveObject()
    positions = [Vector(spline.bezier_points[0].co) for spline in curve.data.splines]
    removeCurve(curve)
    return positions

def onlySelect(object):
    bpy.ops.object.select_all(action = "DESELECT")
    bpy.context.scene.objects.active = object
    object.select = True

def onlySelectList(objects):
    bpy.ops.object.select_all(action = "DESELECT")
    if len(objects) == 0:
        bpy.context.scene.objects.active = None
    else:
        bpy.context.scene.objects.active = objects[0]
    for object in objects:
        object.select = True

def newCurveFromActiveObject():
    bpy.ops.object.convert(target = "CURVE", keep_original = True)
    return bpy.context.scene.objects.active

def removeCurve(curve):
    curveData = curve.data
    bpy.context.scene.objects.unlink(curve)
    bpy.data.objects.remove(curve)
    bpy.data.curves.remove(curveData)

@executeInAreaType("VIEW_3D")
def convertSelectedObjects(type = "MESH"):
    bpy.ops.object.convert(target = type)

@executeInAreaType("VIEW_3D")
def setOriginType(type = "ORIGIN_GEOMETRY"):
    bpy.ops.object.origin_set(type = type)

def removeObject(object):
    if object.mode != "OBJECT": bpy.ops.object.mode_set(mode = "OBJECT")
    bpy.context.scene.objects.unlink(object)
    objectType = object.type
    data = object.data
    bpy.data.objects.remove(object)
    if objectType == "FONT":
        bpy.data.curves.remove(data)
    elif objectType == "MESH":
        bpy.data.meshes.remove(data)

def parentObjectsToMainControler(objects):
    mainControler = getMainObjectContainer(bpy.context.scene)
    for object in objects:
        object.parent = mainControler

def setMaterialOnObjects(objects, material):
    for object in objects:
        object.active_material = material
