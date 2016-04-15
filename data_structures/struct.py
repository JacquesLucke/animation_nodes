from .. sockets.info import getCopyFunction

class Struct:
    __slots__ = ("data", )

    def __init__(self):
        self.data = {}

    def copy(self):
        s = Struct()
        for (dataType, name), value in self.data.items():
            s.data[(dataType, name)] = getCopyFunction(dataType)(value)
        return s

    def __repr__(self):
        return "<AN Struct: {} >".format(self.data)
