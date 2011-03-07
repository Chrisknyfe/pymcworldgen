#!/usr/bin/env python

"""

Generator for map-relevant datasets: layers!

"""

import random
import math
import numpy

from diamondsquare import * # generates plasma noise
from constants import * # stores such cool constants as CHUNK_WIDTH_IN_BLOCKS and MAT_AIR

__all__ = ["Layer", "Filter", "WaterLevelFilter", "TopSoilFilter", "SnowCoverFilter",
            "LayerMask2d", "MaskFilter2d", "BlendMaskFilter2d", "ThresholdMaskFilter2d", "DSLayerMask2d", 
            "HeightMaskRenderFilter"]

#########################################################################
# Layer and Filter: output chunk block ID data (a chunk-sized 3D array of integers)
#########################################################################

class Layer(object):
    """
    Implements a layer of chunk blocks 
    """
    def getChunk(self, cx, cz):
        return numpy.zeros( [CHUNK_WIDTH_IN_BLOCKS, CHUNK_WIDTH_IN_BLOCKS, CHUNK_HEIGHT_IN_BLOCKS] )

class Filter(Layer):
    """
    Implements a layer which draws chunk block from its input and outputs chunk block data.

    This superclass acts as a passthrough filter for chunk block data.
    """
    inputlayer = None
    def __init__(self, inputlayer):
        assert ( issubclass(type(inputlayer), Layer ) )
        self.inputlayer = inputlayer

    def getChunk(self, cx, cz):
        """
        Sample filter: act as a pass-through filter.
        """
        #print "passthru chunk", (cx, cz)
        return self.inputlayer.getChunk(cx, cz)


class WaterLevelFilter(Filter):
    """
    A filter that does a find-replace of all blocks within a certain height range (endpoint inclusive)
    """
    rangebottom = None
    rangetop = None
    findid = None
    replaceid = None
    def __init__(self, inputlayer, rangebottom = 0, rangetop = CHUNK_HEIGHT_IN_BLOCKS / 2, findid = MAT_AIR, replaceid = MAT_WATER):
        super(WaterLevelFilter, self).__init__(inputlayer)
        self.rangebottom = rangebottom
        self.rangetop = rangetop
        self.findid = findid
        self.replaceid = replaceid

    def getChunk(self, cx, cz):
        chunk = self.inputlayer.getChunk(cx, cz) # get
        chunkrange = chunk[:,:, self.rangebottom : self.rangetop + 1] # range
        findfilter = ( chunkrange == self.findid ) # find
        chunkrange[findfilter] = self.replaceid # replace
        return chunk # put

class TopSoilFilter(Filter):
    """
    A filter for replacing the top layer of a material with another
    """
    rangebottom = None
    rangetop = None
    findid = None
    replaceid = None
    thickness = None
    airid = None
    def __init__(self, inputlayer, rangebottom = 0, rangetop = CHUNK_HEIGHT_IN_BLOCKS - 1, findid = MAT_STONE, replaceid = MAT_DIRT, thickness = 4, airid = MAT_AIR):
        super(TopSoilFilter, self).__init__(inputlayer)
        self.rangebottom = rangebottom
        self.rangetop = rangetop
        self.findid = findid
        self.replaceid = replaceid
        self.thickness = thickness
        self.airid = airid

    def getChunk(self, cx, cz):
        chunk = self.inputlayer.getChunk(cx, cz)

        if self.thickness == 0: return chunk # passthru if we're not adding anything for some reason
        workingrange = range(self.rangebottom, self.rangetop)
        for row in chunk:
            for col in row: # for all vertical columns:
                # first block must be an air block
                if col[self.rangetop] != self.airid: continue
                # work downward and replace only self.thickness of the blocks.
                for hix in reversed(workingrange):
                    element = col[hix]
                    if element == self.findid:
                        if self.thickness > 0: # replace blocks 
                            col[max(hix-self.thickness+1, 0):hix+1] = self.replaceid
                        elif self.thickness < 0: # cake over with blocks
                            col[hix+1:min(hix-self.thickness+1,CHUNK_HEIGHT_IN_BLOCKS)] = self.replaceid
                    if element != self.airid: break # we search only through the air

        return chunk # put

