import bpy
import os
from bpy.props import *
from ... tree_info import getNodeByIdentifier
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
    activeEqualizerDataIndex = IntProperty()

    low = IntProperty(name = "Low", default = 0)
    high = IntProperty(name = "High", default = 20000)
    attack = FloatProperty(name = "Attack", default = 0.005, precision = 3)
    release = FloatProperty(name = "Release", default = 0.2, precision = 3)

    bakeProgress = StringProperty()

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

        col = box.column(align = True)
        subcol = col.column(align = True)
        subcol.scale_y = 1.3
        subcol.active = getBakeDataItem(self.sound, self.low, self.high, self.attack, self.release) is None
        self.invokeFunction(subcol, "bakeSound", text = "Bake", icon = "GHOST")
        self.invokeFunction(col, "bakeEqualizerData", text = "Bake Equalizer Data", icon = "RNDCURVE")

        if self.bakeProgress != "":
            box.label(self.bakeProgress, icon = "INFO")

        items = self.sound.bakeData
        if len(items) > 0:
            col = box.column()
            row = col.row(align = True)
            row.label("Baked Data:")
            self.invokeFunction(row, "moveItemUp", icon = "TRIA_UP")
            self.invokeFunction(row, "moveItemDown", icon = "TRIA_DOWN")
            col.template_list("an_BakeItemsUiList", "", self.sound, "bakeData", self, "activeBakeDataIndex", rows = len(items) + 1)

        items = self.sound.equalizerData
        if len(items) > 0:
            col = box.column()
            row = col.row()
            row.label("Equalizer Data:")
            col.template_list("an_EqualizerItemsUiList", "", self.sound, "equalizerData", self, "activeEqualizerDataIndex", rows = len(items) + 1)


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
        sound, low, high, attack, release = self.sound, self.low, self.high, self.attack, self.release
        if getBakeDataItem(sound, low, high, attack, release): return

        soundData = bake(sound, low, high, attack, release)
        bakeDataItem = createBakeDataItem(sound, low, high, attack, release)
        addSavedSample = bakeDataItem.samples.add
        for data in soundData:
            addSavedSample().strength = data

    def bakeEqualizerData(self):
        bpy.ops.an.bake_sound_equalizer_data("INVOKE_DEFAULT",
            nodeIdentifier = self.identifier,
            soundName = self.soundName,
            attack = self.attack,
            release = self.release)

    def removeSingleBakedData(self, index):
        soundData = self.sound.bakeData.remove(int(index))

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

class EqualizerItemsUiList(bpy.types.UIList):
    bl_idname = "an_EqualizerItemsUiList"

    def draw_item(self, context, layout, sound, item, icon, node, activePropname):
        layout.label("#" + str(list(sound.equalizerData).index(item)))
        layout.label(str(round(item.attack, 3)))
        layout.label(str(round(item.release, 3)))



# Bake Equalizer Data
################################

frequencySteps = [0, 20, 40, 80, 250, 600, 2000, 4000, 6000, 8000, 20000]
frequencyRanges = list(zip(frequencySteps[:-1], frequencySteps[1:]))

class BakeEqualizerData(bpy.types.Operator):
    bl_idname = "an.bake_sound_equalizer_data"
    bl_label = "Bake Equalizer Data"

    nodeIdentifier = StringProperty()

    soundName = StringProperty()
    attack = FloatProperty()
    release = FloatProperty()

    def invoke(self, context, event):
        try: self.node = getNodeByIdentifier(self.nodeIdentifier)
        except: self.node = None
        self.sound = bpy.data.sounds[self.soundName]
        self.currentIndex = 0
        self.equalizerData = []
        self.counter = 0
        context.window_manager.modal_handler_add(self)
        self.timer = context.window_manager.event_timer_add(0.001, context.window)
        self.setNodeMessage("Baking Started")
        return {"RUNNING_MODAL"}

    def finish(self):
        bpy.context.window_manager.event_timer_remove(self.timer)
        self.setNodeMessage("")
        return {"FINISHED"}

    def modal(self, context, event):
        if "ESC" == event.type: return self.finish()
        self.counter += 1
        if self.counter % 20 != 0: return {"RUNNING_MODAL"}

        if self.currentIndex < len(frequencyRanges):
            low, high = frequencyRanges[self.currentIndex]
            data = bake(self.sound, low, high, self.attack, self.release)
            self.equalizerData.append(data)
            self.currentIndex += 1
            self.setNodeMessage("Frequency range {}-{} baked".format(low, high))
        else:
            equalizerItem = self.sound.equalizerData.add()
            equalizerItem.attack = self.attack
            equalizerItem.release = self.release
            for equalizerSampleData in zip(*self.equalizerData):
                equalizerSampleItem = equalizerItem.samples.add()
                for sample in equalizerSampleData:
                    equalizerSampleItem.samples.add().strength = sample
            return self.finish()

        context.area.tag_redraw()
        return {"RUNNING_MODAL"}

    def setNodeMessage(self, message):
        if self.node: self.node.bakeProgress = message


# Sound Baking
################################

def bake(sound, low = 0.0, high = 100000, attack = 0.005, release = 0.2):
    '''Returns a float list containing the sampled data'''
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
    soundData = getSamplesFromFCurve(object)
    removeObject(object)
    switchArea(oldArea)
    return soundData

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

def getSamplesFromFCurve(object):
    fcurve = getSingleFCurveWithDataPath(object, "location")
    return [sample.co.y for sample in fcurve.sampled_points]



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

class SingleFrequencySample(bpy.types.PropertyGroup):
    bl_idname = "an_SingleFrequencySample"
    strength = FloatProperty(precision = 6)

class MultipleFrequenciesSample(bpy.types.PropertyGroup):
    bl_idname = "an_MultipleFrequenciesSample"
    samples = CollectionProperty(name = "Samples", type = SingleFrequencySample)

class BakeData(bpy.types.PropertyGroup):
    bl_idname = "an_SoundBakeData"
    low = IntProperty(name = "Low")
    high = IntProperty(name = "High")
    attack = FloatProperty(name = "Attack", precision = 3)
    release = FloatProperty(name = "Release", precision = 3)
    samples = CollectionProperty(name = "Samples", type = SingleFrequencySample)

class EqualizerData(bpy.types.PropertyGroup):
    bl_idname = "an_SoundEqualizerData"
    attack = FloatProperty(name = "Attack", precision = 3)
    release = FloatProperty(name = "Release", precision = 3)
    samples = CollectionProperty(name = "Samples", type = MultipleFrequenciesSample)

def register():
    bpy.types.Sound.bakeData = CollectionProperty(name = "Bake Data", type = BakeData)
    bpy.types.Sound.equalizerData = CollectionProperty(name = "Equalizer Data", type = EqualizerData)

def unregister():
    del bpy.types.Sound.bakeData
    del bpy.types.Sound.equalizerData
