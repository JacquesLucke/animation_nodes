'''
Copyright (C) 2014 Jacques Lucke
mail@jlucke.com

Created by Jacques Lucke

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


bl_info = {
    "name":        "Animation Nodes",
    "description": "Node system for more flexible animations.",
    "author":      "Jacques Lucke",
    "version":     (0, 0, 7),
    "blender":     (2, 7, 4),
    "location":    "Node Editor",
    "category":    "Node",
    "warning":     "Stable, but some things may change in the future."
    }



# load and reload submodules
##################################

from . import developer_utils
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())



# properties
##################################

import bpy
from bpy.props import *
from . id_keys import IDKeySettings

class AnimationNodesSettings(bpy.types.PropertyGroup):
    idKeys = PointerProperty(type = IDKeySettings, name = "ID Keys")



# register
##################################

addon_keymaps = []
def registerKeymaps():
    global addon_keymaps
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name = "Node Editor", space_type = "NODE_EDITOR")
    kmi = km.keymap_items.new("an.insert_node", type = "A", value = "PRESS", ctrl = True)
    kmi = km.keymap_items.new("wm.call_menu_pie", type = "W", value = "PRESS")
    kmi.properties.name = "an.context_pie"
    addon_keymaps.append(km)

def unregisterKeymaps():
    global addon_keymaps
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()

from . import events
from . insert_nodes_menu import registerMenu, unregisterMenu
from . base_types import node as node_base
from . base_types import socket as socket_base
from . base_types import node_function_call
from . base_types import socket_function_call
from . nodes.sound import sequencer_sound_input as sequencer_sound
from . utils import selection

def register():
    bpy.utils.register_module(__name__)

    socket_base.register()
    events.registerHandlers()
    node_base.registerHandlers()
    selection.registerHandlers()
    sequencer_sound.registerHandlers()
    node_function_call.registerHandlers()
    socket_function_call.registerHandlers()

    registerMenu()
    registerKeymaps()

    bpy.types.Scene.animationNodes = PointerProperty(type = AnimationNodesSettings, name = "Animation Nodes Settings")

    print("Registered Animation Nodes with {} modules.".format(len(modules)))

def unregister():
    bpy.utils.unregister_module(__name__)

    socket_base.unregister()
    events.unregisterHandlers()
    node_base.unregisterHandlers()
    selection.unregisterHandlers()
    sequencer_sound.unregisterHandlers()
    node_function_call.unregisterHandlers()
    socket_function_call.unregisterHandlers()

    unregisterMenu()
    unregisterKeymaps()

    del bpy.types.Scene.animationNodes

    print("Unregistered Animation Nodes")
