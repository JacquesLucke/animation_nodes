import bpy

def iterActiveSpacesByType(type):
    for space in iterActiveSpaces():
        if space.type == type:
            yield space

def iterActiveSpaces():
    for area in iterAreas():
        yield area.spaces.active


def getAreaWithType(type):
    for area in iterAreasByType(type):
        return area

def iterAreasByType(type):
    for area in iterAreas():
        if area.type == type:
            yield area

def iterAreas():
    for screen in iterActiveScreens():
        for area in screen.areas:
            yield area

def iterActiveScreens():
    for windowManager in bpy.data.window_managers:
        for window in windowManager.windows:
            yield window.screen
