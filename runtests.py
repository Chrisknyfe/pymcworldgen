#!/usr/bin/env python

"""

Run all unit tests for pyMCWorldGen

"""
import unittest
import testing

subtesting = dir(testing)
print subtesting

suite = unittest.TestLoader().loadTestsFromModule(testing)
unittest.TextTestRunner(verbosity=2).run(suite)
