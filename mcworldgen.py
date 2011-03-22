#!/usr/bin/env python

"""

mcworldgen.py

Standalone generator for mcworldgen: generates a default-ish minecraft map.

"""


# Dependencies
import random
import math
import copy
import time
import os
import subprocess
#import numpy
import time
import pymclevel as mcl

# Modules to test
from diamondsquare import *
from layer import *
from landmark import *
from saveutils import *


random.seed()

def filtertest():

    totaltime = 0

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
                            rangetop = 64 + 30) # Render the terrain heightmask to rock
    # Bottom should be Adminium/Bedrock
    tfilter = WaterLevelFilter(tfilter, rangetop = 0, findid = MAT_STONE, replaceid = MAT_BEDROCK)
    # Add ores
    tfilter = LandmarkGenerator(tfilter, worldseed + 5, landmarklist = [CubicOreLandmark(None, ore = MAT_COALORE, density = 0.5, sizex = 4, sizez = 4, sizey = 4)], density = 2500 , rangebottom = 1, rangetop = 50)
    tfilter = LandmarkGenerator(tfilter, worldseed + 6, landmarklist = [CubicOreLandmark(None, ore = MAT_IRONORE, density = 0.5, sizex = 3, sizez = 3, sizey = 3)], density = 6500 , rangebottom = 1, rangetop = 50)
    tfilter = LandmarkGenerator(tfilter, worldseed + 4, landmarklist = [CubicOreLandmark(None, ore = MAT_GOLDORE, density = 0.5)], density = 2300 , rangebottom = 1, rangetop = 35)
    tfilter = LandmarkGenerator(tfilter, worldseed + 3, landmarklist = [CubicOreLandmark(None, ore = MAT_LAPISORE, density = 0.5)], density = 1200, rangebottom = 1, rangetop = 32)
    tfilter = LandmarkGenerator(tfilter, worldseed + 2, landmarklist = [CubicOreLandmark(None, ore = MAT_REDSTONEORE, density = 0.5, sizex = 3, sizez = 3, sizey = 3)], density = 2600, rangebottom = 1, rangetop = 19)
    tfilter = LandmarkGenerator(tfilter, worldseed + 1, landmarklist = [CubicOreLandmark(None, ore = MAT_DIAMONDORE, density = 0.5)], density = 1400, rangebottom = 1, rangetop = 19)

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
    tfilter = Landmark(tfilter, worldseed, 0, 0) # a single landmark
    tfilter = CacheFilter(tfilter) # since LandmarkGenerator requests chunks multiple times, this is generally needed.
    tfilter = LandmarkGenerator(tfilter, worldseed, landmarklist = [StaticTreeLandmark(None)], density = 2500)

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
            
            starttime = time.clock()     
            currchunk = tfilter.getChunk(chunkrow, chunkcol)
            endtime = time.clock()
            totaltime += endtime - starttime
            setWorldChunk( testworld, currchunk, chunkrow, chunkcol)
    
    saveWorld(testworld)
    renderWorld("testworld", "testworld-"+str(worldseed)+"-"+str(worldsizex*2)+"x"+str(worldsizez*2))
    print "World seed is", worldseed

    print "Processing took", totaltime, "seconds."

if __name__ == "__main__":
   
    try:
        import psyco
        psyco.full()
    except ImportError:
        print "Psyco could not be loaded. Install with \'sudo apt-get install python-psyco\' for additional speed boosts."
        pass
    
    if not os.path.isdir("renders"):
        os.mkdir("renders")
    filtertest()
    print "Generation complete."


