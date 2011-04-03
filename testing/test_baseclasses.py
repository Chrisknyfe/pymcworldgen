#!/usr/bin/env python

"""

Go ahead. Break a subclass. I dare you.

"""

import unittest

# Dependencies
import random
import sys
from constants import *

# Modules to test
from layer import Chunk, Layer, Filter

def validate_chunk_fields(chunk):
    # validate chunk coordinates
    if type(chunk.cx) != int: raise RuntimeError, "chunk cx not of type int"
    if type(chunk.cz) != int: raise RuntimeError, "chunk cx not of type int"
    # validate chunk blocks
    if len(chunk.blocks) != CHUNK_WIDTH_IN_BLOCKS: raise RuntimeError, "chunk doesn't have correct number of rows"
    for rowix in xrange(CHUNK_WIDTH_IN_BLOCKS):
        if len(chunk.blocks[rowix]) != CHUNK_WIDTH_IN_BLOCKS: raise RuntimeError, "chunk row %d doesn't have correct number of columns" % rowix 
        for colix in xrange(CHUNK_WIDTH_IN_BLOCKS):
            if len(chunk.blocks[rowix][colix]) != CHUNK_HEIGHT_IN_BLOCKS: raise RuntimeError, "chunk vertical column (%d,%d) doesn't have correct number of blocks" % (rowix, colix) 
            for heightix in xrange(CHUNK_HEIGHT_IN_BLOCKS):
                if type(chunk.blocks[rowix][colix][heightix]) != int: raise RuntimeError, "chunk block (%d,%d,%d) is not of type int" % (rowix, colix, heightix)
    # validate chunk data
    if len(chunk.data) != CHUNK_WIDTH_IN_BLOCKS: raise RuntimeError, "chunk doesn't have correct number of rows"
    for rowix in xrange(CHUNK_WIDTH_IN_BLOCKS):
        if len(chunk.data[rowix]) != CHUNK_WIDTH_IN_BLOCKS: raise RuntimeError, "chunk row %d doesn't have correct number of columns" % rowix 
        for colix in xrange(CHUNK_WIDTH_IN_BLOCKS):
            if len(chunk.data[rowix][colix]) != CHUNK_HEIGHT_IN_BLOCKS: raise RuntimeError, "chunk vertical column (%d,%d) doesn't have correct number of blocks" % (rowix, colix) 
            for heightix in xrange(CHUNK_HEIGHT_IN_BLOCKS):
                if type(chunk.data[rowix][colix][heightix]) != int: raise RuntimeError, "chunk block (%d,%d,%d) is not of type int" % (rowix, colix, heightix)

class ChunkTestCase(unittest.TestCase):
    """
    Chunk is a class that contains a single chunk of minecraft map data. Acts as a transport class between layers and filters
    - it should contain a square, chunk-sized array of blocks and data.
    - it should have valid integer values for cx and cz. 
    - When copied, none of its fields should affect the fields of the original chunk.
    """
    testobject = None # this gets set in setUp, and tested in the subsequent tests. This allows subclassing of the tested object!
    def setUp(self):
        random.seed()
        self.testobject = Chunk(random.randint(-sys.maxint-1, sys.maxint - 1),random.randint(-sys.maxint -1, sys.maxint - 1))
        try:
            chunk = Chunk( "1", None )
        except Exception as e:
            pass
        else:
            self.fail("chunk constructor should fail on bad input ")
        
    
    def test_valid_fields(self):
        validate_chunk_fields(self.testobject)

    def test_copy(self):
        chunkcopy = self.testobject.copy()
        validate_chunk_fields(chunkcopy)
        chunkcopy.cx += 1
        chunkcopy.cz += 1
        for rowix in xrange(CHUNK_WIDTH_IN_BLOCKS):
            for colix in xrange(CHUNK_WIDTH_IN_BLOCKS):
                for heightix in xrange(CHUNK_HEIGHT_IN_BLOCKS):
                    chunkcopy.blocks[rowix][colix][heightix] += 1
                    chunkcopy.data[rowix][colix][heightix] += 1
        for rowix in xrange(CHUNK_WIDTH_IN_BLOCKS):
            for colix in xrange(CHUNK_WIDTH_IN_BLOCKS):
                for heightix in xrange(CHUNK_HEIGHT_IN_BLOCKS):
                    self.assertNotEqual(chunkcopy.blocks[rowix][colix][heightix], self.testobject.blocks[rowix][colix][heightix])
                    self.assertNotEqual(chunkcopy.data[rowix][colix][heightix], self.testobject.data[rowix][colix][heightix])
        
class LayerTestCase(unittest.TestCase):
    """
    Layer: Implements a layer of minecraft blocks.
    - Constructor should work with no arguments
    - getChunk() should return a valid chunk.
    - getChunk() should fail on bad inputs.
    
    Depends on chunk unit tests.
    """
    testobject = None # this gets set in setUp, and tested in the subsequent tests. This allows subclassing of the tested object!
    
    def setUp(self):
        self.testobject = self.construct(Layer)
        
    def construct(self, thisclass):
        """
        self.construct: the solution to re-testing the superclasses' constructor. Usually we test the class's constructor in setUp,
        but this way we leave a nice hook to override setUp as needed, and to allow the subclass to call the constructor using 
        the superclass's test.
        
        Don't call the superclass's construct() method if you're changing the rules for constructing.
        """
        return thisclass()
    
    def test_getchunk(self):
        self.testobject = Layer()
        random.seed()
        chunk = self.testobject.getChunk(random.randint(-sys.maxint-1, sys.maxint - 1),random.randint(-sys.maxint -1, sys.maxint - 1))
        self.assertEquals(type(chunk), Chunk)
        validate_chunk_fields(chunk)
        
        try:
            self.testobject.getChunk(None, False)
        except Exception as e:
            pass
        else:
            self.fail("filter getChunk should fail on bad input ")
            
class FilterTestCase(LayerTestCase):
    """
    Filter: Implements a filter for layers of minecraft blocks.
    - Should only be constructable by passing a layer in. 
    """

    def setUp(self):
        self.testobject = self.construct(Filter)
    
    def construct(self, thisclass):
        layer = Layer()
        # None is also supported as an inputlayer for filters, but getChunk will fail.
        ft = thisclass(None)        
        try:
            ft = thisclass(False)
        except Exception as e:
            pass
        else:
            self.fail("filter should not accept anything except a layer in its constructor.")
            
        return thisclass(layer)
        
    
    def test_setinputlayer(self):
        newlayer = Layer()
        self.assertNotEqual(newlayer, self.testobject.inputlayer)
        self.testobject.setInputLayer(newlayer)
        self.assertEqual(newlayer, self.testobject.inputlayer)
        
        try:
            self.testobject.setInputLayer("not a layer or subclass thereof")
        except Exception as e:
            pass
        else:
            self.fail("filter should not accept anything except a layer in its constructor.")
        
        
            
              
        
        
        
        
        
