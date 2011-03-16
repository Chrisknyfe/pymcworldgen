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
from saveutils import *


random.seed()

def filtertest():
    testworld = createWorld("testworld")
    # cool seeds: 12397
    worldseed = random.randint(0, 65535)
    worldsizex = 8
    worldsizez = 8
    print "World seed is", worldseed
    
    roughterrain = DSLayerMask2d(worldseed,
                            chunkvolatility = 0.25, 
                            regionvolatility = 0.8, 
                            chunkinitdepth = 1 ) # Terrain height generation

    smoothterrain = DSLayerMask2d(worldseed + 1234,
                            chunkvolatility = 0.15, 
                            regionvolatility = 0.5, 
                            chunkinitdepth = 1 ) # Smooth terrain

    terrainblendmask = DSLayerMask2d(worldseed + 5678,
                            chunkvolatility = 0.0, 
                            regionvolatility = 0.5, 
                            chunkinitdepth = 1 ) # Smooth terrain

    terrain = BlendMaskFilter2d( roughterrain, smoothterrain, alphamask = terrainblendmask)


    tfilter = HeightMaskRenderFilter(terrain,
                            blockid = testworld.materials.Stone.ID,
                            rangebottom = 64 - 30 ,
                            rangetop = 64 + 30) # Render the terrain heightmask to blocks

    tfilter = Filter(tfilter) # passthru filter
    tfilter = TopSoilFilter(tfilter, 
                            rangetop = 85, thickness = 5,
                            findid = testworld.materials.Stone.ID,
                            replaceid = MAT_DIRT) # Replace top rock with dirt
    tfilter = WaterLevelFilter(tfilter,
                            rangebottom = 61, rangetop = 66,
                            findid = testworld.materials.Dirt.ID,
                            replaceid = testworld.materials.Sand.ID) # replace dirt with sandy shores 
    tfilter = WaterLevelFilter(tfilter) # water level at 64
    tfilter = TopSoilFilter(tfilter, 
                            rangetop = 84, thickness = 1, 
                            findid = testworld.materials.Dirt.ID,
                            replaceid = MAT_GRASS) # Replace top dirt with grass
        
    tfilter = WaterLevelFilter(tfilter) # water level at 64
    tfilter = Landmark(worldseed, tfilter, 0, 0) # a single landmark
    tfilter = LandmarkGenerator(worldseed, tfilter, landmarklist = [StaticTreeLandmark], density = 2500)

    tfilter = SnowCoverFilter(tfilter, 
                            rangebottom = 82, 
                            rangetop = 64 + 30 + 1,
                            thickness = 1, 
                            snowid = testworld.materials.Snow.ID) # Cake snow on top of stuff

    # Generate minecraft level
    for chunkrow in xrange(-worldsizex, worldsizex):
        print "Generating westward chunk strip", chunkrow
        for chunkcol in xrange(-worldsizez, worldsizez):
            #print "\n========\nChunk", (chunkrow, chunkcol), "\n========"        
            currchunk = tfilter.getChunk(chunkrow, chunkcol)
            setWorldChunk( testworld, currchunk, chunkrow, chunkcol)
    saveWorld(testworld)
    renderWorld("testworld", "testworld-"+str(worldseed)+"-"+str(worldsizex*2)+"x"+str(worldsizez*2))
    print "World seed is", worldseed



if __name__ == "__main__":
    if not os.path.isdir("renders"):
        os.mkdir("renders")
    filtertest()
    print "Generation complete."


