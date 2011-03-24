#TODO: we don't need half of these imports
#TODO: maybe should not need reference to world object?

import random
import math
import copy
import time
import os
import subprocess
#import numpy
import time

# Modules to test
from diamondsquare import *
from layer import *
from landmark import *
from saveutils import *

def build(worldseed, worldobj):
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
                            blockid = worldobj.materials.Stone.ID,
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
                            findid = worldobj.materials.Stone.ID,
                            replaceid = MAT_DIRT) # Replace top rock with dirt
    tfilter = WaterLevelFilter(tfilter,
                            rangebottom = 61, rangetop = 66,
                            findid = worldobj.materials.Dirt.ID,
                            replaceid = worldobj.materials.Sand.ID) # replace dirt with sandy shores 
    tfilter = WaterLevelFilter(tfilter) # water level at 64
    tfilter = TopSoilFilter(tfilter, 
                            rangetop = 84, thickness = 1, 
                            findid = worldobj.materials.Dirt.ID,
                            replaceid = MAT_GRASS) # Replace top dirt with grass
        
    tfilter = WaterLevelFilter(tfilter) # water level at 64
    tfilter = Landmark(tfilter, worldseed, 0, 0) # a single landmark
    tfilter = CacheFilter(tfilter) # since LandmarkGenerator requests chunks multiple times, this is generally needed.
    tfilter = LandmarkGenerator(tfilter, worldseed, landmarklist = [StaticTreeLandmark(None)], density = 2500)

    tfilter = SnowCoverFilter(tfilter, 
                            rangebottom = 82, 
                            rangetop = 64 + 30 + 1,
                            thickness = 1, 
                            snowid = worldobj.materials.Snow.ID) # Cake snow on top of stuff
    return tfilter
