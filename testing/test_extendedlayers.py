#!/usr/bin/env python

"""

Go ahead. Break a subclass. I dare you.

"""

import unittest

# Dependencies
from constants import *
import test_baseclasses

# Modules to test
from layer import *

class WaterLevelFilterTestCase(test_baseclasses.FilterTestCase):
    def setUp(self):
        layer = Layer()
        self.testobject = WaterLevelFilter(layer)
        try:
            ft = WaterLevelFilter(None)
        except Exception as e:
            pass
        else:
            self.fail("WaterLevelFilter should not accept anything except a layer in its constructor.")
            
class TopSoilFilterTestCase(test_baseclasses.FilterTestCase):
    def setUp(self):
        layer = Layer()
        self.testobject = TopSoilFilter(layer)
        try:
            ft = TopSoilFilter(None)
        except Exception as e:
            pass
        else:
            self.fail("TopSoilFilter should not accept anything except a layer in its constructor.")
            
class SnowCoverFilterTestCase(test_baseclasses.FilterTestCase):
    def setUp(self):
        layer = Layer()
        self.testobject = SnowCoverFilter(layer)
        try:
            ft = SnowCoverFilter(None)
        except Exception as e:
            pass
        else:
            self.fail("SnowCoverFilter should not accept anything except a layer in its constructor.")

class CacheFilterTestCase(test_baseclasses.FilterTestCase):
    def setUp(self):
        layer = Layer()
        self.testobject = CacheFilter(layer)
        try:
            ft = CacheFilter(None)
        except Exception as e:
            pass
        else:
            self.fail("CacheFilter should not accept anything except a layer in its constructor.")
            
    def test_persistence(self):
        print "Please implement cache persistence testing soon!"
        pass
        
