import blf
import textwrap
from bgl import *
from . rectangle import Rectangle

font = 1

class TextBox:
    def __init__(self, text, position, width, fontSize, lineHeightFactor = 1, maxRows = 1e5):
        self.text = text
        self.width = width
        self.maxRows = maxRows
        self.position = position
        self.fontSize = int(fontSize)
        self.lineHeight = self.fontSize / 5 * lineHeightFactor

        self.boundary = Rectangle()
        self.boundary.color = (0.9, 0.9, 0.9, 0.6)
        self.boundary.borderThickness = -1
        self.boundary.borderColor = (0.9, 0.76, 0.4, 1.0)

    def draw(self):
        self.prepareFontDrawing()
        self.separateLines()
        self.calculateBoundaries()
        self.boundary.draw()
        self.drawLines()

    def prepareFontDrawing(self):
        blf.size(font, self.fontSize, 12)

    def separateLines(self):
        self.lines = []
        characterWidth = blf.dimensions(font, "abcde")[0] / 5

        paragraphs = self.text.split("\n")
        for paragraph in paragraphs:
            paragraphLines = textwrap.wrap(paragraph, int(self.width / characterWidth))
            self.lines.extend(paragraphLines)
            
            if len(self.lines) == self.maxRows: break
            elif len(self.lines) > self.maxRows: self.lines = self.lines[:self.maxRows]


    def calculateBoundaries(self):
        lineAmount = len(self.lines)

        x1 = self.position.x
        x2 = x1 + self.width
        y1 = self.position.y
        y2 = y1 - lineAmount * self.lineHeight

        self.boundary.resetPosition(x1, y1, x2, y2)

    def drawLines(self):
        baseLineOffset = blf.dimensions(font, "V")[1]

        glColor4f(0, 0, 0, 1)
        for i, line in enumerate(self.lines):
            blf.position(font, self.boundary.left, self.boundary.top - i * self.lineHeight - baseLineOffset, 0)
            blf.draw(font, line)
