import bpy
from bpy.app.handlers import persistent

# Make sure that this module reloads before all the others
# otherwise the reload of this module will overwrite the handler lists
__reload_order_index__ = -100

sceneUpdatePostHandlers = []
fileLoadPostHandlers = []
addonLoadPostHandlers = []

def eventHandler(event):
    def eventHandlerDecorator(function):
        if event == "SCENE_UPDATE_POST": sceneUpdatePostHandlers.append(function)
        if event == "FILE_LOAD_POST": fileLoadPostHandlers.append(function)
        if event == "ADDON_LOAD_POST": addonLoadPostHandlers.append(function)
        return function
    return eventHandlerDecorator

addonChanged = False
@persistent
def sceneUpdatePost(scene):
    for handler in sceneUpdatePostHandlers:
        handler(scene)

    global addonChanged
    if addonChanged:
        addonChanged = False
        for handler in addonLoadPostHandlers:
            handler()

@persistent
def loadPost(scene):
    for handler in fileLoadPostHandlers:
        handler()


def registerHandlers():
    bpy.app.handlers.scene_update_post.append(sceneUpdatePost)
    bpy.app.handlers.load_post.append(loadPost)

    global addonChanged
    addonChanged = True

def unregisterHandlers():
    bpy.app.handlers.scene_update_post.remove(sceneUpdatePost)
    bpy.app.handlers.load_post.remove(loadPost)
