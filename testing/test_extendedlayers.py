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
        self.testobject = self.construct(WaterLevelFilter)
            
class TopSoilFilterTestCase(test_baseclasses.FilterTestCase):
    def setUp(self):
        self.testobject = self.construct(TopSoilFilter)
            
class SnowCoverFilterTestCase(test_baseclasses.FilterTestCase):
    def setUp(self):
        self.testobject = self.construct(SnowCoverFilter)

class CacheFilterTestCase(test_baseclasses.FilterTestCase):
    def setUp(self):
        self.testobject = self.construct(CacheFilter)
            
    def test_persistence(self):
        print
        print "Please implement cache persistence testing soon!"
        pass
        
