#!/usr/bin/env python

"""

Generator for map-relevant datasets: layers!

"""

import random
import math
import copy

from diamondsquare import * # generates plasma noise
from constants import * # stores such cool constants as CHUNK_WIDTH_IN_BLOCKS and MAT_AIR

__all__ = ["Layer", "Filter", "WaterLevelFilter", "TopSoilFilter", "SnowCoverFilter", "CacheFilter",
            "LayerMask2d", "MaskFilter2d", "BlendMaskFilter2d", "ThresholdMaskFilter2d", "DSLayerMask2d", 
            "HeightMaskRenderFilter"]

#########################################################################
# Layer and Filter: output chunk block ID data (a chunk-sized 3D array of integers)
#########################################################################

class Chunk(object):
    """
    Implements a single chunk. Contains block ID's, data, entities, etc.
    """
    cx = None
    cz = None
    blocks = None
    data = None
    
    def __init__(self, cx, cz, fillmaterial=MAT_AIR):
        if type(cx) != int or type(cz) != int: raise RuntimeError, "chunk coordinates must be of type int"
        # Passing None to fillmaterial allows us to create an empty chunk, without even block or data arrays. Saves on overhead.
        if fillmaterial != None:
            self.blocks = [[[fillmaterial for vert in xrange(CHUNK_HEIGHT_IN_BLOCKS)] for row in xrange(CHUNK_WIDTH_IN_BLOCKS)] for col in xrange(CHUNK_WIDTH_IN_BLOCKS)]
            self.data = [[[0 for vert in xrange(CHUNK_HEIGHT_IN_BLOCKS)] for row in xrange(CHUNK_WIDTH_IN_BLOCKS)] for col in xrange(CHUNK_WIDTH_IN_BLOCKS)]
        self.cx = cx
        self.cz = cz

    # TODO: for some reason, this causes a segmentation fault.
    #def __copy__(self):
        #newchunk = copy.copy(self)
        #newchunk.blocks = copy.deepcopy(self.blocks)
        #newchunk.data = copy.deepcopy(self.data)
        #return newchunk

    def copy(self):
        newchunk = copy.copy(self)
        xlen = len(self.blocks)
        zlen = len(self.blocks[0])
        ylen = len(self.blocks[0][0])
        newchunk.blocks = [[ list(self.blocks[x][z]) for z in xrange( zlen )] for x in xrange( xlen )] 
        newchunk.data = [[ list(self.data[x][z]) for z in xrange( zlen )] for x in xrange( xlen )] 
        return newchunk

class Layer(object):
    """
    Implements a layer of minecraft blocks 
    """
    def getChunk(self, cx, cz):
        return Chunk(cx, cz)

class Filter(Layer):
    """
    Implements a layer which draws chunk block from its input and outputs chunk block data.

    This superclass acts as a passthrough filter for chunk block data. Subclass this and override
    Filter.getChunk() to create more interesting filters.

    inputlayer must either be a Layer, a subclass of Layer, or None (in which case you will need to
    set the inputlayer later.)
    """
    inputlayer = None
    def __init__(self, inputlayer):
        if inputlayer != None and not issubclass(type(inputlayer), Layer ): raise RuntimeError, "input to filter must be a layer type (or subclass thereof) or none"
        self.inputlayer = inputlayer

    def getChunk(self, cx, cz):
        """
        Sample filter: act as a pass-through filter.
        """
        return self.inputlayer.getChunk(cx, cz)

    def setInputLayer(self, inputlayer):
        """
        Set the input layer of a Filter.

        Don't use this too often. You run the risk of creating cyclic pipelines, and causing
        python to shit a brick.
        """
        if inputlayer == None or not issubclass(type(inputlayer), Layer ): raise RuntimeError, "input to filter must be a layer type (or subclass thereof)"
        self.inputlayer = inputlayer


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
        chunk = self.inputlayer.getChunk(cx, cz)
        findid = self.findid
        replaceid = self.replaceid
        for row in chunk.blocks:
            for col in row:
                for ix in xrange(self.rangebottom, min( len(col), self.rangetop + 1) ):
                    if col[ix] == findid:
                        col[ix] = self.replaceid
        return chunk 

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
        airid = self.airid
        findid = self.findid
        replaceid = self.replaceid
        thickness = self.thickness
        rangetop = self.rangetop
        rangebottom = self.rangebottom
        workingrange = range(self.rangebottom, self.rangetop + 1)
        workingrange.reverse()
        for row in chunk.blocks:
            for col in row: # for all vertical columns:
                # first block must be an air block
                if col[rangetop] != airid: continue
                # work downward and replace only self.thickness of the blocks.
                for hix in workingrange:
                    element = col[hix]
                    if element == findid:
                        if thickness > 0: # replace blocks 
                            #col[max(hix-thickness+1, 0):hix+1] = replaceid
                            for i in xrange( max(hix-thickness+1, 0), hix+1 ):
                                col[i] = replaceid
                        elif self.thickness < 0: # cake over with blocks
                            for i in xrange( hix+1, min(hix-thickness+1,CHUNK_HEIGHT_IN_BLOCKS) ):
                                col[i] = replaceid
                    if element != airid: break # we search only through the air

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
        workingrange = range(rangebottom, rangetop + 1)
        workingrange.reverse()
        for row in chunk.blocks:
            for col in row: # for all vertical columns:
                # first block must be an air block
                if col[rangetop] != airid: continue
                # work downward and replace only self.thickness of the blocks.
                for hix in workingrange:           
                    if col[hix] != airid:  # we search only through the air
                        for i in xrange(hix+1, hix+1+thickness):
                            col[i] = snowid
                        break

        return chunk

