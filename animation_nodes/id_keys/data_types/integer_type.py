import bpy
import random
from bpy.props import *
from mathutils import Vector
from . base import SingleIDKeyDataType
from ... data_structures import LongList
from ... algorithms.lists import naturalSortKey
from ... utils.blender_ui import getDpiFactor, redrawAll
from ... utils.selection import getSortedSelectedObjects

class IntegerDataType(SingleIDKeyDataType):
    identifier = "Integer"
    default = 0

    @classmethod
    def getList(cls, objects, name):
        default = cls.default
        path = cls.getPath(name)
        return LongList.fromValues(getattr(object, path, default) for object in objects)

    @classmethod
    def drawExtras(cls, layout, object, name):
        row = layout.row(align = True)
        props = row.operator("an.id_keys_from_sorted_objects", text = "Sort", icon = "SORTSIZE")
        props.idKeyName = name
        props = row.operator("an.id_keys_integer_offset", text = "Offset", icon="LINENUMBERS_ON")
        props.idKeyName = name

    @classmethod
    def drawCopyMenu(cls, layout, object, name):
        props = layout.operator("an.copy_id_key_to_attribute", text = "to Pass Index")
        props.dataType = "Integer"
        props.propertyName = name
        props.attribute = "pass_index"



# Sorting
###########################################

sortModeItems = [
    ("SELECTION_ORDER", "Selection Order", "", "BORDERMOVE", 0),
    ("NAME", "Object Name", "Sort objects alphanumerically", "SORTALPHA", 1),
    ("DISTANCE", "Distance", "Sort by distance to active object", "FULLSCREEN_ENTER", 2),
    ("RANDOM", "Random", "", "MOD_PARTICLES", 3),
    ("AXIS", "Axis", "", "ORIENTATION_GLOBAL", 4)
]

axisItems = [(axis, axis, "") for axis in ("X", "Y", "Z")]

locationModeItems = [
    ("ORIGIN", "Object Origin", ""),
    ("BOUDING_BOX_CENTER", "Bounding Box Center", "")
]

class IDKeysFromSortedObjects(bpy.types.Operator):
    bl_idname = "an.id_keys_from_sorted_objects"
    bl_label = "ID Keys from Sorted Objects"
    bl_description = "Assign ID Keys based on the selected sorting method"

    idKeyName: StringProperty()
    sortMode: EnumProperty(name = "Sorting Method", default = "SELECTION_ORDER",
        items = sortModeItems)

    offset: IntProperty(name = "Offset", default = 0)
    reverse: BoolProperty(name = "Reverse", default = False)

    axis: EnumProperty(name = "Axis", default = "X", items = axisItems)
    threshold: FloatProperty(name = "Threshold", default = 0.01,
        description = "Objects with similar location should get the same index")
    locationMode: EnumProperty(name = "Location Mode", default = "ORIGIN",
        items = locationModeItems)
        
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) != 0

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 250 * getDpiFactor())

    def draw(self, context):
        layout = self.layout
        layout.column().prop(self, "sortMode", text = "Method", expand = True)
        layout.separator()

        if self.sortMode == "SELECTION_ORDER":
            pass
        elif self.sortMode == "AXIS":
            layout.prop(self, "axis")
            layout.prop(self, "locationMode", text = "Location")
            layout.prop(self, "threshold")
        elif self.sortMode == "DISTANCE":
            if context.active_object is None:
                layout.label(text = "No active object.", icon = "INFO")
            else:
                layout.prop(self, "locationMode", text = "Location")
                layout.prop(self, "threshold")
        elif self.sortMode == "RANDOM":
            pass
        elif self.sortMode == "NAME":
            pass

        layout.prop(self, "reverse")
        layout.prop(self, "offset")

    def check(self, context):
        return True

    def execute(self, context):
        if self.sortMode == "SELECTION_ORDER":
            iterSortedObjects = self.sort_SelectionOrder
        elif self.sortMode == "AXIS":
            iterSortedObjects = self.sort_Axis
        elif self.sortMode == "DISTANCE":
            iterSortedObjects = self.sort_Distance
        elif self.sortMode == "RANDOM":
            iterSortedObjects = self.sort_Random
        elif self.sortMode == "NAME":
            iterSortedObjects = self.sort_Name

        sortedObjects = list(iterSortedObjects())
        for i, objects in enumerate(sortedObjects):
            if not isinstance(objects, (list, tuple)):
                objects = [objects]
            for object in objects:
                if self.reverse:
                    index = len(sortedObjects) - i - 1
                else:
                    index = i
                object.id_keys.set("Integer", self.idKeyName, index + self.offset)

        redrawAll()
        return {"FINISHED"}

    def sort_SelectionOrder(self):
        return getSortedSelectedObjects()

    def sort_Axis(self):
        index = ["X", "Y", "Z"].index(self.axis)
        return self.sort_ByFunction(lambda x: self.getObjectLocation(x)[index])

    def sort_Distance(self):
        reference = bpy.context.active_object
        if reference is None:
            return []
        location = self.getObjectLocation(reference)
        return self.sort_ByFunction(lambda x: (self.getObjectLocation(x) - location).length)

    def sort_Random(self):
        objects = list(bpy.context.selected_objects)
        random.seed()
        random.shuffle(objects)
        return objects

    def sort_Name(self):
        return sorted(bpy.context.selected_objects, key = lambda x: naturalSortKey(x.name))

    def sort_ByFunction(self, keyFunc):
        sortedObjects = []
        threshold = self.threshold

        for object in sorted(bpy.context.selected_objects, key = keyFunc):
            if len(sortedObjects) == 0:
                sortedObjects.append([object])
            elif abs(keyFunc(sortedObjects[-1][0]) - keyFunc(object)) < threshold:
                sortedObjects[-1].append(object)
            else:
                sortedObjects.append([object])

        return sortedObjects

    def getObjectLocation(self, object):
        if self.locationMode == "ORIGIN":
            return object.location
        elif self.locationMode == "BOUDING_BOX_CENTER":
            p1 = Vector(object.bound_box[0])
            p2 = Vector(object.bound_box[6])
            return object.matrix_world * ((p1 + p2) / 2)
        
