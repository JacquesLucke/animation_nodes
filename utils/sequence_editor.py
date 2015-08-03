import bpy
from . path import toAbsolutePath

def getSoundFilePathsInSequencer():
    paths = [toAbsolutePath(sound.filepath, library = sound.library) for sound in getSoundsInSequencer()]
    return list(set(paths))

def getSoundsInSequencer():
    soundSequences = getSoundSequences()
    sounds = [sequence.sound for sequence in soundSequences]
    return list(set(sounds))

def getSoundSequences():
    editor = bpy.context.scene.sequence_editor
    if not editor: return []
    return [sequence for sequence in editor.sequences if sequence.type == "SOUND"]

def getEmptyChannel(editor):
    channels = [False] * 32
    for sequence in editor.sequences:
        channels[sequence.channel - 1] = True
    for channel, isUsed in enumerate(channels):
        if not isUsed: return channel + 1
    return 32

def getOrCreateSequencer():
    scene = bpy.context.scene
    if not scene.sequence_editor:
        scene.sequence_editor_create()
    return scene.sequence_editor
