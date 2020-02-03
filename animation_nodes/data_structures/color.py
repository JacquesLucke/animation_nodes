class Color:
    def __init__(self, color):
        if len(color) != 4:
            raise ValueError("Expected a tuple of 4 numbers.")
        self.color = list(color)

    def __len__(self):
        return 4

    def __getitem__(self, key):
        return self.color[key]
    
    def __eq__(self, other):
        if not isinstance(other, Color):
            return False
        return all(a == b for a, b in zip(self.color, other.color))

    def __hash__(self):
        return hash(tuple(self.color))

    def __repr__(self):
        return f"Color(R: {self.r:.2f}, G: {self.g:.2f}, B: {self.b:.2f}, A: {self.a:.2f})"

    def copy(self):
      return Color(self.color)

    @property
    def r(self):
        return self.color[0]

    @property
    def g(self):
        return self.color[1]

    @property
    def b(self):
        return self.color[2]

    @property
    def a(self):
        return self.color[3]

    @r.setter
    def r(self, r):
        self.color[0] = r

    @g.setter
    def g(self, g):
        self.color[1] = g

    @b.setter
    def b(self, b):
        self.color[2] = b

    @a.setter
    def a(self, a):
        self.color[3] = a
