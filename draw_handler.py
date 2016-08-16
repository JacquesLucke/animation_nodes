import bpy
import functools
from collections import defaultdict

handlersPerEditor = defaultdict(list)

def drawHandler(editorName, regionName):
    def drawHandlerDecorator(function):
        registerDrawHandler(function, editorName, regionName)

        @functools.wraps(function)
        def wrapper():
            function()
        return wrapper

    return drawHandlerDecorator

def registerDrawHandler(function, editorName, regionName):
    editor = getattr(bpy.types, editorName)
    handler = editor.draw_handler_add(function, (), regionName, "POST_PIXEL")
    handlersPerEditor[editor].append((handler, regionName))

def unregister():
    for editor, handlers in handlersPerEditor.items():
        for handler, regionName in handlers:
            editor.draw_handler_remove(handler, regionName)
