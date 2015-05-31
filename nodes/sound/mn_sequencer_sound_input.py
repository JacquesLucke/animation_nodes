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

bakeFrequencies = [(50, 150), (150, 300)]

class mn_SequencerSoundInput(Node, AnimationNode):
    bl_idname = "mn_SequencerSoundInput"
    bl_label = "Sequencer Sound Input"
    
    def init(self, context):
        self.use_custom_color = True
        self.color = (0.4, 0.9, 0.4)
        self.width = 400
        
    def getInputSocketNames(self):
        return {}
    def getOutputSocketNames(self):
        return {}
        
    def draw_buttons(self, context, layout):
        
        frame = context.scene.frame_current
        
        soundSequences = getSoundSequences()
        for sequence in soundSequences:
            if sequence.frame_final_start <= frame <= sequence.frame_final_end:
                layout.label("{} - Frame: {}".format(sequence.name, frame - sequence.frame_start))
                
        self.callFunctionFromUI(layout, "bakeSoundsInSequencer", text = "Bake Sounds")
        self.callFunctionFromUI(layout, "clearBakedData", text = "Clear Baked Data")
                
    def bakeSoundsInSequencer(self):
        sounds = self.getSoundsInSequencer()
        for sound in sounds:
            self.removeBakedData(sound)
            self.bakeSound(sound)
            
    def getSoundsInSequencer(self):
        soundSequences = getSoundSequences()
        sounds = [sequence.sound for sequence in soundSequences]
        return list(set(sounds))
        
    def removeBakedData(self, sound):
        dataHolder = self.getDataHolder()
                
    def bakeSound(self, sound):
        for minFrequency, maxFrequency in bakeFrequencies:
            bakeID = self.getBakeID(sound, minFrequency, maxFrequency)
            self.prepareBaking(bakeID)
            bpy.ops.graph.sound_bake(
                filepath = sound.filepath,
                low = minFrequency,
                high = maxFrequency)
            self.finishBaking()
        
    def prepareBaking(self, bakeID):
        bpy.ops.object.select_all(action = "DESELECT")
        dataHolder = self.getDataHolder()
        dataHolder.hide = False
        dataHolder.select = True
        deselectAllFCurves(dataHolder)
        self.removeBakeID(dataHolder, bakeID)
        dataHolder[bakeID] = 0.5
        dataHolder.keyframe_insert(frame = 0, data_path = toDataPath(bakeID))
        
        context = bpy.context
        context.scene.frame_current = 0
        context.scene.objects.active = dataHolder
        context.area.type = "GRAPH_EDITOR"
        
    def removeBakeID(self, dataHolder, bakeID):
        if bakeID in dataHolder:
            del dataHolder[bakeID]
            removeFCurveWithDataPath(dataHolder, toDataPath(bakeID))
        
    def finishBaking(self):
        context = bpy.context
        context.area.type = "NODE_EDITOR"
        
    def clearBakedData(self):
        dataHolder = self.getDataHolder()
        for key, value in dataHolder.items():
            if key.startswith("SOUND"):
                self.removeBakeID(dataHolder, key)
                
    def getDataHolder(self):
        object = bpy.context.scene.objects.get(dataHolderName)
        if object: return object
        object = bpy.data.objects.get(dataHolderName)
        if not object: object = bpy.data.objects.new(dataHolderName, None)
        bpy.context.scene.objects.link(object)
        return object
        
    def getBakeID(self, sound, minFrequency, maxFrequency):
        return "SOUND" + sound.name + str(minFrequency) + "-" + str(maxFrequency)
        
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