class SnowCoverFilter(Filter):
    """
    A filter for replacing the top layer of a material with another
    """
    rangebottom = None
    rangetop = None
    snowid = None
    thickness = None
    airid = None
    def __init__(self, inputlayer, rangebottom = 0, rangetop = CHUNK_HEIGHT_IN_BLOCKS - 1, snowid = MAT_SNOW, thickness = 1, airid = MAT_AIR):
        super(SnowCoverFilter, self).__init__(inputlayer)
        self.rangebottom = rangebottom
        self.rangetop = rangetop
        self.snowid = snowid
        self.thickness = thickness
        self.airid = airid

    def getChunk(self, cx, cz):
        chunk = self.inputlayer.getChunk(cx, cz)

        if self.thickness <= 0: return chunk # passthru if we're not adding anything for some reason
        # Pull out variables that don't change with iteration
        airid = self.airid
        thickness = self.thickness
        snowid = self.snowid
        rangetop = self.rangetop
        rangebottom = self.rangebottom
        workingrange = range(rangebottom, rangetop)
        workingrange.reverse()
        for row in chunk:
            for col in row: # for all vertical columns:
                # first block must be an air block
                if col[rangetop] != airid: continue
                # work downward and replace only self.thickness of the blocks.
                for hix in workingrange:           
                    if col[hix] != airid:  # we search only through the air
                        col[hix+1:hix+1+thickness] = snowid
                        break

        return chunk

#########################################################################
# LayersMask2d and MaskFilter2d: output chunk heightmap data (a chunk-sized 2d array of values from 0.0 to 1.0)
#########################################################################

class LayerMask2d(object):
    """
    A 2d layer mask of height values (between 0.0 and 1.0). Can double as a terrain heightmap.

    You can seed this LayerMask2d with initial data, or just leave it blank.
    """
    initialdata = None
    def __init__(self, initialdata = None):
        if initialdata is not None:
            assert( len(initialdata) == CHUNK_WIDTH_IN_BLOCKS)
            assert(len(initialdata[0]) == CHUNK_WIDTH_IN_BLOCKS)
            self.initialdata = initialdata

    def getChunkHeights(self, cx, cz):
        if self.initialdata is not None: 
            return self.initialdata
        return numpy.ones( [CHUNK_WIDTH_IN_BLOCKS, CHUNK_WIDTH_IN_BLOCKS] )

class MaskFilter2d(LayerMask2d):
    """
    Implements a layer which draws data from its inputs and outputs a 2D LayerMask2d.

    This superclass acts as a passthrough filter for LayerMask2ds.
    """
    inputlayer = None
    def __init__(self, inputlayer):
        assert ( issubclass(type(inputlayer), LayerMask2d ) )
        self.inputlayer = inputlayer

    def getChunkHeights(self, cx, cz):
        """
        Sample filter: act as a pass-through filter.
        """
        #print "passthru chunk", (cx, cz)
        return self.inputlayer.getChunkHeights(cx, cz)

class BlendMaskFilter2d(LayerMask2d):
    """
    Blends two input LayerMask2ds given either an alphamask or a blendscale.
    
    Blendscale slides the blending between the two layers. If blendscale is closer
    to 0.0, firstlayer is more prominent. if 1.0, secondlayer is more prominent.
    """
    firstlayer = None
    secondlayer = None
    alphamask = None
    blendscale = None
    def __init__(self, firstlayer, secondlayer, alphamask = None, blendscale = 0.5):
        assert ( issubclass(type(firstlayer), LayerMask2d ) )
        assert ( issubclass(type(secondlayer), LayerMask2d ) )
        if alphamask is not None:
            assert ( issubclass(type(alphamask), LayerMask2d ) )
        assert ( type(blendscale) == float and 0.0 <= blendscale <= 1.0 )
        self.firstlayer = firstlayer
        self.secondlayer = secondlayer
        self.alphamask = alphamask
        self.blendscale = blendscale

    def getChunkHeights(self, cx, cz):
        """
        Blend two input LayerMask2ds given either an alphamask or a blendscale.
        """
        firstheights = self.firstlayer.getChunkHeights(cx, cz)
        secondheights = self.secondlayer.getChunkHeights(cx, cz)
        if self.alphamask is not None:
            alphaheights = self.alphamask.getChunkHeights(cx, cz)
            return firstheights * (1.0 - alphaheights) + secondheights * alphaheights
        else:
            return ( firstheights * (1.0 - self.blendscale) ) + ( secondheights * self.blendscale )

