import bpy
from . handlers import eventHandler

enableSelectionSorting = True
sortedSelectionNames = []

def getSortedSelectedObjects():
    objects = []
    for name in getSortedSelectedObjectNames():
        objects.append(bpy.data.objects.get(name))
    return objects

def getSortedSelectedObjectNames():
    return sortedSelectionNames

@eventHandler("ALWAYS")
def updateSelectionSorting():
    global sortedSelectionNames

    selectedNames = getSelectedObjectNames()

    if enableSelectionSorting:
        newSortedSelection = []

        selectedNamesSet = set(selectedNames)
        for name in sortedSelectionNames:
            if name in selectedNamesSet:
                newSortedSelection.append(name)

        for name in selectedNames:
            if name not in newSortedSelection:
                newSortedSelection.append(name)

        sortedSelectionNames = newSortedSelection
    else:
        sortedSelectionNames = selectedNames

def getSelectedObjectNames():
    viewLayer = bpy.data.window_managers[0].windows[0].view_layer
    return [obj.name for obj in viewLayer.objects if obj.select_get(view_layer = viewLayer)]
