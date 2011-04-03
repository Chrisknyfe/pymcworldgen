#!/usr/bin/env python

"""

Unit testing for chunk class

"""

import unittest

# Dependencies
import random
import sys
from constants import *
from layer import Layer
import test_baseclasses

# Modules to test
from landmark import Landmark


class LandmarkTestCase(test_baseclasses.FilterTestCase):
    """
    Landmark: A single object placed somewhere in the minecraft world. 
    - 
    """
    def setUp(self):
        layer = Layer()
        self.testobject = Landmark(layer)
        
        try:
            ft = Landmark(None)
        except Exception as e:
            pass
        else:
            self.fail("Landmark should not accept anything except a layer in its constructor.")
        
            
        
        
        
