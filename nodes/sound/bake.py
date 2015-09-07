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

    low = FloatProperty(name = "Low", default = 0)
    high = FloatProperty(name = "High", default = 20000)
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
        self.invokeFunction(col, "bakeSound", text = "Bake", icon = "GHOST")

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

    @property
    def sound(self):
        return bpy.data.sounds.get(self.soundName)


def bake(sound, low = 0.0, high = 100000, attack = 0.005, release = 0.2):
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



# register
################################

class Sample(bpy.types.PropertyGroup):
    strength = FloatProperty(precision = 6)

class BakeData(bpy.types.PropertyGroup):
    low = FloatProperty()
    high = FloatProperty()
    attack = FloatProperty(precision = 3)
    release = FloatProperty(precision = 3)
    samples = CollectionProperty(type = Sample)

def register():
    bpy.types.Sound.bakeData = CollectionProperty(type = BakeData)

def unregister():
    del bpy.types.Sound.bakeData
