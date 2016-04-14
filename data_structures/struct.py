class Struct:
    def __init__(self):
        self.data = {}

    def copy(self):
        s = Struct()
        s.data.update(self.data)
        return s

    def __repr__(self):
        return "<AN Struct: {} >".format(self.data)