def getIDKeyIntegerName(name):
    IDKeyName="AN*Integer*%s" % name
    return IDKeyName

def getObjectsIDKeys(idKeyName):
    object_list=[]
    for obj in bpy.context.selected_objects:
        try:
            obj[idKeyName]
            object_list.append(obj)
        except KeyError: pass
    sorted_list = sorted(object_list, key=lambda obj: obj[idKeyName])
    return sorted_list

class IDKeysIntegerOffset(bpy.types.Operator):
    bl_idname = "an.id_keys_integer_offset"
    bl_label = "ID Keys Offset"
    bl_description = "Offset ID Keys of selected Objects."

    idKeyName: StringProperty()
    offset_type: EnumProperty(
        name="Type",
        default='ADD',
        items=(
            ('ADD', "Add",
             "Add number to every selected object which have Index key.\n"
             "Before :\n"
             "0, 1, 2, 3\n"
             "After Offset 1 :\n"
             "1, 2, 3, 4"),
            ('RANDOMIZE', "Randomize",
             "Randomize Index key for all selected objects which have Index Key.\n"
             "Before :\n"
             "0, 1, 2, 3\n"
             "After :\n"
             "1, 3, 0, 2"),
            ('REVERT', "Revert",
             "Revert Index for every selected object which have Index Key.\n"
             "Before :\n"
             "0, 1, 2, 3\n"
             "After :\n"
             "3, 2, 1, 0"),
            ('FILL', "Fill Gaps",
             "Fill Gaps in a serie of Index.\n"
             "Before :\n"
             "0, 1, 3, 4\n"
             "After :\n"
             "0, 1, 2, 3"),
        ))
    offset_value: IntProperty(name="Offset value", default=0)
    random_method: EnumProperty(
        name="Method",
        default='EXISTING',
        items=(
            ('EXISTING', "Existing",
             "Randomize existing indexes through selected objects."),
            ('CREATE', "Create",
             "Create random index for each selected object."),
        ))
    random_seed: IntProperty(name="Seed", default=0)
    random_min: IntProperty(name="Min", default=0)
    random_max: IntProperty(name="Max", default=10)
    start_at: BoolProperty(name="Start at", default=False)
    remove_gaps: BoolProperty(name="Remove gaps", default=False)

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) != 0

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 250 * getDpiFactor())

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "offset_type", expand = True)
        if self.offset_type=="ADD":
            layout.prop(self, "offset_value")
        elif self.offset_type=="RANDOMIZE":
            layout.prop(self, "random_method", text="")
            if self.random_method=="CREATE":
                row=layout.row(align=True)
                row.prop(self, "random_min")
                row.prop(self, "random_max")
            else: layout.prop(self, "random_seed")
        elif self.offset_type=="REVERT":
            layout.prop(self, "remove_gaps")
            if self.remove_gaps:
                row = layout.row()
                row.prop(self, "start_at")
                if self.start_at: row.prop(self, "offset_value", text="")
        elif self.offset_type=="FILL":
            row=layout.row()
            row.prop(self, "start_at")
            if self.start_at: row.prop(self, "offset_value", text="")

    def check(self, context):
        return True

    def execute(self, context):
        idkey=getIDKeyIntegerName(self.idKeyName)
        object_list=getObjectsIDKeys(idkey)
        if self.offset_type=="ADD":
            for obj in object_list: obj[idkey]=obj[idkey]+self.offset_value
            #for obj in object_list: obj.id_keys.set("Integer", idkey, index + self.offset)
        elif self.offset_type=="RANDOMIZE":
            if self.random_method=="EXISTING":
                random_numbers=[i for i in range(len(object_list))]
                random.seed(self.random_seed)
                random.shuffle(random_numbers)
            else:
                try: random_numbers=random.sample(range(self.random_min, self.random_max), len(object_list))
                except ValueError: random_numbers = random.sample(range(self.random_min, len(object_list)), len(object_list))
            for obj in object_list: obj[idkey] = random_numbers[object_list.index(obj)]
        elif self.offset_type == "REVERT":
            if self.remove_gaps:
                if self.start_at: offset = self.offset_value
                else: offset = object_list[0][idkey]
                object_list.reverse()
                for obj in object_list: obj[idkey] = object_list.index(obj)+offset
            else:
                index_list = []
                for obj in object_list: index_list.append(obj[idkey])
                index_list.reverse()
                for obj in object_list: obj[idkey]=index_list[object_list.index(obj)]
        elif self.offset_type == "FILL":
            if self.start_at: offset=self.offset_value
            else: offset=object_list[0][idkey]
            for obj in object_list: obj[idkey] = object_list.index(obj)+offset
        redrawAll()
        self.offset_value=0
        return {'FINISHED'}
