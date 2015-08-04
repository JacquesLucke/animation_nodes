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

import bpy

# socket origins
######################

def isSocketLinked(socket):
    origin = getOriginSocket(socket)
    return isOtherOriginSocket(socket, origin)

def isOtherOriginSocket(socket, origin):
    return origin is not None and origin.node.name != socket.node.name

def getOriginSocket(socket):
    if hasLinks(socket):
        fromSocket = socket.links[0].from_socket
        if fromSocket.node.type == "REROUTE":
            return getOriginSocket(fromSocket.node.inputs[0])
        else:
            return fromSocket
    else:
        if socket.node.type == "REROUTE":
            return None
        else:
            return socket

def hasLinks(socket):
    return len(socket.links) > 0
