import ast
import sys

def isCodeValid(code):
    return getSyntaxError(code) is None

def getSyntaxError(code):
    try:
        ast.parse(code)
        return None
    except SyntaxError as e:
        return e
