import bpy
import os
import math
from mathutils import Vector
from bpy.props import *
from bpy.app.handlers import persistent
from ... utils.nodes import getNode
from ... events import propertyChanged
from ... base_types.node import AnimationNode
from ... algorithms import interpolation
from ... utils.names import toDataPath
from ... utils.task_manager import TaskManager, Task
from ... utils.sequence_editor import getSoundsInSequencer, getSoundSequences, getEmptyChannel, getOrCreateSequencer
from ... utils.path import toAbsolutePath
from ... utils.fcurve import (getSingleFCurveWithDataPath,
                              removeFCurveWithDataPath,
                              deselectAllFCurves,
                              newFCurveForCustomProperty,
                              removeCustomProperty)


class Sample(bpy.types.PropertyGroup):
    strength = FloatProperty(precision = 6)
bpy.utils.register_class(Sample)
class BakeData(bpy.types.PropertyGroup):
    low = FloatProperty()
    high = FloatProperty()
    attack = FloatProperty
    release = FloatProperty()
    samples = CollectionProperty(type = Sample)

bpy.utils.register_class(BakeData)
bpy.types.Sound.bakeData = CollectionProperty(type = BakeData)

bakeFrequencies = [
    (0, 20),
    (20, 40),
    (40, 80),
    (80, 250),
    (250, 600),
    (600, 2000),
    (2000, 4000),
    (4000, 6000),
    (6000, 8000),
    (8000, 20000) ]
strengthListLength = len(bakeFrequencies)


class SequencerSoundInput(bpy.types.Node, AnimationNode):
    bl_idname = "an_SequencerSoundInput"
    bl_label = "Sequencer Sound Input"

    def settingChanged(self, context):
        self.inputs["Frequency"].hide = self.fullFrequencyRange

    isBaking = BoolProperty(default = False)
    bakeInfo = StringProperty(default = "")
    bakeProgress = IntProperty(min = 0, max = 100)

    fullFrequencyRange = BoolProperty(default = True, update = settingChanged)

    attack = FloatProperty(default = 0.005, description = "Lower values -> faster rising curve", min = 0, max = 2)
    release = FloatProperty(default = 0.2, description = "Lower values -> faster falling curve", min = 0, max = 5)

    channels = FloatVectorProperty(size = 32, update = propertyChanged, default = [True] + [False] * 31, min = 0, description = "Influence of the different sequence editor channels on the output")
    displayChannelAmount = IntProperty(default = 1, min = 0, max = 32, description = "Amount of channels displayed inside of the node")

    frameTypes = [
        ("OFFSET", "Offset", ""),
        ("ABSOLUTE", "Absolute", "") ]
    frameType = EnumProperty(name = "Frame Type", items = frameTypes, default = "OFFSET")

    def create(self):
        self.use_custom_color = True
        self.color = (0.4, 0.9, 0.4)
        self.width = 200
        self.inputs.new("an_FloatSocket", "Frame", "frame")
        socket = self.inputs.new("an_FloatSocket", "Frequency", "frequency")
        socket.value = 0.4
        socket.hide = True
        self.outputs.new("an_FloatSocket", "Strength", "strength")
        self.outputs.new("an_FloatListSocket", "Strengths", "strengths").hide = True

    def draw(self, layout):
        sequencesAmount = len(getattr(bpy.context.scene.sequence_editor, "sequences", []))
        if sequencesAmount == 0:
            self.drawEasyUI(layout)
        else:
            self.drawComplexUI(layout)

    def drawEasyUI(self, layout):
        col = layout.column()
        col.scale_y = 1.5
        props = col.operator("an.load_sound_into_sequence_editor", icon = "PLUS")
        props.nodeTreeName = self.id_data.name
        props.nodeName = self.name

    def drawComplexUI(self, layout):
        row = layout.row(align = True)
        icon = "ERROR" if sequencerData.hasChanged else "FILE_TICK"
        self.callFunctionFromUI(row, "bakeSounds", text = "Bake Sounds", icon = icon)
        row.operator("an.clear_baked_data", text = "", icon = "X")

        if self.isBaking:
            layout.prop(self, "bakeProgress", text = "Progress", slider = True)
            layout.label(self.bakeInfo, icon = "INFO")

        col = layout.column(align = True)
        for i in range(self.displayChannelAmount):
            col.prop(self, "channels", index = i, text = "Channel {}".format(i+1))

        layout.prop(self, "frameType")

    def drawAdvanced(self, layout):
        layout.prop(self, "fullFrequencyRange")
        col = layout.column(align = True)
        col.prop(self, "attack", text = "Attack Time")
        col.prop(self, "release", text = "Release Time")

        layout.prop(self, "displayChannelAmount", text = "Amount of Channels")

    def execute(self, frame, frequency):
        if self.frameType == "OFFSET":
            frame += bpy.context.scene.frame_current

        strengths = Vector.Fill(strengthListLength, 0)
        for i, channelStrength in enumerate(self.channels):
            if channelStrength > 0:
                if frame == int(frame):
                    strengthList = sequencerData.getChannelStrengthList(channel = i + 1, frame = frame)
                else:
                    # for motion blur / subframes
                    strengthList1 = sequencerData.getChannelStrengthList(channel = i + 1, frame = int(frame))
                    strengthList2 = sequencerData.getChannelStrengthList(channel = i + 1, frame = int(frame) + 1)
                    influence = frame % 1
                    strengthList = strengthList1 * (1 - influence) + strengthList2 * influence
                strengths += strengthList * channelStrength

        if self.fullFrequencyRange: strength = sum(strengths)
        else: strength = self.getFrequencyStrength(strengths, frequency)

        return strength, list(strengths)

    def getFrequencyStrength(self, strengthList, frequencyIndicator):
        frequencyIndicator *= strengthListLength
        lower = strengthList[max(min(math.floor(frequencyIndicator), strengthListLength - 1), 0)]
        upper = strengthList[max(min(math.ceil(frequencyIndicator), strengthListLength - 1), 0)]
        influence = frequencyIndicator % 1.0
        influence = interpolation.quadraticInOut(influence)
        return lower * (1 - influence) + upper * influence

    def bakeSounds(self):
        bpy.ops.an.bake_sounds("INVOKE_DEFAULT",
            nodeTreeName = self.id_data.name,
            nodeName = self.name,
            attack = self.attack,
            release = self.release)



