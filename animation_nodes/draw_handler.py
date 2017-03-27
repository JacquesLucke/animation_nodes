import bpy
from collections import defaultdict

drawHandlers = []
registeredHandlersPerEditor = defaultdict(list)

def drawHandler(editorName, regionName):
    def drawHandlerDecorator(function):
        drawHandlers.append((function, editorName, regionName))
        return function

    return drawHandlerDecorator

def register():
    for function, editorName, regionName in drawHandlers:
        editor = getattr(bpy.types, editorName)
        handler = editor.draw_handler_add(function, (), regionName, "POST_PIXEL")
        registeredHandlersPerEditor[editor].append((handler, regionName))

def unregister():
    for editor, handlers in registeredHandlersPerEditor.items():
        for handler, regionName in handlers:
            editor.draw_handler_remove(handler, regionName)
    registeredHandlersPerEditor.clear()
