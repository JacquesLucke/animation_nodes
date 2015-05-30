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

class mn_SoundStripManager(Node, AnimationNode):
    bl_idname = "mn_SoundStripManager"
    bl_label = "Sound Strip Manager"
    
    filepath = StringProperty()
    
    def init(self, context):
        self.use_custom_color = True
        self.color = (0.4, 0.9, 0.4)
        self.width = 400
        
    def getInputSocketNames(self):
        return {}
    def getOutputSocketNames(self):
        return {}
        
    def draw_buttons(self, context, layout):
        if self.filepath == "":
            col = layout.column()
            col.scale_y = 1.5
            self.callFunctionFromUI(col, "loadNewSound", text = "Load", description = "Choose a sound file with the file browser and load it", icon = "IMPORT")
            
            pathsInOtherNodes = getAttributesFromNodesWithType("mn_SoundStripManager", "filepath")
            
            for sequence in getSoundSequences():
                path = sequence.sound.filepath
                if path not in pathsInOtherNodes:
                    props = layout.operator("mn.set_sound_path_on_node", text = sequence.sound.name)
                    props.nodeTreeName = self.id_data.name
                    props.nodeName = self.name
                    props.path = sequence.sound.filepath
        
        if self.filepath != "":
            layout.label(self.filename)
            
        return
        
        self.callFunctionFromUI(layout, "autoSetEndFrame", text = "Set End Frame", description = "Set the end frame based on the last frame of all loaded sound sequences")
        self.callFunctionFromUI(layout, "cacheSounds", text = "Cache Sounds", description = "Load the sounds into RAM for faster and better timed playback")
        
        sequence = self.getSoundSequence()
        if not sequence: return
        layout.prop(sequence, "name")
        layout.prop(sequence, "mute")
            
    def getSoundSequence(self):
        sequences = getSoundSequences()
        for sequence in sequences:
            if sequence.sound.filepath == self.filepath:
                return sequence
        return None
        
    def loadNewSound(self):
        bpy.ops.mn.load_sound_file("INVOKE_DEFAULT", nodeTreeName = self.id_data.name, nodeName = self.name)
        
    def loadSoundFile(self, filepath):
        self.filepath = filepath
        editor = getSequenceEditor()
        channel = getEmptyChannel(editor)
        sound = editor.sequences.new_sound(self.filename, filepath, channel, 1)
        
        
    @property
    def filename(self):
        return os.path.basename(self.filepath)
        
    def autoSetEndFrame(self):
        sequences = getSoundSequences()
        if len(sequences) == 0: return
        
        scene = bpy.context.scene
        lastSequenceFrame = max([sequence.frame_final_end for sequence in sequences])
        minEndFrame = scene.frame_start + 1
        scene.frame_end = max(minEndFrame, lastSequenceFrame)
        
    def cacheSounds(self):
        sequences = getSoundSequences()
        sounds = list(set([sequence.sound for sequence in sequences]))
        for sound in sounds:
            if not sound.use_memory_cache:
                sound.use_memory_cache = True
             
    def copy(self, node):
        self.filepath = ""
        
        
class LoadSoundFile(bpy.types.Operator):
    bl_idname = "mn.load_sound_file"
    bl_label = "Load Sound File"
    
    nodeTreeName = bpy.props.StringProperty()
    nodeName = bpy.props.StringProperty()
    filepath = bpy.props.StringProperty(subtype = "FILE_PATH")
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return { 'RUNNING_MODAL' }
        
    def execute(self, context):
        node = getNode(self.nodeTreeName, self.nodeName)
        path = self.filepath
        if any([path.endswith(extension) for extension in soundFileTypes]):
            node.loadSoundFile(self.filepath)
        else:
            raise Exception("No valid file name extension")
        return {'FINISHED'}

        
class RemoveSoundSequence(bpy.types.Operator):
    bl_idname = "mn.remove_sound_sequence"
    bl_label = "Remove Sound Sequence"
    
    path = bpy.props.StringProperty()
        
    def execute(self, context):
        editor = getSequenceEditor()
        for sequence in sequences:
            if sequence.sound.filepath == self.path:
                sounds = sequence.sound
                editor.sequences.remove(sequence)
        if sound.users == 0:
            bpy.data.sounds.remove(sound)
        return {'FINISHED'}
        
class SetSoundPathOnNode(bpy.types.Operator):
    bl_idname = "mn.set_sound_path_on_node"
    bl_label = "Set sound path"
    
    nodeTreeName = bpy.props.StringProperty()
    nodeName = bpy.props.StringProperty()
    
    path = bpy.props.StringProperty()
        
    def execute(self, context):
        node = getNode(self.nodeTreeName, self.nodeName)
        node.filepath = self.path
        return {'FINISHED'}


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