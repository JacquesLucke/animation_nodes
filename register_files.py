import bpy

from . import keymap
from . import events
from . import tree_info
from . utils import selection
from . ui import generic_node_panel
from . base_types import node as node_base
from . base_types import socket as socket_base
from . ui.node_menu import registerMenu, unregisterMenu
from . nodes.sound import sequencer_sound_input as sequencer_sound
from . operators import dynamic_operators

def registerFiles():
    socket_base.register()
    events.registerHandlers()
    tree_info.registerHandlers()
    node_base.registerHandlers()
    selection.registerHandlers()
    generic_node_panel.register()
    sequencer_sound.registerHandlers()
    dynamic_operators.registerHandlers()

    registerMenu()
    keymap.register()

def unregisterFiles():
    socket_base.unregister()
    events.unregisterHandlers()
    tree_info.unregisterHandlers()
    node_base.unregisterHandlers()
    selection.unregisterHandlers()
    generic_node_panel.unregister()
    sequencer_sound.unregisterHandlers()
    dynamic_operators.unregisterHandlers()

    unregisterMenu()
    keymap.unregister()
