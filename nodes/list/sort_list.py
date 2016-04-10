import bpy
from bpy.props import *
from collections import defaultdict
from ... utils.code import isCodeValid
from ... tree_info import keepNodeState
from ... utils.names import toVariableName
from ... events import executionCodeChanged
from ... sockets.info import toIdName, isList
from ... base_types.node import AnimationNode
from ... utils.enum_items import enumItemsFromDicts
from mathutils.geometry import distance_point_to_plane

class SortingTemplate:
    identifier = "NONE"
    dataType = "NONE"
    label = "NONE"

    def setup(self, node):
        pass

    def draw(self, layout):
        pass

    def sort(self, inList, reverseOutput, *args):
        '''Returns either the sorted list or an error message'''
        return []



# Object List Sorting
##################################################

class SortObjectListWithDirectionTemplate(bpy.types.PropertyGroup, SortingTemplate):
    identifier = "OBJECT_LIST__DIRECTION"
    dataType = "Object List"
    label = "Direction"

    useInitialTransforms = BoolProperty(name = "Use Initial Transforms", default = False)

    def setup(self, node):
        node.newInput("an_VectorSocket", "Direction", "direction").value = (0, 0, 1)

    def draw(self, layout):
        layout.prop(self, "useInitialTransforms")

    def sort(self, objects, reverse, direction):
        if not all(objects): return "List elements must not be None"

        distance = distance_point_to_plane
        if self.useInitialTransforms:
            keyFunction = lambda object: distance(object.id_keys.get("Transforms", "Initial Transforms")[0], (0, 0, 0), direction)
        else:
            keyFunction = lambda object: distance(object.location, (0, 0, 0), direction)

        return sorted(objects, key = keyFunction, reverse = reverse)

class SortObjectListByPointDistanceTemplate(bpy.types.PropertyGroup, SortingTemplate):
    identifier = "OBJECT_LIST__POINT_DISTANCE"
    dataType = "Object List"
    label = "Point Distance"

    useInitialTransforms = BoolProperty(name = "Use Initial Transforms", default = False)

    def setup(self, node):
        node.newInput("an_VectorSocket", "Point", "point")

    def draw(self, layout):
        layout.prop(self, "useInitialTransforms")

    def sort(self, objects, reverse, point):
        if not all(objects): return "List elements must not be None"

        if self.useInitialTransforms:
            keyFunction = lambda object: (object.id_keys.get("Transforms", "Initial Transforms")[0] - point).length_squared
        else:
            keyFunction = lambda object: (object.location - point).length_squared

        return sorted(objects, key = keyFunction, reverse = reverse)

class SortObjectListByNameTemplate(bpy.types.PropertyGroup, SortingTemplate):
    identifier = "OBJECT_LIST__NAME"
    dataType = "Object List"
    label = "Name"

    def sort(self, objects, reverse):
        if not all(objects): return "List elements must not be None"

        return sorted(objects, key = lambda x: x.name, reverse = reverse)


# Polygon List Sorting
##################################################

class SortPolygonListWithDirectionTemplate(bpy.types.PropertyGroup, SortingTemplate):
    identifier = "POLYGON_LIST__DIRECTION"
    dataType = "Polygon List"
    label = "Direction"

    def setup(self, node):
        node.newInput("an_VectorSocket", "Direction", "direction").value = (0, 0, 1)

    def sort(self, polygons, reverse, direction):
        distance = distance_point_to_plane
        keyFunction = lambda polygon: distance(polygon.center, (0, 0, 0), direction)
        return sorted(polygons, key = keyFunction, reverse = reverse)



# Collect templates in a property group
##################################################

class SortingTemplates(bpy.types.PropertyGroup):
    bl_idname = "an_SortingTemplatesGroup"

    templateIdentifiersByDataType = defaultdict(list)

    def getTemplates(self, dataType):
        identifiers = self.templateIdentifiersByDataType[dataType]
        return [self.getTemplate(identifier) for identifier in identifiers]

    def getTemplate(self, identifier):
        return getattr(self, identifier)

for template in SortingTemplate.__subclasses__():
    setattr(SortingTemplates, template.identifier, PointerProperty(type = template))
    SortingTemplates.templateIdentifiersByDataType[template.dataType].append(template.identifier)



# Actual Node
###################################################

keyListTypeItems = [
    ("FLOAT", "Float", "", "NONE", 0),
    ("STRING", "String", "", "NONE", 1) ]

class SortListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SortListNode"
    bl_label = "Sort List"
    bl_width_default = 190

    templates = PointerProperty(type = SortingTemplates)

    def assignedTypeChanged(self, context):
        self.listIdName = toIdName(self.assignedType)
        self.generateSockets()

    assignedType = StringProperty(update = assignedTypeChanged)
    listIdName = StringProperty()

    def getSortTypeItems(self, context):
        items = []
        items.append({"value" : "CUSTOM", "name" : "Custom"})
        items.append({"value" : "KEY_LIST", "name" : "Key List"})
        for template in self.templates.getTemplates(self.assignedType):
            items.append({"value" : template.identifier, "name" : template.label})
        return enumItemsFromDicts(items)

    def sortTypeChanged(self, context):
        self.generateSockets()

    sortType = EnumProperty(name = "Sort Type", update = sortTypeChanged,
        items = getSortTypeItems)

    sortKey = StringProperty(update = executionCodeChanged, default = "e")

    keyListType = EnumProperty(name = "Key List Type", default = "FLOAT",
        items = keyListTypeItems, update = sortTypeChanged)

    def elementNameChanged(self, context):
        variableName = toVariableName(self.elementName)
        if variableName != self.elementName:
            self.elementName = variableName
        executionCodeChanged()

    elementName = StringProperty(name = "Element Name", default = "e",
        update = elementNameChanged)

    errorMessage = StringProperty()

    def create(self):
        self.assignedType = "Object List"
        self.sortType = "CUSTOM"

    def draw(self, layout):
        layout.prop(self, "sortType", text = "Type")

        if self.sortType == "CUSTOM":
            col = layout.column(align = True)
            col.label("Key (use {} for the element)".format(repr(self.elementName)))
            col.prop(self, "sortKey", text = "")
        elif self.sortType == "KEY_LIST":
            layout.prop(self, "keyListType", text = "Keys")
        else:
            self.activeTemplate.draw(layout)

        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def drawAdvanced(self, layout):
        layout.prop(self, "elementName")

    def getExecutionCode(self):
        if self.sortType == "CUSTOM":
            yield from self.iterCustomSortingLines()
        elif self.sortType == "KEY_LIST":
            yield from self.iterKeyListSortingLines()
        else:
            yield from self.iterTemplateSortingLines()

    def iterCustomSortingLines(self):
        sortExpression = "sorted(inList, key = lambda {}: {}, reverse = reverseOutput)".format(self.elementName, self.sortKey)
        if isCodeValid(sortExpression):
            self.errorMessage = ""
            yield "try:"
            yield "    outList = " + sortExpression
            yield "    self.errorMessage = ''"
            yield "except:"
            yield "    outList = []"
            yield "    self.errorMessage = str(sys.exc_info()[1])"
        else:
            self.errorMessage = "Invalid Expression"
            yield "outList = inList"

    def iterKeyListSortingLines(self):
        zipExpression = "zip(inList, keyList)"
        sortExpression = "sorted({}, key = lambda item: item[1], reverse = reverseOutput)".format(zipExpression)
        unzipExpression = "[item[0] for item in {}]".format(sortExpression)

        yield "if len(inList) == len(keyList):"
        yield "    try:"
        yield "        outList = {}".format(unzipExpression)
        yield "        self.errorMessage = ''"
        yield "    except:"
        yield "        outList = []"
        yield "        self.errorMessage = str(sys.exc_info()[1])"
        yield "else:"
        yield "    outList = []"
        yield "    self.errorMessage = 'The list lengths are not equal'"

    def iterTemplateSortingLines(self):
        yield "self.errorMessage = ''"
        templateParameters = ", ".join(socket.identifier for socket in self.inputs)
        yield "output = self.activeTemplate.sort({})".format(templateParameters)
        yield "if isinstance(output, list):"
        yield "    outList = output"
        yield "    self.errorMessage = ''"
        yield "else:"
        yield "    outList = []"
        yield "    self.errorMessage = output"

    def edit(self):
        listDataType = self.getWantedDataType()
        self.assignType(listDataType)

    def getWantedDataType(self):
        listInput = self.inputs[0].dataOrigin
        listOutputs = self.outputs[0].dataTargets

        if listInput is not None: return listInput.dataType
        if len(listOutputs) == 1: return listOutputs[0].dataType
        return self.inputs[0].dataType

    def assignType(self, listDataType):
        if not isList(listDataType): return
        if listDataType == self.assignedType: return
        self.assignedType = listDataType

        if self.sortType not in ("CUSTOM", "KEY_LIST"):
            self.sortType = "CUSTOM"

    @keepNodeState
    def generateSockets(self):
        self.inputs.clear()
        self.outputs.clear()
        self.newInput(self.listIdName, "List", "inList").dataIsModified = True
        self.newInput("an_BooleanSocket", "Reverse", "reverseOutput").value = False

        if self.sortType == "KEY_LIST":
            if self.keyListType == "FLOAT":
                self.newInput("an_FloatListSocket", "Key List", "keyList")
            elif self.keyListType == "STRING":
                self.newInput("an_StringListSocket", "Key List", "keyList")

        self.newOutput(self.listIdName, "Sorted List", "outList")

        self.setupActiveTemplate()

    def setupActiveTemplate(self):
        template = self.activeTemplate
        if template is not None:
            template.setup(self)

    @property
    def activeTemplate(self):
        if self.sortType in ("CUSTOM", "KEY_LIST"): return None
        return self.templates.getTemplate(self.sortType)
