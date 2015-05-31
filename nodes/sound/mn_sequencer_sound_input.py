import bpy
import os
from bpy.props import *
from bpy.types import Node
from ... mn_utils import getNode
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... utils.mn_node_utils import getAttributesFromNodesWithType

# https://developer.blender.org/diffusion/B/browse/master/source/blender/imbuf/intern/util.c;23c7d14afdb0e5b6d56d4776b487bff6ab5d232c$165
soundFileTypes = ["wav", "ogg", "oga", "mp3", "mp2", "ac3", "aac", "flac", "wma", "eac3", "aif", "aiff", "m4a", "mka"]

dataHolderName = "Sound Data Holder"

class BakeSetting:
    def __init__(self, low = 0, high = 20000):
        self.low = low
        self.high = high

bakeSettings = [
    BakeSetting(0, 20),
    BakeSetting(20, 40),
    BakeSetting(40, 80),
    BakeSetting(80, 250),
    BakeSetting(250, 600),
    BakeSetting(600, 4000),
    BakeSetting(4000, 6000),
    BakeSetting(6000, 8000),
    BakeSetting(8000, 20000) ]
    

class mn_SequencerSoundInput(Node, AnimationNode):
    bl_idname = "mn_SequencerSoundInput"
    bl_label = "Sequencer Sound Input"
    
    isBaking = BoolProperty(default = False)
    bakeInfo = StringProperty(default = "")
    bakeProgress = IntProperty(min = 0, max = 100)
    
    channels = FloatVectorProperty(size = 32, update = nodePropertyChanged, default = [True] + [False] * 31)
    displayChannelAmount = IntProperty(default = 3, min = 0, max = 32)
    
    def init(self, context):
        self.use_custom_color = True
        self.color = (0.4, 0.9, 0.4)
        self.width = 400
        forbidCompiling()
        self.inputs.new("mn_FloatSocket", "Frame")
        self.inputs.new("mn_IntegerSocket", "Frequency")
        self.outputs.new("mn_FloatSocket", "Strength")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Frame" : "frame",
                "Frequency" : "frequency"}
                
    def getOutputSocketNames(self):
        return {"Strength" : "strength"}
        
    def draw_buttons(self, context, layout):
        row = layout.row(align = True)
        
        props = row.operator("mn.bake_sounds")
        props.nodeTreeName = self.id_data.name
        props.nodeName = self.name
        
        row.operator("mn.clear_baked_data", text = "", icon = "X")
        
        if self.isBaking:
            layout.prop(self, "bakeProgress", text = "Progress", slider = True)
            layout.label(self.bakeInfo, icon = "INFO")
                
        col = layout.column(align = True)   
        for i in range(self.displayChannelAmount):
            col.prop(self, "channels", index = i, text = "Channel {}".format(i+1))
            
    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "displayChannelAmount")
        
    def execute(self, frame, frequency):
        strength = 0
        for sequence in getSoundSequences():
            if sequence.frame_final_start <= frame <= sequence.frame_final_end:
                strength += bakedData.getSoundStrength(sequence, frame - sequence.frame_start, frequency)
        return strength
    
from ... utils.fcurve import getSingleValueAtFrame        
        
class BakedData:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.sequenceData = {}
        self.fileBakeData = {}
        
    def update(self):
        self.reset()
        
        paths = getSoundFilePathsInSequencer()
        for path in paths:
            self.fileBakeData[path] = FileBakeData(path)
        
        soundSequences = getSoundSequences()
        for sequence in soundSequences:
            self.sequenceData[sequence.name] = self.fileBakeData[sequence.sound.filepath]
            
    def getSoundStrength(self, sequence, frame, frequency):
        fileData = self.sequenceData.get(sequence.name)
        if not fileData: return 0.0
        dataHolder = getDataHolder()
        bakeSetting = bakeSettings[frequency]
        dataPath = toDataPath(getBakeID(sequence.sound.filepath, bakeSetting))
        return getSingleValueAtFrame(dataHolder, dataPath, frame)
            
class FileBakeData:
    def __init__(self, filepath):
        self.bakeIDs = []
        for bakeSetting in bakeSettings:
            self.bakeIDs.append(getBakeID(filepath, bakeSetting))
            
bakedData = BakedData()             
        

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
        return {"FINISHED"}
        
class BakeSounds(bpy.types.Operator):
    bl_idname = "mn.bake_sounds"
    bl_label = "Bake Sounds"
    bl_description = "Bake all sounds which are used in the sequence editor (hold CTRL to rebake existing data)"
    bl_options = {"REGISTER"}
    
    nodeTreeName = StringProperty()
    nodeName = StringProperty()
        
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
    
    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        
        rebake = event.ctrl
        
        tm = TaskManager()
        
        filepaths = getSoundFilePathsInSequencer()
        for path in filepaths:
            for bakeSetting in bakeSettings:
                waitTask = WaitTask(25)
                bakeTask = BakeFrequencyTask(path, bakeSetting, rebake)
                if rebake or not bakeTask.bakedDataExists:
                    tm.appendTasks(waitTask, bakeTask)
        
        self.taskManager = tm
        
        self.timer = context.window_manager.event_timer_add(0.001, context.window)
        
        return {"RUNNING_MODAL"}
        
    def finish(self):
        node = getNode(self.nodeTreeName, self.nodeName)
        node.isBaking = False
        bpy.context.window_manager.event_timer_remove(self.timer)
        bakedData.update()
        return {"FINISHED"}
        
        
        
