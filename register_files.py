import bpy

from . import keymap
from . import events
from . import tree_info
from . ui import node_colors
from . utils import selection
from . ui import generic_node_panel
from . ui import auto_nodetree_selection
from . operators import dynamic_operators
from . base_types import node as node_base
from . base_types import socket as socket_base
from . ui.node_menu import registerMenu, unregisterMenu
from . nodes.sound import sequencer_sound_input as sequencer_sound

def registerFiles():
    socket_base.register()
    node_colors.register()
    events.registerHandlers()
    tree_info.registerHandlers()
    node_base.registerHandlers()
    selection.registerHandlers()
    generic_node_panel.register()
    sequencer_sound.registerHandlers()
    dynamic_operators.registerHandlers()
    auto_nodetree_selection.registerHandlers()

    registerMenu()
    keymap.register()

def unregisterFiles():
    socket_base.unregister()
    node_colors.unregister()
    events.unregisterHandlers()
    tree_info.unregisterHandlers()
    node_base.unregisterHandlers()
    selection.unregisterHandlers()
    generic_node_panel.unregister()
    sequencer_sound.unregisterHandlers()
    dynamic_operators.unregisterHandlers()
    auto_nodetree_selection.unregisterHandlers()

    unregisterMenu()
    keymap.unregister()
