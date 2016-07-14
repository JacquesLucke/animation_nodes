import unittest

def runTests():
    print("\n" * 5)
    allTests = unittest.TestLoader().discover("animation_nodes", pattern = "test*")
    unittest.TextTestRunner(verbosity = 1).run(allTests)
    print("\n" * 5)