class ThresholdMaskFilter2d(LayerMask2d):
    """
    Imposes a threshold on the incoming layermask2d.
    """
    inputlayer = None
    thresholdbottom = None
    thresholdtop = None
    def __init__(self, inputlayer, thresholdbottom = 0.5, thresholdtop = 1.0):
        assert ( issubclass(type(inputlayer), LayerMask2d ) )
        self.inputlayer = inputlayer
        self.thresholdbottom = thresholdbottom
        self.thresholdtop = thresholdtop

    def getChunkHeights(self, cx, cz):
        """
        Threshold the mask filter
        """
        heights = self.inputlayer.getChunkHeights(cx, cz)
        thresher = ( self.thresholdbottom <= heights ) & ( heights <= self.thresholdtop ) # create an indexing array
        heights[thresher] = 1.0
        heights[thresher == False] = 0.0
        return heights

class DSLayerMask2d(LayerMask2d):

    """
    Two-dimensional diamond-square heightmap layer.
    """
    
    seed = None
    chunkvolatility = None # diamond-square randomness for a chunk
    regionvolatility = None # diamond-square randomness for a region
    chunkinitdepth = None # initial recursion depth for chunk generation (chunkvolatility**chunkinitdepth for starting chunk volatility)
    regioncache = None # a dictionary of regions we have already generated.

    blockheightoverrides = None

    def __init__(self, seed, chunkvolatility = 0.5, regionvolatility = 0.4, chunkinitdepth = 3):
        self.seed = seed
        self.chunkvolatility = chunkvolatility
        self.regionvolatility = regionvolatility
        self.chunkinitdepth = chunkinitdepth

        self.regioncache = {}

        self.blockheightoverrides = {}

    def setOverrides( overridelist ):
        raise NotImplementedError("I don't know what format setOverrides should take!")
    
    def getregioncorner(self, coord ):
        """
        Get the corner height of a region (well, four neighboring regions, anyway.)
        
        coord - the coordinates of the region corner, region-sized (512 blocks wide)
        """

        assert( type(coord[0]) == int )
        assert( type(coord[1]) == int )
        assert( type(self.seed) == int )

        regionsouth = coord[0]
        regionwest = coord[1]
        random.seed( self.seed ^ ((regionsouth & 0xFFFF0000) | (regionwest & 0x0000FFFF)) )
        random.jumpahead( ((regionwest & 0xFFFF0000) | (regionsouth & 0x0000FFFF)) ) 

        corner = random.random()
        #print "Region corner", (regionsouth, regionwest), "is", corner
        return corner

    
    def getChunkHeights(self, cx, cz):
        """
        Get the heightmap for a 16 block x 16 block chunk.        
        """
        chunksouth = cx % REGION_WIDTH_IN_CHUNKS
        chunkwest = cz % REGION_WIDTH_IN_CHUNKS
        regionsouth = int(math.floor(cx / REGION_WIDTH_IN_CHUNKS))
        regionwest = int(math.floor(cz / REGION_WIDTH_IN_CHUNKS))

        # Get region chunk corners
        chunkcorners = self.getRegionChunkCornerHeights( (regionsouth, regionwest) )

        # Generate chunk data using desired chunk corners
        # using numpy array so we can do a 2D slice to output this array
        arr = numpy.array([[-1.0 for col in xrange(CHUNK_WIDTH_IN_BLOCKS + 1)] for row in xrange(CHUNK_WIDTH_IN_BLOCKS + 1)])

        arr[0][0] = chunkcorners[chunksouth][chunkwest]
        arr[len(arr)-1][0] = chunkcorners[chunksouth + 1][chunkwest]
        arr[0][len(arr[0])-1] = chunkcorners[chunksouth][chunkwest + 1]
        arr[len(arr)-1][len(arr[0])-1] = chunkcorners[chunksouth + 1][chunkwest + 1]

        # First, generate edges, in order to seam up chunks.
        diamondsquare1D(arr[0,:] ,seed = self.seed, volatility = self.chunkvolatility, initdepth = self.chunkinitdepth)
        diamondsquare1D(arr[CHUNK_WIDTH_IN_BLOCKS,:] ,seed = self.seed, volatility = self.chunkvolatility, initdepth = self.chunkinitdepth)
        diamondsquare1D(arr[:,0] ,seed = self.seed, volatility = self.chunkvolatility, initdepth = self.chunkinitdepth)
        diamondsquare1D(arr[:,CHUNK_WIDTH_IN_BLOCKS] ,seed = self.seed, volatility = self.chunkvolatility, initdepth = self.chunkinitdepth)
        # Then fill in the rest!
        diamondsquare2D(arr, seed = self.seed, volatility = self.chunkvolatility, initdepth = self.chunkinitdepth)

        return arr[0:CHUNK_WIDTH_IN_BLOCKS,0:CHUNK_WIDTH_IN_BLOCKS] # we slice the first 16 values in each dimension to create an even chunk.

    
    def getRegionChunkCornerHeights(self, regioncoord):
        """
        Get the heightmap for the chunk corners within a region.     
        """
        regionsouth = regioncoord[0]
        regionwest = regioncoord[1]

        # Grab from the cache so we don't have to regenerate the region every time.
        if ( regioncoord in self.regioncache ):
            return self.regioncache[regioncoord]

        # Generate region chunk corners
        arr = numpy.array([[-1.0 for col in xrange(REGION_WIDTH_IN_CHUNKS + 1)] for row in xrange(REGION_WIDTH_IN_CHUNKS + 1)])
        
        arr[0][0] = self.getregioncorner( (regionsouth,regionwest) )
        arr[len(arr)-1][0] = self.getregioncorner( (regionsouth + 1,regionwest) )
        arr[0][len(arr[0])-1] = self.getregioncorner( (regionsouth,regionwest + 1) )
        arr[len(arr)-1][len(arr[0])-1] = self.getregioncorner( (regionsouth + 1,regionwest + 1) )

        # First, generate edges, in order to seam up chunks.
        diamondsquare1D(arr[0,:] ,seed = self.seed, volatility = self.regionvolatility)
        diamondsquare1D(arr[REGION_WIDTH_IN_CHUNKS,:] ,seed = self.seed, volatility = self.regionvolatility)
        diamondsquare1D(arr[:,0] ,seed = self.seed, volatility = self.regionvolatility)
        diamondsquare1D(arr[:,REGION_WIDTH_IN_CHUNKS] ,seed = self.seed, volatility = self.regionvolatility)
        # Then fill in the rest!
        diamondsquare2D(arr, seed = self.seed, volatility = self.regionvolatility)

        # cache the region so we can save on processing power later.
        self.regioncache[regioncoord] = arr

        return arr

