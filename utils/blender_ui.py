import bpy

def getAreaWithType(type):
    for area in iterAreasByType(type):
        return area

def iterAreasByType(type):
    for area in iterAreas():
        if area.type == type:
            yield area

def iterAreas():
    for screen in bpy.data.screens:
        for area in screen.areas:
            yield area
