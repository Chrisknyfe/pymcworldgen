#!/usr/bin/env python

"""

Run all unit tests for pyMCWorldGen

"""

import unittest
import testing
modnames = dir(testing)
suite = unittest.TestSuite()
for modname in modnames:
    if not modname.startswith("__"):
        suite.addTest(unittest.TestLoader().loadTestsFromModule( getattr(testing, modname) ) )
unittest.TextTestRunner(verbosity=2).run(suite)
