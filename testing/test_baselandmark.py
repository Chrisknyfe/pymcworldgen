#!/usr/bin/env python

"""

Go ahead. Break a subclass. I dare you.

"""

import unittest

# Dependencies
from layer import Layer
from constants import *
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
            
    def test_setPos(self):
        rx = self.testobject.x + 5
        rz = self.testobject.z + 5
        ry = self.testobject.y + 5
        self.testobject.setPos( rx, rz, ry )
        self.assertEqual(rx, self.testobject.x)
        self.assertEqual(rz, self.testobject.z)
        self.assertEqual(ry, self.testobject.y)
            
    def test_setSeed(self):
        rseed = self.testobject.seed + 5
        self.testobject.setSeed( rseed )
        self.assertEqual(rseed, self.testobject.seed)
    
    def test_isLandmarkInChunk(self):
        (bx, bz, by) = (8, 8, 64) # block position in world
        (cx, cz) = (bx / CHUNK_WIDTH_IN_BLOCKS, bz / CHUNK_WIDTH_IN_BLOCKS)
        self.testobject.setPos( bx, bz, by )
        # we should at least detect when we're in the chunk that contains the landmark's origin.
        # Other chunks are fair game, depending on the landmark's needs.
        self.assertTrue( self.testobject.isLandmarkInChunk(cx, cz) )
        try:
            self.testobject.isLandmarkInChunk( "", None )
        except Exception as e:
            pass
        else:
            self.fail("isLandmarkInChunk should fail on non-number input")
            
        
        
        
