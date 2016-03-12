import bpy
from mathutils import Vector

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


def redrawAll():
    for area in iterAreas():
        area.tag_redraw()

def isViewportRendering():
    return any([space.viewport_shade == "RENDERED" for space in iterActiveSpacesByType("VIEW_3D")])


def convertToRegionLocation(region, x, y):
    factor = getDpiFactor()
    x *= factor
    y *= factor
    return Vector(region.view2d.view_to_region(x, y, clip = False))

def getDpiFactor():
    return getDpi() / 72

def getDpi():
    systemPreferences = bpy.context.user_preferences.system
    retinaFactor = getattr(systemPreferences, "pixel_size", 1)
    return systemPreferences.dpi * retinaFactor

def executeInAreaType(areaType):
    def changeAreaTypeDecorator(function):
        def wrapper(*args, **kwargs):
            area = bpy.context.area
            oldType = area.type
            area.type = areaType
            output = function(*args, **kwargs)
            area.type = oldType
            return output
        return wrapper
    return changeAreaTypeDecorator


class PieMenuHelper:
    def draw(self, context):
        pie = self.layout.menu_pie()
        self.drawLeft(pie)
        self.drawRight(pie)
        self.drawBottom(pie)
        self.drawTop(pie)
        self.drawTopLeft(pie)
        self.drawTopRight(pie)
        self.drawBottomLeft(pie)
        self.drawBottomRight(pie)

    def drawLeft(self, layout):
        self.empty(layout)

    def drawRight(self, layout):
        self.empty(layout)

    def drawBottom(self, layout):
        self.empty(layout)

    def drawTop(self, layout):
        self.empty(layout)

    def drawTopLeft(self, layout):
        self.empty(layout)

    def drawTopRight(self, layout):
        self.empty(layout)

    def drawBottomLeft(self, layout):
        self.empty(layout)

    def drawBottomRight(self, layout):
        self.empty(layout)

    def empty(self, layout, text = ""):
        layout.row().label(text)
