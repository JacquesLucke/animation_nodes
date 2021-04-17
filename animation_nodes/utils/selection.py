import bpy

sortedSelectionNames = []

def getSortedSelectedObjects():
    objects = []
    for name in getSortedSelectedObjectNames():
        objects.append(bpy.data.objects.get(name))
    return objects

def getSortedSelectedObjectNames():
    return sortedSelectionNames

def updateSelectionSorting(viewLayer):
    global sortedSelectionNames

    selectedNames = getSelectedObjectNames(viewLayer)

    newSortedSelection = []

    selectedNamesSet = set(selectedNames)
    for name in sortedSelectionNames:
        if name in selectedNamesSet:
            newSortedSelection.append(name)

    for name in selectedNames:
        if name not in newSortedSelection:
            newSortedSelection.append(name)

    sortedSelectionNames = newSortedSelection

def getSelectedObjectNames(viewLayer):
    return [obj.name for obj in viewLayer.objects if obj.select_get(view_layer = viewLayer)]

def getSelectedObjects(viewLayer):
    return [obj for obj in viewLayer.objects if obj.select_get(view_layer = viewLayer)]

def getActiveObject(viewLayer):
    return viewLayer.objects.active
