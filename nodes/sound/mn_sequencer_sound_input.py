import bpy
import os
import math
from mathutils import Vector
from bpy.props import *
from bpy.types import Node
from bpy.app.handlers import persistent
from ... mn_utils import getNode
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... algorithms import interpolation
from ... utils.mn_name_utils import toDataPath
from ... utils.task_manager import TaskManager, Task
from ... utils.sequence_editor import getSoundFilePathsInSequencer, getSoundSequences
from ... utils.fcurve import (getSingleFCurveWithDataPath, 
                              removeFCurveWithDataPath,
                              deselectAllFCurves,
                              newFCurveForCustomProperty,
                              removeCustomProperty)

dataHolderName = "Sound Data Holder"

class BakeFrequencyRange:
    def __init__(self, low = 0, high = 20000):
        self.low = low
        self.high = high

bakeFrequencyRanges = [
    BakeFrequencyRange(0, 20),
    BakeFrequencyRange(20, 40),
    BakeFrequencyRange(40, 80),
    BakeFrequencyRange(80, 250),
    BakeFrequencyRange(250, 600),
    BakeFrequencyRange(600, 2000),
    BakeFrequencyRange(2000, 4000),
    BakeFrequencyRange(4000, 6000),
    BakeFrequencyRange(6000, 8000),
    BakeFrequencyRange(8000, 20000) ]
strengthListLength = len(bakeFrequencyRanges)
    
    
class AdditionalBakeData(bpy.types.PropertyGroup):
    attack = FloatProperty(default = 0.005, description = "Lower values -> faster rising curve", min = 0, max = 2)
    release = FloatProperty(default = 0.2, description = "Lower values -> faster falling curve", min = 0, max = 5)

class mn_SequencerSoundInput(Node, AnimationNode):
    bl_idname = "mn_SequencerSoundInput"
    bl_label = "Sequencer Sound Input"
    
    isBaking = BoolProperty(default = False)
    bakeInfo = StringProperty(default = "")
    bakeProgress = IntProperty(min = 0, max = 100)
    
    bakeData = PointerProperty(type = AdditionalBakeData)
    
    channels = FloatVectorProperty(size = 32, update = nodePropertyChanged, default = [True] + [False] * 31, min = 0)
    displayChannelAmount = IntProperty(default = 3, min = 0, max = 32, description = "Amount of channels displayed inside of the node")
    
    frameTypes = [
        ("OFFSET", "Offset", ""),
        ("ABSOLUTE", "Absolute", "") ]
    frameType = bpy.props.EnumProperty(name = "Frame Type", items = frameTypes, default = "OFFSET")
    
    def init(self, context):
        self.use_custom_color = True
        self.color = (0.4, 0.9, 0.4)
        self.width = 200
        forbidCompiling()
        self.inputs.new("mn_FloatSocket", "Frame")
        self.inputs.new("mn_FloatSocket", "Frequency").number = 0.4
        self.outputs.new("mn_FloatSocket", "Strength")
        self.outputs.new("mn_FloatListSocket", "Strengths")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Frame" : "frame",
                "Frequency" : "frequency"}
                
    def getOutputSocketNames(self):
        return {"Strength" : "strength",
                "Strengths" : "strengths"}
        
    def draw_buttons(self, context, layout):
        row = layout.row(align = True)
        icon = "ERROR" if sequencerData.hasChanged else "FILE_TICK"
        props = row.operator("mn.bake_sounds", icon = icon)
        props.nodeTreeName = self.id_data.name
        props.nodeName = self.name
        props.bakeData.attack = self.bakeData.attack
        props.bakeData.release = self.bakeData.release
        row.operator("mn.clear_baked_data", text = "", icon = "X")
        
        if self.isBaking:
            layout.prop(self, "bakeProgress", text = "Progress", slider = True)
            layout.label(self.bakeInfo, icon = "INFO")
                
        col = layout.column(align = True)   
        for i in range(self.displayChannelAmount):
            col.prop(self, "channels", index = i, text = "Channel {}".format(i+1))
            
        layout.prop(self, "frameType")
            
    def draw_buttons_ext(self, context, layout):
        col = layout.column(align = True)
        col.prop(self.bakeData, "attack", text = "Attack Time")
        col.prop(self.bakeData, "release", text = "Release Time")
        
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
        strength = self.getFrequencyStrength(strengths, frequency)
        return strength, list(strengths)
        
    def getFrequencyStrength(self, strengthList, frequencyIndicator):
        frequencyIndicator *= strengthListLength
        lower = strengthList[max(min(math.floor(frequencyIndicator), strengthListLength - 1), 0)]
        upper = strengthList[max(min(math.ceil(frequencyIndicator), strengthListLength - 1), 0)]
        influence = frequencyIndicator % 1.0
        influence = interpolation.quadraticInOut(influence)
        return lower * (1 - influence) + upper * influence
        
        
    
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
        dataHolder = getDataHolder()
        
        for i, frequencyRange in enumerate(bakeFrequencyRanges):
            bakeID = toBakeID(sequence.sound.filepath, frequencyRange)
            path = toDataPath(bakeID)
            fcurve = getSingleFCurveWithDataPath(dataHolder, path, storeInCache = False)
            if not fcurve: continue
            if not getattr(fcurve, "is_valid", False): continue
            for frame in range(sequence.frame_final_start, sequence.frame_final_end + 1):
                soundFrame = frame - sequence.frame_start
                self.frames[frame][i] += fcurve.evaluate(soundFrame)
        
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

