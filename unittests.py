#!/usr/bin/env python

"""

Unit testing for pymcworldgen

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
from scipy import *
from pylab import *

# Modules to test
from diamondsquare import *
from layer import *
from landmark import *

# Convenient rm -rf python function
# http://code.activestate.com/recipes/552732-remove-directories-recursively/
def rm_rf(d):
    for path in (os.path.join(d,f) for f in os.listdir(d)):
        if os.path.isdir(path):
            rm_rf(path)
        else:
            os.unlink(path)
    os.rmdir(d)


def savechunkimage( chunk, name='randomchunk' ):
    hold(False)
    ct = numpy.transpose(chunk) # for some reason, imshow reverses the axes. It thinks this is column major.
    imshow( ct, origin='lower', extent=[0,len(chunk),0,len(chunk[0])])
    hold(True)
    xlabel('x (positive is south)')
    ylabel('z (positive is west)')
    title(name)
    savefig(os.path.join("renders", name))

def createWorld(name):
    worlddir = os.path.join( os.getcwd(), "renders", name )
    if ( os.path.exists( worlddir ) ):
        print "World exists, deleting..."
        rm_rf(worlddir)
    os.mkdir( worlddir )

    world = mcl.MCInfdevOldLevel( worlddir, create = True);

    world.generateLights();
    world.setPlayerPosition( (0, 67, 0) ) # add 3 to make sure his head isn't in the ground.
    world.setPlayerSpawnPosition( (0, 64, 0) )
    world.saveInPlace()
    return world

def saveWorld(world):
    # save the world to file...
    world.saveInPlace()

def renderWorld(worldname, filename):
    # take a c10t snapshot!
    subprocess.call(["./c10t/c10t", "-w", "./renders/" + worldname, "-o", "./renders/" + filename + ".png", "--oblique-angle" ])    

def getWorldChunk(world, cx, cz):
    if not world.containsChunk(cx, cz):
        world.createChunk(cx, cz)
    chunk = world.getChunk(cx, cz)
    return numpy.array(chunk.Blocks)

chunksBeforeNextSave = 256
def setWorldChunk(world, arr, cx, cz):
    global chunksBeforeNextSave
    assert( len(arr) == 16 )
    assert( len(arr[0]) == 16 )
    assert( len(arr[0][0]) == 128 )

    if not world.containsChunk(cx, cz):
        world.createChunk(cx, cz)
    chunk = world.getChunk(cx, cz)
    chunk.Blocks[:] = arr
    chunk.chunkChanged()    
    # Periodically save the map.
    chunksBeforeNextSave -= 1
    if chunksBeforeNextSave <= 0:
        chunksBeforeNextSave = 256
        saveWorld(world)    

 

def ds_unittest():
    print "Testing diamond square 2D on empty odd-sized array" 
    m = [[-1 for col in xrange(5)] for row in xrange(5)];
    #print m
    diamondsquare2D( m, 1234 )
    #print m
    # test that all values were filled
    for row in m:
        for col in row:
            assert( col >= 0 )
    
    print "Testing diamond square 2D on corner-initialized even-sized array" 
    m = [[-1 for col in xrange(4)] for row in xrange(4)]; m[0][0] = 0.5; m[3][0] = 0.5; m[0][3] = 0.5; m[3][3] = 0.5
    #print m
    diamondsquare2D( m, 1234 )
    #print m
    # test that all values were filled
    for row in m:
        for col in row:
            assert( col >= 0 )

    print "Testing diamond square 1D on empty odd array"
    a = [-1 for el in xrange(9)]
    #print a
    diamondsquare1D( a, 1234 )
    #print a
    # test that all values were filled
    for el in a:
        assert( el >= 0 )

    print "Testing diamond square 1D on corner-filled even array"
    a = [-1 for el in xrange(10)]; a[0] = 0.95; a[9] = 0.05
    #print a
    diamondsquare1D( a, 1234 )
    #print a
    # test that all values were filled
    for el in a:
        assert( el >= 0 )

        

def ds_2dplottest():
    random.seed()

    # Allocate the array
    zsize = ( random.randint(20, 100), random.randint(20,100) )
    z = [[-0.25 for col in xrange( zsize[0] )] for row in xrange( zsize[1] )]
    print "size of 2d z is", (len(z), len(z[0]))

    # Initialize corners
    z[0][0] = z[len(z)-1][0] = z[0][len(z[0])-1] = z[len(z)-1][len(z[0])-1] = 0.5

    # Generate entire terrain
    diamondsquare2D(z)
    savechunkimage(z, 'terrain full')


def ds_1dplottest():
    random.seed()

    # Generate entire terrain
    z = [-0.1 for row in xrange( random.randint(20,100) )]
    z[0] = z[len(z)-1] = 0.5

    diamondsquare1D(z, seed = random.randint(0, 65535) )

    figure()
    plot(range(len(z)), z)
    xlabel('position along string')
    ylabel('height')
    title('Full Edge')
    grid(True)
    savefig(os.path.join("renders", 'fulledge') )
    #show()
    

def lg_unittest():

    dummylayer = Layer()

    
    dummylayer.getChunk( (0,0) )

    random.seed()
    terrainheight = DSLayer2d(random.randint(0, 65535))

    # make sure we can generate good chunks
    print "\nTesting single chunk\n========"
    chunkdata = terrainheight.getChunkHeights( random.randint(0,65536) , random.randint(0,65536) )
    savechunkimage(chunkdata, 'single chunk')    


    # make sure we can generate good regions
    print "\nTesting single region\n========"
    regiondata = terrainheight.getRegionChunkCornerHeights( (random.randint(0,65536) , random.randint(0,65536)) ) 
    savechunkimage(regiondata, 'single region')    

    """
    # check to see if we can make seamless chunks
    chunkzero = terrainheight.getChunkHeights( 0 , 0 )
    #print "Chunk Zero\n========\n", chunkzero
    savechunkimage(chunkzero, 'chunk zero')


    chunkone = terrainheight.getChunkHeights( 1 , 0 )
    #print "Chunk One\n========\n", chunkone
    savechunkimage(chunkone, 'chunk one')

    pairachunks = numpy.concatenate( (chunkzero, chunkone), axis = 0)
    #print "Pair of chunks\n========\n", pairachunks
    savechunkimage(pairachunks, 'pairachunks')

    # wait, WHAT??? these plots make no sense.
    testx = 16
    testy = 13
    testimg = [ [ (col / float(testx*testy) ) + (row / float(testx) ) for col in xrange(testy) ] for row in xrange (testx) ]
    #print "Test image\n========\n", testimg
    savechunkimage(testimg, 'test image')
    # OH. shit was rotated wrongly
    """

    # let's test region seaming
    print "\nTesting region seaming\n========"
    fullmap = None
    for regionsouth in xrange(0, 4):
        westwardstrip = None
        for regionwest in xrange(0, 4):
            print "Generating region", (regionsouth, regionwest)
            regionraw = terrainheight.getRegionChunkCornerHeights( (regionsouth , regionwest) )
            currregion = regionraw[0:32,0:32] #slice off the last edges
            if westwardstrip == None:
                westwardstrip = currregion
            else:
                westwardstrip = numpy.append( westwardstrip, currregion, axis = 1)
        if fullmap == None:
            fullmap = westwardstrip
        else:
            fullmap = numpy.append( fullmap, westwardstrip, axis = 0)
    savechunkimage(fullmap, 'lg_unittest_regionmap')
    
    # let's go wild generating a huge map
    print "\nTesting huge map seaming\n========"
    fullmap = None
    for chunksouth in xrange(0, 66):
        westwardstrip = None
        print "Generating westward chunk strip", chunksouth
        for chunkwest in xrange(0, 66):
            currchunk = terrainheight.getChunkHeights( chunksouth , chunkwest )
            if westwardstrip == None:
                westwardstrip = currchunk
            else:
                westwardstrip = numpy.append( westwardstrip, currchunk, axis = 1)
        if fullmap == None:
            fullmap = westwardstrip
        else:
            fullmap = numpy.append( fullmap, westwardstrip, axis = 0)
    savechunkimage(fullmap, 'lg_unittest_hugemap')

def world_savetest():
    testworld = createWorld("world_savetest_testworld")
    random.seed()
    worldseed = random.randint(0, 65535)
    terrainheight = DSLayer2d(worldseed, 
                            chunkvolatility = 0.5, 
                            regionvolatility = 0.4, 
                            chunkinitdepth = 3 )

    tfilter = HeightMaskRenderFilter(terrainheight,
                            blockid = testworld.materials.Wood.ID,
                            rangebottom = 50 ,
                            rangetop = 100) # Render the terrain heightmask to blocks

    
    #dummychunk = numpy.array([ [ [0 for h in xrange(128)] for c in xrange(16)] for r in xrange(16)])
    #dummychunk[:,:,0:64] = testworld.materials.Dirt.ID
    
    #dummychunk = terrainheight.getChunk(0,0)
    #setWorldChunk(testworld, dummychunk, 0,0)

    # Generate renders
    fullmap = None
    for chunkrow in xrange(32):
        westwardstrip = None
        print "Generating westward chunk strip", chunkrow
        for chunkcol in xrange(32):
            print "Chunk", (chunkrow, chunkcol)
            # save to minecraft level            
            currchunk = tfilter.getChunk(chunkrow, chunkcol)
            setWorldChunk( testworld, currchunk, chunkrow, chunkcol)
            
            # save to graph
            currchunkheight = terrainheight.getChunkHeights( chunkrow , chunkcol )
            if westwardstrip == None:
                westwardstrip = currchunkheight
            else:
                westwardstrip = numpy.append( westwardstrip, currchunkheight, axis = 1)
        if fullmap == None:
            fullmap = westwardstrip
        else:
            fullmap = numpy.append( fullmap, westwardstrip, axis = 0)
    savechunkimage(fullmap, 'world_savetest_hugemap')

    #print "Input chunk\n========\n", dummychunk
    #print "Output chunk\n========\n",getWorldChunk(testworld, 0,0)
    saveWorld(testworld)
    renderWorld("world_savetest_testworld", "world_savetest_testworld-"+str(worldseed)+"-"+str(32)+"x"+str(32))

def filtertest():
    testworld = createWorld("filtertest_testworld")
    #random.seed()
    worldseed = 12397 # random.randint(0, 65535)
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
    tfilter = Landmark(worldseed, tfilter, 255, 255) # a single landmark
    tfilter = Landmark(worldseed, tfilter, 0, 0) # a single landmark
    tfilter = Landmark(worldseed, tfilter, 0, 255) # a single landmark
    tfilter = Landmark(worldseed, tfilter, 255, 0) # a single landmark
    tfilter = Landmark(worldseed, tfilter, 128, 128) # a single landmark
    tfilter = Landmark(worldseed, tfilter, -20, -10) # a single landmark
    tfilter = Landmark(worldseed, tfilter, 300, 258) # a single landmark

    # Generate minecraft level
    for chunkrow in xrange(worldsizex):
        print "Generating westward chunk strip", chunkrow
        for chunkcol in xrange(worldsizez):
            #print "\n========\nChunk", (chunkrow, chunkcol), "\n========"        
            currchunk = tfilter.getChunk(chunkrow, chunkcol)
            setWorldChunk( testworld, currchunk, chunkrow, chunkcol)
    saveWorld(testworld)
    renderWorld("filtertest_testworld", "filtertest_testworld-"+str(worldseed)+"-"+str(worldsizex)+"x"+str(worldsizez))
    print "World seed is", worldseed

def blendfiltertest():
    random.seed()
    worldseed = random.randint(0, 65535)
    worldsizex = 16
    worldsizez = 16
    print "World seed is", worldseed
    
    terrheightmask = DSLayer2d(worldseed,
                            chunkvolatility = 0.25, 
                            regionvolatility = 1.0, 
                            chunkinitdepth = 1 ) # Terrain height generation


    terrheightmask2 = DSLayer2d(worldseed + 1234,
                            chunkvolatility = 0.25, 
                            regionvolatility = 1.0, 
                            chunkinitdepth = 2 ) # Terrain height generation

    maskdata = numpy.ones( [16,16] )
    maskdata[:8,:] = 0.0
    alphamask = LayerMask2d(maskdata)

    blending = BlendMaskFilter2d( terrheightmask, terrheightmask2)
    
    savechunkimage(terrheightmask.getChunkHeights(0,0), 'blendfiltertest_firstheights') 
    savechunkimage(terrheightmask2.getChunkHeights(0,0), 'blendfiltertest_secondheights') 
    savechunkimage(blending.getChunkHeights(0,0), 'blendfiltertest_blendedheights') 

if __name__ == "__main__":
    if not os.path.isdir("renders"):
        os.mkdir("renders")
    ds_unittest()
    ds_2dplottest()
    ds_1dplottest()
    lg_unittest()
    world_savetest()
    filtertest()
    blendfiltertest()
    print "Tests complete."