class TaskManager:
    def __init__(self):
        self._tasks = []
        self.taskIndex = 0
        
    def appendTask(self, task):
        self.tasks.append(task)
        
    def appendTasks(self, *tasks):
        self._tasks.extend(tasks)
        
    def execute(self, event):
        if self.isFinished:
            return "FINISHED"
            
        task = self._tasks[self.taskIndex]
        status = task.execute(event)
        if status == "FINISHED":
            self.taskIndex += 1
            
        return "FINISHED" if self.isFinished else "CONTINUE"
            
    @property
    def isFinished(self):
        return self.taskIndex >= len(self._tasks)
        
    @property
    def nextDescription(self):
        for task in self._tasks[self.taskIndex:]:
            if task.description != "":
                return task.description
        return ""
        
    @property
    def percentage(self):
        totalTimeWeigth = self.getTotalTimeWeight()
        if totalTimeWeigth == 0: return 0
        return self.getTimeWeight(end = self.taskIndex) / self.getTotalTimeWeight()
        
    def getTotalTimeWeight(self):
        return self.getTimeWeight(end = len(self._tasks))
        
    def getTimeWeight(self, start = 0, end = 0):
        weight = 0
        for task in self._tasks[start:end]:
            weight += task.timeWeight
        return weight
         
         
class Task:
    def execute(self, event):
        return "FINISHED"
    def __getattr__(self, name):
        if name == "description":
            return ""
        if name == "timeWeight":
            return 1
        
class WaitTask(Task):
    def __init__(self, timeSteps):
        self.amount = timeSteps
        
    def execute(self, event):
        if event.type == "TIMER":
            self.amount -= 1
        return "FINISHED" if self.amount == 0 else "CONTINUE"
        
class BakeFrequencyTask(Task):
    def __init__(self, filepath, bakeSetting, rebake = False):
        self.timeWeight = 20
        self.filepath = filepath
        self.bakeSetting = bakeSetting
        self.bakeID = getBakeID(filepath, bakeSetting)
        self.description = "{} : {} - {}".format(os.path.basename(filepath), bakeSetting.low, bakeSetting.high)
        self.rebake = rebake
        
    @property
    def bakedDataExists(self):
        dataHolder = getDataHolder()
        return self.bakeID in dataHolder
        
    def execute(self, event):
        dataHolder = getDataHolder()
        selectOnly(dataHolder)
        deselectAllFCurves(dataHolder)
        newFCurveForCustomFloatProperty(dataHolder, self.bakeID)
        self.setValidContext()
        bpy.ops.graph.sound_bake(
            filepath = self.filepath,
            low = self.bakeSetting.low,
            high = self.bakeSetting.high)
        return "FINISHED"
        
    def setValidContext(self):
        bpy.context.scene.frame_current = 0
        bpy.context.area.type = "GRAPH_EDITOR"
        
        
def selectOnly(object):
    bpy.ops.object.select_all(action = "DESELECT")
    object.select = True
    object.hide = False
    bpy.context.scene.objects.active = object
        
def newFCurveForCustomFloatProperty(object, name):
    removeCustomProperty(object, name)
    object[name] = 0.5
    object.keyframe_insert(frame = 0, data_path = toDataPath(name))
        
def removeCustomProperty(object, name):
    if name in object:
        del object[name]
        removeFCurveWithDataPath(object, toDataPath(name))
        
        
        
def getBakeID(filepath, bakeSetting):
    return "SOUND" + os.path.basename(filepath) + str(bakeSetting.low) + "-" + str(bakeSetting.high)
        
def getDataHolder():
    object = bpy.context.scene.objects.get(dataHolderName)
    if object: return object
    object = bpy.data.objects.get(dataHolderName)
    if not object: object = bpy.data.objects.new(dataHolderName, None)
    bpy.context.scene.objects.link(object)
    return object
    
def getSoundFilePathsInSequencer():
    paths = [sound.filepath for sound in getSoundsInSequencer()]
    return list(set(paths))
    
def getSoundsInSequencer():
    soundSequences = getSoundSequences()
    sounds = [sequence.sound for sequence in soundSequences]
    return list(set(sounds))        
       
        
        
        
def toDataPath(name):
    return '["{}"]'.format(name)

def deselectAllFCurves(object):
    for fcurve in getFCurves(object):
        fcurve.select = False
    
def removeFCurveWithDataPath(object, datapath):
    foundFCurve = None
    for fcurve in getFCurves(object):
        if fcurve.data_path == datapath:
            foundFCurve = fcurve
            break
    if foundFCurve:
        object.animation_data.action.fcurves.remove(fcurve)
        
def getFCurves(object):
    try: return object.animation_data.action.fcurves
    except: return []
        
def getEmptyChannel(editor):
    channels = [True] * 32
    for sequence in editor.sequences:
        channels[sequence.channel - 1] = False
    for i, channel in enumerate(channels):
        if channel:
            return i + 1
    raise Exception("No free sequencer channel")

def getSoundSequences():
    editor = bpy.context.scene.sequence_editor
    if not editor: return []
    return [sequence for sequence in editor.sequences if sequence.type == "SOUND"]
        
def getSequenceEditor():
    scene = bpy.context.scene
    if not scene.sequence_editor:
        scene.sequence_editor_create()
    return scene.sequence_editor         