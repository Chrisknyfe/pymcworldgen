#!/usr/bin/env python

"""

Landmark generation - interspersed landmarks on the terrain

"""

import random
import math
from layer import *
import numpy

class Landmark(Layer):
    """
    A chunk generator for a single landmark somewhere in the world.
    """
    seed = None
    terrainlayer = None
    x = None
    z = None
    layermask = None
    
    # Viewrange is a class property only. This is the maximum number of blocks from
    # the centerpoint that this Landmark will generate blocks.
    viewrange = 0
    def __init__(self, seed, terrainlayer, x = 0, z = 0, layermask = None):
        """
        Landmark constructor. Random seed necessary. terrainlayer necessary.
        if x and z are None, we generate at a random point? I don't really like that behavior
        how about we generate at 0,0. Layermask can prevent us from spawning in
        certain places, or give us a random probability that we won't spawn in an area.
        """
        self.seed = seed
        self.terrainlayer = terrainlayer
        self.x = x
        self.z = z
        self.layermask = layermask

    def isLandmarkInChunk(self, cx, cz):
        """
        Determine whether the given chunk contains a portion of this landmark.
        """
        bxrange = (cx*16 - self.viewrange, (cx+1)*16 + self.viewrange)
        bzrange = (cz*16 - self.viewrange, (cz+1)*16 + self.viewrange)

        if ( bxrange[0] <= self.x < bxrange[1] ) and ( bzrange[0] <= self.z < bzrange[1] ):
            return True
        else:
            return False

    def editChunk(self, cornerblockx, cornerblockz, terrainchunk):
        # Dummy: output a wood block at height 105.
        # where in the array does this block belong?
        relx = self.x - cornerblockx
        relz = self.z - cornerblockz
        # test assert to make sure things are going just as planned.
        assert( 0 <= relx < 16 )
        assert( 0 <= relz < 16 )
        terrainchunk[relx, relz, 0:127] = 17
        
    def getChunk(self, cx, cz):
        """
        Output a chunk for processing. 
        """
        # If we aren't in this chunk, either act as a passthru or return an opaque chunk.
        if not self.isLandmarkInChunk(cx, cz):
            return self.terrainlayer.getChunk(cx, cz)
        # If we are in the chunk, let's write our blocks to the output chunk
        terrainchunk = self.terrainlayer.getChunk(cx, cz)
        outputchunk = terrainchunk
        self.editChunk(cx*16, cz*16, terrainchunk)
        return outputchunk