# Cache Sound Data
###########################

class SequencerData:
    def __init__(self):
        self.reset()

    def reset(self):
        self.channels = {}
        self.hash = ""

    def getChannelStrengthList(self, channel, frame):
        frame = int(frame)
        if channel in self.channels:
            return self.channels[channel].getStrengthList(frame)
        return Vector.Fill(strengthListLength, 0)

    def update(self):
        self.channels.clear()
        soundSequences = getSoundSequences()
        for sequence in soundSequences:
            channel = sequence.channel
            if channel not in self.channels:
                self.channels[channel] = ChannelData()
            self.channels[channel].insert(sequence)
        self.hash = self.calculateSequencerHash()

    @property
    def hasChanged(self):
        return self.hash != self.calculateSequencerHash()

    def calculateSequencerHash(self):
        elements = []
        soundSequences = getSoundSequences()
        for sequence in soundSequences:
            elements.append(sequence.sound.filepath)
            elements.append(sequence.channel)
            elements.append(sequence.frame_start)
            elements.append(sequence.frame_final_start)
            elements.append(sequence.frame_final_end)
        return "".join([str(element) for element in elements])


class ChannelData:
    def __init__(self):
        self.frames = []

    def getStrengthList(self, frame):
        if frame < len(self.frames):
            return self.frames[frame]
        return Vector.Fill(strengthListLength, 0)

    def insert(self, sequence):
        self.insertMissingFrames(sequence.frame_final_end)
        sound = sequence.sound
        startFrame = sequence.frame_start
        finalEndFrame = sequence.frame_final_end

        for i, (low, high )in enumerate(bakeFrequencies):
            item = getSoundBakeItemFromFrequency(sound, low, high)
            if item is None: continue

            samples = [sample.strength for sample in item.samples]
            frameRangeStart = sequence.frame_final_start
            frameRangeEnd = min(finalEndFrame + 1, startFrame + len(samples))

            for frame in range(frameRangeStart, frameRangeEnd):
                soundFrame = frame - startFrame
                self.frames[frame][i] += samples[soundFrame]

    def insertMissingFrames(self, endFrame):
        if endFrame >= len(self.frames):
            for i in range(endFrame - len(self.frames) + 1):
                self.frames.append(Vector.Fill(strengthListLength, 0))

# all cache data is stored in this variable
sequencerData = SequencerData()

@persistent
def updateSequencerData(scene):
    # update the cache when the file is loaded
    sequencerData.update()



# Operators
###########################

class LoadSound(bpy.types.Operator):
    bl_idname = "an.load_sound_into_sequence_editor"
    bl_label = "Load Sound"
    bl_description = ""
    bl_options = {"REGISTER"}

    nodeTreeName = StringProperty()
    nodeName = StringProperty()

    filepath = bpy.props.StringProperty(subtype = "FILE_PATH")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        editor = getOrCreateSequencer()
        channel = getEmptyChannel(editor)
        editor.sequences.new_sound("Sound", self.filepath, channel, frame_start = 1)
        node = getNode(self.nodeTreeName, self.nodeName)
        node.bakeSounds()
        return {"FINISHED"}

class ClearBakedData(bpy.types.Operator):
    bl_idname = "an.clear_baked_data"
    bl_label = "Clear Baked Data"
    bl_description = ""
    bl_options = {"REGISTER"}

    def execute(self, context):
        sounds = getSoundsInSequencer()
        for sound in sounds:
            sound.bakeData.clear()
        sequencerData.update()
        return {"FINISHED"}