#########################################################################
# Hybrid filters: convert one output type to another
#########################################################################

class HeightMaskRenderFilter(Layer):
    """
    Renders a LayerMask2d to block data as block heights. 
    """
    inputlayer = None
    blockid = None
    rangebottom = None
    rangetop = None # 
    def __init__(self, inputlayer, blockid = MAT_STONE, rangebottom = 50, rangetop = 100 ):
        assert ( issubclass(type(inputlayer), LayerMask2d ) )
        self.inputlayer = inputlayer
        self.blockid = blockid
        self.rangebottom = rangebottom
        self.rangetop = rangetop

    def getChunk(self, cx, cz):
        # 2D array
        heights = self.inputlayer.getChunkHeights( cx,cz )
        # 3D array
        blocks = numpy.zeros( [CHUNK_WIDTH_IN_BLOCKS,CHUNK_WIDTH_IN_BLOCKS,CHUNK_HEIGHT_IN_BLOCKS] ) 

        # Copy height information into 3D block array
        for row in xrange(CHUNK_WIDTH_IN_BLOCKS):
            for col in xrange(CHUNK_WIDTH_IN_BLOCKS):
                # we limit the vertical range in which the heightmap lives.
                blockheight = int( heights[row,col] * (self.rangetop - self.rangebottom) + self.rangebottom ) 
                blocks[row,col,0:blockheight] = self.blockid

        return blocks



        
