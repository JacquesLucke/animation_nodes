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

from . import keymap
from . import events
from . import tree_info
from . utils import selection
from . base_types import node as node_base
from . base_types import node_function_call
from . base_types import socket_function_call
from . base_types import socket as socket_base
from . import node_properties_panel as node_panel
from . insert_nodes_menu import registerMenu, unregisterMenu
from . nodes.sound import sequencer_sound_input as sequencer_sound

def register():
    bpy.utils.register_module(__name__)

    node_panel.register()
    socket_base.register()
    events.registerHandlers()
    tree_info.registerHandlers()
    node_base.registerHandlers()
    selection.registerHandlers()
    sequencer_sound.registerHandlers()
    node_function_call.registerHandlers()
    socket_function_call.registerHandlers()

    registerMenu()
    keymap.register()

    bpy.types.Scene.animationNodes = PointerProperty(type = AnimationNodesSettings, name = "Animation Nodes Settings")

    print("Registered Animation Nodes with {} modules.".format(len(modules)))

def unregister():
    bpy.utils.unregister_module(__name__)

    node_panel.unregister()
    socket_base.unregister()
    events.unregisterHandlers()
    tree_info.unregisterHandlers()
    node_base.unregisterHandlers()
    selection.unregisterHandlers()
    sequencer_sound.unregisterHandlers()
    node_function_call.unregisterHandlers()
    socket_function_call.unregisterHandlers()

    unregisterMenu()
    keymap.unregister()

    del bpy.types.Scene.animationNodes

    print("Unregistered Animation Nodes")
