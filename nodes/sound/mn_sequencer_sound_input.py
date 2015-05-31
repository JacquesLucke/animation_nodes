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

bakeFrequencies = [
    (0, 20),
    (20, 40),
    (40, 80),
    (80, 250),
    (250, 600),
    (600, 4000),
    (4000, 6000),
    (6000, 8000),
    (8000, 20000) ]

class mn_SequencerSoundInput(Node, AnimationNode):
    bl_idname = "mn_SequencerSoundInput"
    bl_label = "Sequencer Sound Input"
    
    isBaking = BoolProperty(default = False)
    bakeInfo = StringProperty(default = "")
    bakeProgress = IntProperty(min = 0, max = 100)
    
    def init(self, context):
        self.use_custom_color = True
        self.color = (0.4, 0.9, 0.4)
        self.width = 400
        
    def getInputSocketNames(self):
        return {}
    def getOutputSocketNames(self):
        return {}
        
    def draw_buttons(self, context, layout):
    
        props = layout.operator("mn.bake_sounds")
        props.nodeTreeName = self.id_data.name
        props.nodeName = self.name
        
        if self.isBaking:
            layout.prop(self, "bakeProgress", text = "Progress", slider = True)
            layout.label(self.bakeInfo, icon = "INFO")
        self.callFunctionFromUI(layout, "clearBakedData", text = "Clear Baked Data")
        
    def clearBakedData(self):
        dataHolder = getDataHolder()
        for key, value in dataHolder.items():
            if key.startswith("SOUND"):
                removeCustomProperty(dataHolder, key)
                
    
        
def getBakeID(filepath, minFrequency, maxFrequency):
    return "SOUND" + os.path.basename(filepath) + str(minFrequency) + "-" + str(maxFrequency)
        
def getDataHolder():
    object = bpy.context.scene.objects.get(dataHolderName)
    if object: return object
    object = bpy.data.objects.get(dataHolderName)
    if not object: object = bpy.data.objects.new(dataHolderName, None)
    bpy.context.scene.objects.link(object)
    return object
    
def getSoundsInSequencer():
    soundSequences = getSoundSequences()
    sounds = [sequence.sound for sequence in soundSequences]
    return list(set(sounds))    
        
        
class BakeSounds(bpy.types.Operator):
    bl_idname = "mn.bake_sounds"
    bl_label = "Bake Sounds"
    bl_description = ""
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
        
        tm = TaskManager()
        
        sounds = getSoundsInSequencer()
        for sound in sounds:
            for low, high in bakeFrequencies:
                waitTask = WaitTask(20)
                bakeTask = BakeFrequencyTask(sound.filepath, low, high)
                tm.appendTasks(waitTask, bakeTask)
        
        self.taskManager = tm
        
        self.timer = context.window_manager.event_timer_add(0.001, context.window)
        
        return {"RUNNING_MODAL"}
        
    def finish(self):
        node = getNode(self.nodeTreeName, self.nodeName)
        node.isBaking = False
        bpy.context.window_manager.event_timer_remove(self.timer)
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
    def __init__(self, filepath, lowFrequency, highFrequency):
        self.timeWeight = 20
        self.filepath = filepath
        self.lowFrequency = lowFrequency
        self.highFrequency = highFrequency
        self.bakeID = getBakeID(filepath, lowFrequency, highFrequency)
        self.description = "{} : {} - {}".format(os.path.basename(filepath), lowFrequency, highFrequency)
        
    def execute(self, event):
        dataHolder = getDataHolder()
        selectOnly(dataHolder)
        deselectAllFCurves(dataHolder)
        newFCurveForCustomFloatProperty(dataHolder, self.bakeID)
        self.setValidContext()
        bpy.ops.graph.sound_bake(
            filepath = self.filepath,
            low = self.lowFrequency,
            high = self.highFrequency)
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