import sys
from .. import problems

def compileScript(script, name = "<string>"):
    try:
        return compile(script, name, "exec")
    except SyntaxError:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lineNumber = exc_value.lineno
        print("\n"*5)
        for i, line in enumerate(script.split("\n")):
            if i + 1 == lineNumber:
                print(line + "        <-------------- Error happens here")
            else:
                print(line)
        problems.report(message = "Invalid syntax (see console)", forbidExecution = True)