class ClearBakedData(bpy.types.Operator):
    bl_idname = "mn.clear_baked_data"
    bl_label = "Clear Baked Data"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        dataHolder = getDataHolder()
        for key, value in dataHolder.items():
            if key.startswith("SOUND"):
                removeCustomProperty(dataHolder, key)
        sequencerData.reset()
        return {"FINISHED"}
        
        
class BakeSounds(bpy.types.Operator):
    bl_idname = "mn.bake_sounds"
    bl_label = "Bake Sounds"
    bl_description = "Bake all sounds which are used in the sequence editor (hold CTRL to rebake existing data)"
    bl_options = {"REGISTER"}
    
    nodeTreeName = StringProperty()
    nodeName = StringProperty()
    
    bakeData = PointerProperty(type = AdditionalBakeData)
    
    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        self.timer = context.window_manager.event_timer_add(0.001, context.window)
        self.createTasks(rebake = event.ctrl)
        return {"RUNNING_MODAL"}
        
    def createTasks(self, rebake):
        self.taskManager = TaskManager()
        filepaths = getSoundFilePathsInSequencer()
        for path in filepaths:
            for bakeFrequencyRange in bakeFrequencyRanges:
                waitTask = WaitTask(25)
                bakeTask = BakeFrequencyTask(path, bakeFrequencyRange, self.bakeData, rebake)
                if rebake or not bakeTask.bakedDataExists:
                    self.taskManager.appendTasks(waitTask, bakeTask)
        
    def modal(self, context, event):
        if event.type == "ESC": return self.finish()
        
        status = self.taskManager.execute(event)
        description = self.taskManager.nextDescription
        context.area.type = "NODE_EDITOR"
        
        node = getNode(self.nodeTreeName, self.nodeName)
        node.isBaking = True
        node.bakeInfo = description
        node.bakeProgress = self.taskManager.percentage * 100
        
        context.area.type = "NODE_EDITOR"
        context.area.tag_redraw()
        
        return {"RUNNING_MODAL"} if status == "CONTINUE" else self.finish()
    
    def finish(self):
        node = getNode(self.nodeTreeName, self.nodeName)
        node.isBaking = False
        bpy.context.window_manager.event_timer_remove(self.timer)
        sequencerData.update()
        return {"FINISHED"}
        
        
        
# Tasks for task manager
###########################        
        
class WaitTask(Task):
    def __init__(self, timeSteps):
        self.amount = timeSteps
        
    def execute(self, event):
        if event.type == "TIMER":
            self.amount -= 1
        return "FINISHED" if self.amount == 0 else "CONTINUE"
        
class BakeFrequencyTask(Task):
    def __init__(self, filepath, bakeFrequencyRange, bakeData, rebake = False):
        self.timeWeight = 100
        self.filepath = filepath
        self.bakeFrequencyRange = bakeFrequencyRange
        self.bakeID = toBakeID(filepath, bakeFrequencyRange)
        self.description = "{} : {} - {}".format(os.path.basename(filepath), bakeFrequencyRange.low, bakeFrequencyRange.high)
        self.bakeData = bakeData
        self.rebake = rebake
        
    @property
    def bakedDataExists(self):
        dataHolder = getDataHolder()
        return self.bakeID in dataHolder
        
    def execute(self, event):
        dataHolder = getDataHolder()
        makeAloneVisibleInGraphEditor(dataHolder)
        deselectAllFCurves(dataHolder)
        newFCurveForCustomProperty(dataHolder, self.bakeID, 0.0)
        self.setValidContext()
        
        bpy.ops.graph.sound_bake(
            filepath = self.filepath,
            low = self.bakeFrequencyRange.low,
            high = self.bakeFrequencyRange.high,
            attack = self.bakeData.attack,
            release = self.bakeData.release)
            
        dataHolder.hide = True
        bpy.context.scene.objects.active = None
        return "FINISHED"
        
    def setValidContext(self):
        bpy.context.scene.frame_current = 0
        bpy.context.area.type = "GRAPH_EDITOR"
        
        
        
# Utils
###########################          
          
def getDataHolder():
    object = bpy.context.scene.objects.get(dataHolderName)
    if object: return object
    object = bpy.data.objects.get(dataHolderName)
    if not object: object = bpy.data.objects.new(dataHolderName, None)
    bpy.context.scene.objects.link(object)
    return object
    
def toBakeID(filepath, bakeFrequencyRange):
    # must not be longer than 63 characters
    # changing this requires rebaking in all files
    return "SOUND" + os.path.basename(filepath)[-40:] + str(bakeFrequencyRange.low) + "-" + str(bakeFrequencyRange.high)    
    
def makeAloneVisibleInGraphEditor(object):
    bpy.ops.object.select_all(action = "DESELECT")
    object.hide_select = False
    object.hide = False
    object.select = True
    bpy.context.scene.objects.active = object    

    

# Register
################################## 

def register_handlers():    
    bpy.app.handlers.load_post.append(updateSequencerData)
    
def unregister_handlers():
    bpy.app.handlers.load_post.remove(updateSequencerData)       