class CacheFilter(Filter):
    """
    Implements a caching passthru filter.

    If the input chunk has already been requested and cached, we just pull from the cache.

    inputlayer must either be a Layer, a subclass of Layer, or None (in which case you will need to
    set the inputlayer later.)
    """
    cache = None
    def __init__(self, inputlayer):
        Filter.__init__(self, inputlayer)
        self.cache = {}

    def getChunk(self, cx, cz):
        """
        Sample filter: act as a pass-through filter.
        """
        if not (cx, cz) in self.cache:
            passchunk = self.inputlayer.getChunk(cx, cz)
            #savechunk = copy.copy(passchunk)
            savechunk = passchunk.copy()
            self.cache[ (cx,cz) ] = savechunk
            return passchunk
        else:
            #return copy.copy(self.cache[ (cx,cz) ] )
            return self.cache[ (cx,cz) ].copy()

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
            outarr = [[-1.0 for z in xrange(CHUNK_WIDTH_IN_BLOCKS)] for x in xrange(CHUNK_WIDTH_IN_BLOCKS)]
            for x in xrange(CHUNK_WIDTH_IN_BLOCKS):
                for z in xrange(CHUNK_WIDTH_IN_BLOCKS):
                    outarr[x][z] = firstheights[x][z] * (1.0 - alphaheights[x][z]) + secondheights[x][z] * alphaheights[x][z]
            return outarr
        else:
            outarr = [[-1.0 for z in xrange(CHUNK_WIDTH_IN_BLOCKS)] for x in xrange(CHUNK_WIDTH_IN_BLOCKS)]
            for x in xrange(CHUNK_WIDTH_IN_BLOCKS):
                for z in xrange(CHUNK_WIDTH_IN_BLOCKS):
                    outarr[x][z] = firstheights[x][z] * (1.0 - self.blendscale) + secondheights[x][z] * self.blendscale
            return outarr

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
        arr = [[-1.0 for col in xrange(CHUNK_WIDTH_IN_BLOCKS + 1)] for row in xrange(CHUNK_WIDTH_IN_BLOCKS + 1)]

        arr[0][0] = chunkcorners[chunksouth][chunkwest]
        arr[len(arr)-1][0] = chunkcorners[chunksouth + 1][chunkwest]
        arr[0][len(arr[0])-1] = chunkcorners[chunksouth][chunkwest + 1]
        arr[len(arr)-1][len(arr[0])-1] = chunkcorners[chunksouth + 1][chunkwest + 1]

        # First, generate edges, in order to seam up chunks.
        edgearr = [-1.0 for row in xrange(CHUNK_WIDTH_IN_BLOCKS + 1)]
        edgearr[0] = arr[0][0]
        edgearr[CHUNK_WIDTH_IN_BLOCKS] = arr[0][CHUNK_WIDTH_IN_BLOCKS]
        diamondsquare1D(edgearr ,seed = self.seed, volatility = self.chunkvolatility, initdepth = self.chunkinitdepth)
        for i in xrange(CHUNK_WIDTH_IN_BLOCKS + 1): arr[0][i] = edgearr[i]

        edgearr = [-1.0 for row in xrange(CHUNK_WIDTH_IN_BLOCKS + 1)]
        edgearr[0] = arr[CHUNK_WIDTH_IN_BLOCKS][0]
        edgearr[CHUNK_WIDTH_IN_BLOCKS] = arr[CHUNK_WIDTH_IN_BLOCKS][CHUNK_WIDTH_IN_BLOCKS]
        diamondsquare1D(edgearr ,seed = self.seed, volatility = self.chunkvolatility, initdepth = self.chunkinitdepth)
        for i in xrange(CHUNK_WIDTH_IN_BLOCKS + 1): arr[CHUNK_WIDTH_IN_BLOCKS][i] = edgearr[i]

        edgearr = [-1.0 for row in xrange(CHUNK_WIDTH_IN_BLOCKS + 1)]
        edgearr[0] = arr[0][0]
        edgearr[CHUNK_WIDTH_IN_BLOCKS] = arr[CHUNK_WIDTH_IN_BLOCKS][0]
        diamondsquare1D(edgearr ,seed = self.seed, volatility = self.chunkvolatility, initdepth = self.chunkinitdepth)
        for i in xrange(CHUNK_WIDTH_IN_BLOCKS + 1): arr[i][0] = edgearr[i]

        edgearr = [-1.0 for row in xrange(CHUNK_WIDTH_IN_BLOCKS + 1)]
        edgearr[0] = arr[0][CHUNK_WIDTH_IN_BLOCKS]
        edgearr[CHUNK_WIDTH_IN_BLOCKS] = arr[CHUNK_WIDTH_IN_BLOCKS][CHUNK_WIDTH_IN_BLOCKS]
        diamondsquare1D(edgearr ,seed = self.seed, volatility = self.chunkvolatility, initdepth = self.chunkinitdepth)
        for i in xrange(CHUNK_WIDTH_IN_BLOCKS + 1): arr[i][CHUNK_WIDTH_IN_BLOCKS] = edgearr[i]

        # Then fill in the rest!
        diamondsquare2D(arr, seed = self.seed, volatility = self.chunkvolatility, initdepth = self.chunkinitdepth)

        outarr = []
        for i in xrange(CHUNK_WIDTH_IN_BLOCKS):
            outarr.append( arr[i][0:CHUNK_WIDTH_IN_BLOCKS] )

        return outarr # we slice the first 16 values in each dimension to create an even chunk.

    
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
        arr = [[-1.0 for col in xrange(REGION_WIDTH_IN_CHUNKS + 1)] for row in xrange(REGION_WIDTH_IN_CHUNKS + 1)]
        
        arr[0][0] = self.getregioncorner( (regionsouth,regionwest) )
        arr[len(arr)-1][0] = self.getregioncorner( (regionsouth + 1,regionwest) )
        arr[0][len(arr[0])-1] = self.getregioncorner( (regionsouth,regionwest + 1) )
        arr[len(arr)-1][len(arr[0])-1] = self.getregioncorner( (regionsouth + 1,regionwest + 1) )

        # First, generate edges, in order to seam up chunks.

        edgearr = [-1.0 for row in xrange(REGION_WIDTH_IN_CHUNKS + 1)]
        edgearr[0] = arr[0][0]
        edgearr[REGION_WIDTH_IN_CHUNKS] = arr[0][REGION_WIDTH_IN_CHUNKS]
        diamondsquare1D(edgearr ,seed = self.seed, volatility = self.regionvolatility)
        for i in xrange(REGION_WIDTH_IN_CHUNKS + 1): arr[0][i] = edgearr[i]

        edgearr = [-1.0 for row in xrange(REGION_WIDTH_IN_CHUNKS + 1)]
        edgearr[0] = arr[REGION_WIDTH_IN_CHUNKS][0]
        edgearr[REGION_WIDTH_IN_CHUNKS] = arr[REGION_WIDTH_IN_CHUNKS][REGION_WIDTH_IN_CHUNKS]
        diamondsquare1D(edgearr ,seed = self.seed, volatility = self.regionvolatility)
        for i in xrange(REGION_WIDTH_IN_CHUNKS + 1): arr[REGION_WIDTH_IN_CHUNKS][i] = edgearr[i]

        edgearr = [-1.0 for row in xrange(REGION_WIDTH_IN_CHUNKS + 1)]
        edgearr[0] = arr[0][0]
        edgearr[REGION_WIDTH_IN_CHUNKS] = arr[REGION_WIDTH_IN_CHUNKS][0]
        diamondsquare1D(edgearr ,seed = self.seed, volatility = self.regionvolatility)
        for i in xrange(REGION_WIDTH_IN_CHUNKS + 1): arr[i][0] = edgearr[i]

        edgearr = [-1.0 for row in xrange(REGION_WIDTH_IN_CHUNKS + 1)]
        edgearr[0] = arr[0][REGION_WIDTH_IN_CHUNKS]
        edgearr[REGION_WIDTH_IN_CHUNKS] = arr[REGION_WIDTH_IN_CHUNKS][REGION_WIDTH_IN_CHUNKS]
        diamondsquare1D(edgearr ,seed = self.seed, volatility = self.regionvolatility)
        for i in xrange(REGION_WIDTH_IN_CHUNKS + 1): arr[i][REGION_WIDTH_IN_CHUNKS] = edgearr[i]

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
        chunk = Chunk(cx, cz)
        blocks = chunk.blocks
        blockid = self.blockid
        rangetop = self.rangetop
        rangebottom = self.rangebottom
        rangeheight = self.rangetop - self.rangebottom
        # Copy height information into 3D block array
        for row in xrange(CHUNK_WIDTH_IN_BLOCKS):
            for col in xrange(CHUNK_WIDTH_IN_BLOCKS):
                # we limit the vertical range in which the heightmap lives.
                blockheight = int( heights[row][col] * (rangeheight) + rangebottom )
                blockslice = blocks[row][col]
                for ix in xrange(blockheight):
                    blockslice[ix] = blockid
        return chunk
   
