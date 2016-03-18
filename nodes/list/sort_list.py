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

    @staticmethod
    def setup(node):
        pass

    @staticmethod
    def sort(inList, reverseOutput, *args):
        '''Returns either the sorted list or an error message'''
        return []



# Object List Sorting
##################################################

class SortObjectListWithDirectionTemplate(bpy.types.PropertyGroup, SortingTemplate):
    identifier = "SORT_OBJECT_LIST_WITH_DIRECTION"
    dataType = "Object List"
    label = "Direction"

    @staticmethod
    def setup(node):
        node.inputs.new("an_VectorSocket", "Direction", "direction")

    @staticmethod
    def sort(objects, reverse, direction):
        if not all(objects): return "List elements must not be None"

        distance = distance_point_to_plane
        return sorted(objects,
            reverse = reverse,
            key = lambda x: distance(x.location, (0, 0, 0), direction))

class SortObjectListByNameTemplate(bpy.types.PropertyGroup, SortingTemplate):
    identifier = "SORT_OBJECT_LIST_BY_NAME"
    dataType = "Object List"
    label = "Name"

    @staticmethod
    def sort(objects, reverse):
        if not all(objects): return "List elements must not be None"

        return sorted(objects,
            reverse = reverse,
            key = lambda x: x.name)

class SortObjectListByPointDistanceTemplate(bpy.types.PropertyGroup, SortingTemplate):
    identifier = "SORT_OBJECT_LIST_BY_POINT_DISTANCE"
    dataType = "Object List"
    label = "Point Distance"

    @staticmethod
    def setup(node):
        node.inputs.new("an_VectorSocket", "Point", "point")

    @staticmethod
    def sort(objects, reverse, point):
        if not all(objects): return "List elements must not be None"

        return sorted(objects,
            reverse = reverse,
            key = lambda x: (x.location - point).length)



# Collect templates in a property group
##################################################

class SortingTemplates(bpy.types.PropertyGroup):
    bl_idname = "an_SortingTemplatesGroup"

    templateByIdentifier = dict()
    templatesByDataType = defaultdict(list)

    def getTemplates(self, dataType):
        return self.templatesByDataType[dataType] + self.templatesByDataType["All"]

    def getTemplate(self, identifier):
        return self.templateByIdentifier[identifier]

for template in SortingTemplate.__subclasses__():
    SortingTemplates.templateByIdentifier[template.identifier] = template
    SortingTemplates.templatesByDataType[template.dataType].append(template)
    setattr(SortingTemplates, template.identifier, PointerProperty(type = template))



# Actual Node
###################################################

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
        for template in self.templates.getTemplates(self.assignedType):
            items.append({"value" : template.identifier, "name" : template.label})
        return enumItemsFromDicts(items)

    def sortTypeChanged(self, context):
        self.generateSockets()

    sortType = EnumProperty(name = "Sort Type", update = sortTypeChanged,
        items = getSortTypeItems)

    sortKey = StringProperty(update = executionCodeChanged, default = "e")

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

        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def drawAdvanced(self, layout):
        layout.prop(self, "elementName")

    def getExecutionCode(self):
        if self.sortType == "CUSTOM":
            yield from self.iterCustomSortingLines()
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
        self.sortType = "CUSTOM"

    @keepNodeState
    def generateSockets(self):
        self.inputs.clear()
        self.outputs.clear()
        self.inputs.new(self.listIdName, "List", "inList").dataIsModified = True
        self.inputs.new("an_BooleanSocket", "Reverse", "reverseOutput").value = False
        self.outputs.new(self.listIdName, "Sorted List", "outList")

        self.setupActiveTemplate()

    def setupActiveTemplate(self):
        template = self.activeTemplate
        if template is not None:
            template.setup(self)

    @property
    def activeTemplate(self):
        if self.sortType == "CUSTOM": return None
        return self.templates.getTemplate(self.sortType)
