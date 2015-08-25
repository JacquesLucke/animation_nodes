import bpy
import random
from bpy.props import *
from mathutils import Vector, Matrix
from ... utils.nodes import getNode
from ... base_types.node import AnimationNode
from ... id_keys import setIDKeyData, createIDKey
from ... nodes.container_provider import getMainObjectContainer

idPropertyName = "text separation node id"
indexPropertyName = "text separation node index"

outputTypeItems = [
    ("TEXT", "Text", ""),
    ("CURVE", "Curve", ""),
    ("MESH", "Mesh", "") ]

class SeparateTextObject(bpy.types.Node, AnimationNode):
    bl_idname = "an_SeparateTextObject"
    bl_label = "Separate Text Object"

    sourceObjectName = StringProperty(name = "Source Object")
    currentID = IntProperty(default = 0)
    objectCount = IntProperty(default = 0)
    parentLetters = BoolProperty(name = "Parent to Main Container", default = True)
    materialName = StringProperty(name = "Material", default = "")
    outputType = EnumProperty(name = "Output Type", items = outputTypeItems)

    def create(self):
        self.outputs.new("an_ObjectListSocket", "Text Objects", "textObjects")
        self.width = 180

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "sourceObjectName", text = "Source")
        assign = row.operator("an.assign_active_object_to_text_separation_node", icon = "EYEDROPPER", text = "")
        assign.nodeTreeName = self.nodeTree.name
        assign.nodeName = self.name

        source = self.getSourceObject()
        if source is not None:
            row.prop(source, "hide", text = "")

        layout.prop_search(self, "materialName", bpy.data, "materials", text="Material", icon="MATERIAL_DATA")
        layout.prop(self, "outputType", expand = True)

        self.invokeFunction(layout, "updateSeparation",
            text = "Update",
            description = "Recreate the individual characters from the source object",
            icon = "FILE_REFRESH")

    def drawAdvanced(self, layout):
        layout.prop(self, "parentLetters")

    def execute(self):
        textObjects = [None] * self.objectCount
        for object in bpy.context.scene.objects:
            if self.isObjectPartOfThisNode(object):
                textObjects[getattr(object, '["'+indexPropertyName+'"]', 0)] = object
        return textObjects

    def updateSeparation(self):
        self.removeExistingObjects()
        self.createNewNodeID()

        source = self.getSourceObject()
        if source is None: return
        if source.data is None: return
        source.hide = False

        createIDKey("Initial Transforms", "Transforms")
        createIDKey("Initial Text", "String")

        objects = splitTextObject(source)
        for i, object in enumerate(objects):
            object[idPropertyName] = self.currentID
            object[indexPropertyName] = i
            setIDKeyData(object, "Initial Transforms", "Transforms", (object.location, object.rotation_euler, object.scale))
            setIDKeyData(object, "Initial Text", "String", getattr(object.data, "body", ""))
        self.objectCount = len(objects)

        onlySelectList(objects)
        if self.outputType in ("MESH", "CURVE"):
            convertSelectedObjects(self.outputType)

        if self.parentLetters:
            parentObjectsToMainControler(objects)

        material = bpy.data.materials.get(self.materialName)
        if material:
            setMaterialOnObjects(objects, material)

        source.hide = True

    def removeExistingObjects(self):
        objects = []
        for object in bpy.context.scene.objects:
            if self.isObjectPartOfThisNode(object):
                objects.append(object)
        for object in objects:
            removeObject(object)

    def createNewNodeID(self):
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
        characterObject = newCharacterObject(name, source.data, character)

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

def newCharacterObject(name, sourceData, character):
    newTextData = sourceData.copy()
    newTextData.body = character
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

def convertSelectedObjects(type = "MESH"):
    bpy.context.area.type = "VIEW_3D"
    bpy.ops.object.convert(target = type)
    bpy.context.area.type = "NODE_EDITOR"

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
    mainControler = getMainObjectContainer()
    for object in objects:
        object.parent = mainControler

def setMaterialOnObjects(objects, material):
    for object in objects:
        object.active_material = material


class AssignActiveObjectToTextSeparationNode(bpy.types.Operator):
    bl_idname = "an.assign_active_object_to_text_separation_node"
    bl_label = "Assign Active Object"

    nodeTreeName = StringProperty()
    nodeName = StringProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        object = context.active_object
        node = getNode(self.nodeTreeName, self.nodeName)
        node.sourceObjectName = object.name
        return {'FINISHED'}
