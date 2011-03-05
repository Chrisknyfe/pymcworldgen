#!/usr/bin/env python

"""

Standalone generator for mcworldgen

basically mcworldgentest with scipy/pylab stripped out

"""

# Dependencies
import random
import math
import copy
import time
import os
import subprocess
import numpy
import pymclevel as mcl

# Modules to test
from diamondsquare import *
from layer import *
from landmark import *

# Test stuff so I don't have to write it twice
from unittests import rm_rf, createWorld, getWorldChunk, setWorldChunk, saveWorld, renderWorld

def filtertest():
    testworld = createWorld("testworld")
    random.seed()
    # cool seeds: 12397
    worldseed = random.randint(0, 65535)
    worldsizex = 16
    worldsizez = 16
    print "World seed is", worldseed
    
    terrheightmask = DSLayer2d(worldseed,
                            chunkvolatility = 0.25, 
                            regionvolatility = 0.8, 
                            chunkinitdepth = 1 ) # Terrain height generation
    
    #terrheightmask = LayerMask2d() # would yield a tall, flat map.

    terrheightmask = MaskFilter2d(terrheightmask) # passthrough

    #terrheightmask = ThresholdMaskFilter2d(terrheightmask) # threshold

    tfilter = HeightMaskRenderFilter(terrheightmask,
                            blockid = testworld.materials.Stone.ID,
                            rangebottom = 64 - 30 ,
                            rangetop = 64 + 30) # Render the terrain heightmask to blocks

    tfilter = Filter(tfilter) # passthru filter
    tfilter = TopSoilFilter(tfilter, 
                            rangetop = 85, thickness = 5,
                            findid = testworld.materials.Stone.ID,
                            replaceid = testworld.materials.Dirt.ID) # Replace top rock with dirt
    tfilter = WaterLevelFilter(tfilter,
                            rangebottom = 61, rangetop = 66,
                            findid = testworld.materials.Dirt.ID,
                            replaceid = testworld.materials.Sand.ID) # replace dirt with sandy shores 
    tfilter = WaterLevelFilter(tfilter) # water level at 64
    tfilter = TopSoilFilter(tfilter, 
                            rangetop = 84, thickness = 1, 
                            findid = testworld.materials.Dirt.ID,
                            replaceid = testworld.materials.Grass.ID) # Replace top dirt with grass
    tfilter = SnowCoverFilter(tfilter, 
                            rangebottom = 82, 
                            rangetop = 64 + 30 + 1,
                            thickness = 1, 
                            snowid = testworld.materials.Snow.ID) # Cake snow on top of exposed stone
        
    tfilter = WaterLevelFilter(tfilter) # water level at 64
    #tfilter = Landmark(worldseed, tfilter, 255, 255) # a single landmark
    #tfilter = Landmark(worldseed, tfilter, 0, 0) # a single landmark
    #tfilter = Landmark(worldseed, tfilter, 0, 255) # a single landmark
    #tfilter = Landmark(worldseed, tfilter, 255, 0) # a single landmark
    #tfilter = Landmark(worldseed, tfilter, 128, 128) # a single landmark
    #tfilter = Landmark(worldseed, tfilter, -20, -10) # a single landmark
    #tfilter = Landmark(worldseed, tfilter, 300, 258) # a single landmark

    # Generate minecraft level
    for chunkrow in xrange(worldsizex):
        print "Generating westward chunk strip", chunkrow
        for chunkcol in xrange(worldsizez):
            #print "\n========\nChunk", (chunkrow, chunkcol), "\n========"        
            currchunk = tfilter.getChunk(chunkrow, chunkcol)
            setWorldChunk( testworld, currchunk, chunkrow, chunkcol)
    saveWorld(testworld)
    renderWorld("testworld", "testworld-"+str(worldseed)+"-"+str(worldsizex)+"x"+str(worldsizez))
    print "World seed is", worldseed


if __name__ == "__main__":
    if not os.path.isdir("renders"):
        os.mkdir("renders")
    filtertest()
    print "Generation complete."


