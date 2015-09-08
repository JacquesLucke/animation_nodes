import bpy
import os
from bpy.props import *
from ... base_types.node import AnimationNode
from ... utils.path import getAbsolutePathOfSound
from ... utils.enum_items import enumItemsFromDicts
from ... utils.fcurve import getSingleFCurveWithDataPath
from ... utils.sequence_editor import getOrCreateSequencer, getEmptyChannel, getSoundsInSequencer

@enumItemsFromDicts
def getSoundSequenceItems(self, context):
    items = []
    for sound in getSoundsInSequencer():
        items.append({"value" : sound.name, "id" : sound.filepath})
    return items

class SoundBakeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SoundBakeNode"
    bl_label = "Sound Bake"

    soundName = EnumProperty(name = "Sound", items = getSoundSequenceItems)

    activeBakeDataIndex = IntProperty()

    low = IntProperty(name = "Low", default = 0)
    high = IntProperty(name = "High", default = 20000)
    attack = FloatProperty(name = "Attack", default = 0.005, precision = 3)
    release = FloatProperty(name = "Release", default = 0.2, precision = 3)

    def create(self):
        self.width = 300

    def draw(self, layout):
        layout.separator()
        col = layout.column()
        col.scale_y = 1.4
        self.invokePathChooser(col, "loadSound", text = "Load New Sound", icon = "NEW")
        layout.separator()

        if self.sound is None: return

        col = layout.column(align = True)
        col.prop(self, "soundName", text = "")
        box = col.box()
        row = box.row()
        col = row.column(align = True)
        col.prop(self, "low")
        col.prop(self, "high")
        col = row.column(align = True)
        col.prop(self, "attack")
        col.prop(self, "release")

        col = box.column()
        col.scale_y = 1.3
        col.active = getBakeDataItem(self.sound, self.low, self.high, self.attack, self.release) is None
        self.invokeFunction(col, "bakeSound", text = "Bake", icon = "GHOST")

        items = self.sound.bakeData
        if len(items) == 0: return
        col = box.column()
        row = col.row()
        row.label("Baked Data:")
        self.invokeFunction(row, "moveItemUp", icon = "TRIA_UP")
        self.invokeFunction(row, "moveItemDown", icon = "TRIA_DOWN")
        col.template_list("an_BakeItemsUiList", "", self.sound, "bakeData", self, "activeBakeDataIndex", rows = len(items) + 1)

    def execute(self):
        return

    def loadSound(self, path):
        editor = getOrCreateSequencer()
        channel = getEmptyChannel(editor)
        sequence = editor.sequences.new_sound(
            name = os.path.basename(path),
            filepath = path,
            channel = channel,
            frame_start = bpy.context.scene.frame_start)
        self.soundName = sequence.sound.name

    def bakeSound(self):
        bake(self.sound, self.low, self.high, self.attack, self.release)

    def removeSingleBakedData(self, index):
        self.sound.bakeData.remove(int(index))

    def moveItemUp(self):
        fromIndex = self.activeBakeDataIndex
        toIndex = fromIndex - 1
        self.moveItem(fromIndex, toIndex)

    def moveItemDown(self):
        fromIndex = self.activeBakeDataIndex
        toIndex = fromIndex + 1
        self.moveItem(fromIndex, toIndex)

    def moveItem(self, fromIndex, toIndex):
        self.sound.bakeData.move(fromIndex, toIndex)
        self.activeBakeDataIndex = min(max(toIndex, 0), len(self.sound.bakeData) - 1)

    @property
    def sound(self):
        return bpy.data.sounds.get(self.soundName)


class BakeItemsUiList(bpy.types.UIList):
    bl_idname = "an_BakeItemsUiList"

    def draw_item(self, context, layout, sound, item, icon, node, activePropname):
        layout.label("#" + str(list(sound.bakeData).index(item)))
        layout.label(str(round(item.low)))
        layout.label(str(round(item.high)))
        layout.label(str(round(item.attack, 3)))
        layout.label(str(round(item.release, 3)))
        node.invokeFunction(layout, "removeSingleBakedData", icon = "X", emboss = False, data = list(sound.bakeData).index(item))


# Sound Baking
################################

def bake(sound, low = 0.0, high = 100000, attack = 0.005, release = 0.2):
    if getBakeDataItem(sound, low, high, attack, release):
        # This is already baked
        return

    object = createObjectWithFCurveAsTarget()
    setStartTime()
    oldArea = switchArea("GRAPH_EDITOR")
    usedUnpacking, filepath = getRealFilePath(sound)

    bpy.ops.graph.sound_bake(
        filepath = filepath,
        low = low,
        high = high,
        attack = attack,
        release = release)

    if usedUnpacking: os.remove(filepath)
    item = createBakeDataItem(sound, low, high, attack, release)
    saveBakedData(object, item)
    removeObject(object)
    switchArea(oldArea)

def createObjectWithFCurveAsTarget():
    bpy.ops.object.add()
    object = bpy.context.active_object
    object.keyframe_insert(frame = 0, data_path = "location", index = 0)
    return object

def removeObject(object):
    bpy.context.scene.objects.unlink(object)
    bpy.data.objects.remove(object)

def setStartTime():
    bpy.context.scene.frame_current = 0

def switchArea(targetType):
    area = bpy.context.area
    oldType = area.type
    area.type = targetType
    return oldType

def getRealFilePath(sound):
    filepath = getAbsolutePathOfSound(sound)
    if os.path.exists(filepath): return False, filepath
    if not sound.packed_file: raise Exception("Sound file not found")
    path = os.path.join(os.path.dirname(__file__), "TEMPORARY SOUND FILE")
    file = open(path, "w+b")
    file.write(sound.packed_file.data)
    file.close()
    return True, path

def createBakeDataItem(sound, low, high, attack, release):
    item = sound.bakeData.add()
    item.low = low
    item.high = high
    item.attack = attack
    item.release = release
    return item

def saveBakedData(object, bakeDataItem):
    fcurve = getSingleFCurveWithDataPath(object, "location")
    addSavedSample = bakeDataItem.samples.add
    for sample in fcurve.sampled_points:
        addSavedSample().strength = sample.co.y



# Utils
################################

def getBakeDataItem(sound, low, high, attack, release):
    for item in sound.bakeData:
        if all([item.low == low,
                item.high == high,
                item.attack == attack,
                item.release == release]): return item



# Register
################################

class Sample(bpy.types.PropertyGroup):
    strength = FloatProperty(precision = 6)

class BakeData(bpy.types.PropertyGroup):
    low = IntProperty(name = "Low")
    high = IntProperty(name = "High")
    attack = FloatProperty(name = "Attack", precision = 3)
    release = FloatProperty(name = "Release", precision = 3)
    samples = CollectionProperty(name = "Samples", type = Sample)

def register():
    bpy.types.Sound.bakeData = CollectionProperty(name = "Bake Data", type = BakeData)

def unregister():
    del bpy.types.Sound.bakeData
