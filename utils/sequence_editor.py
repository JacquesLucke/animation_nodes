import bpy
from . path import toAbsolutePath

def getEmptyChannel(editor):
    channels = [False] * 32
    for sequence in editor.sequences:
        channels[sequence.channel - 1] = True
    for channel, isUsed in enumerate(channels):
        if not isUsed: return channel + 1
    return 32

def getOrCreateSequencer(scene):
    if not scene.sequence_editor:
        scene.sequence_editor_create()
    return scene.sequence_editor
