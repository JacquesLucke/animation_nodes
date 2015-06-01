import bpy

def getSoundFilePathsInSequencer():
    paths = [sound.filepath for sound in getSoundsInSequencer()]
    return list(set(paths))
    
def getSoundsInSequencer():
    soundSequences = getSoundSequences()
    sounds = [sequence.sound for sequence in soundSequences]
    return list(set(sounds))      

def getSoundSequences():
    editor = bpy.context.scene.sequence_editor
    if not editor: return []
    return [sequence for sequence in editor.sequences if sequence.type == "SOUND"] 