class BakeSounds(bpy.types.Operator):
    bl_idname = "an.bake_sounds"
    bl_label = "Bake Sounds"
    bl_description = "Bake all sounds which are used in the sequence editor (hold CTRL to rebake existing data)"
    bl_options = {"REGISTER"}

    nodeTreeName = StringProperty()
    nodeName = StringProperty()

    attack = FloatProperty()
    release = FloatProperty()

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        self.timer = context.window_manager.event_timer_add(0.001, context.window)
        self.createTasks(rebake = event.ctrl)
        return {"RUNNING_MODAL"}

    def createTasks(self, rebake):
        self.taskManager = TaskManager()
        sounds = getSoundsInSequencer()
        for sound in sounds:
            for low, high in bakeFrequencies:
                waitTask = WaitTask(25)
                bakeTask = BakeSoundObject(sound.name, low, high, self.attack, self.release)
                if not bakeTask.frequencyIsBaked or rebake:
                    self.taskManager.appendTasks(waitTask, bakeTask)

    def modal(self, context, event):
        if event.type == "ESC": return self.finish()
        if event.type != "TIMER": return {"RUNNING_MODAL"}

        try: status = self.taskManager.execute(event)
        except MissingSoundFileException:
            self.report({"ERROR"}, "Sound file not found and it is not packed into the .blend file")
            return self.finish()
        description = self.taskManager.nextDescription
        self.node.isBaking = True
        self.node.bakeInfo = description
        self.node.bakeProgress = self.taskManager.percentage * 100

        context.area.type = "NODE_EDITOR"
        context.area.tag_redraw()

        return {"RUNNING_MODAL"} if status == "CONTINUE" else self.finish()

    def finish(self):
        self.node.isBaking = False
        bpy.context.area.type = "NODE_EDITOR"
        bpy.context.window_manager.event_timer_remove(self.timer)
        sequencerData.update()
        return {"FINISHED"}

    @property
    def node(self):
        return getNode(self.nodeTreeName, self.nodeName)



# Tasks for task manager
###########################

class WaitTask(Task):
    def __init__(self, timeSteps):
        self.amount = timeSteps

    def execute(self, event):
        if event.type == "TIMER":
            self.amount -= 1
        return "FINISHED" if self.amount == 0 else "CONTINUE"


class BakeSoundObject(Task):
    def __init__(self, soundName, low, high, attack, release):
        self.timeWeight = 100
        self.soundName = soundName
        self.low, self.high, self.attack, self.release = low, high, attack, release
        self.description = "{} : {} - {}".format(soundName, low, high)

    @property
    def frequencyIsBaked(self):
        return self.getBakeItemWithSameFrequency() is not None

    @property
    def sound(self):
        return bpy.data.sounds.get(self.soundName)

    def execute(self, event):
        sound = self.sound

        filepath = toAbsolutePath(sound.filepath, library = sound.library)
        useUnpacking = False
        if not os.path.exists(filepath):
            if sound.packed_file:
                filepath = os.path.join(os.path.dirname(__file__), "TEMPORARY SOUND FILE")
                file = open(filepath, "w+b")
                file.write(sound.packed_file.data)
                file.close()
                useUnpacking = True
            else:
                raise MissingSoundFileException

        object = self.createActiveObject()
        bpy.context.scene.frame_current = 0
        bpy.context.area.type = "GRAPH_EDITOR"

        bpy.ops.graph.sound_bake(
            filepath = filepath,
            low = self.low,
            high = self.high,
            attack = self.attack,
            release = self.release)

        if useUnpacking:
            os.remove(filepath)

        bakeItem = self.getEmptyBakeItem()
        fcurve = getSingleFCurveWithDataPath(object, "location")
        for sample in fcurve.sampled_points:
            sampleItem = bakeItem.samples.add()
            sampleItem.strength = sample.co.y

        bpy.context.scene.objects.unlink(object)
        bpy.data.objects.remove(object)

        return "FINISHED"

    def createActiveObject(self):
        bpy.ops.object.add()
        object = bpy.context.active_object
        object.keyframe_insert(frame = 0, data_path = "location", index = 0)
        return object

    def getEmptyBakeItem(self):
        sound = self.sound
        item = self.getBakeItemWithSameFrequency()
        if not item: item = self.newItem()
        item.samples.clear()
        return item

    def getBakeItemWithSameFrequency(self):
        return getSoundBakeItemFromFrequency(self.sound, self.low, self.high)

    def newItem(self):
        item = self.sound.bakeData.add()
        item.name = "{} - {}".format(self.low, self.high)
        item.low = self.low
        item.high = self.high
        item.attack = self.attack
        item.release = self.release
        return item

def getSoundBakeItemFromFrequency(sound, low, high):
    for item in sound.bakeData:
        if item.low == low and item.high == high:
            return item
    return None

class MissingSoundFileException(Exception):
    pass



# Register
##################################

def registerHandlers():
    bpy.app.handlers.load_post.append(updateSequencerData)

def unregisterHandlers():
    bpy.app.handlers.load_post.remove(updateSequencerData)
