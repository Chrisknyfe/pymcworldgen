#!/usr/bin/env python

"""

Landmark generation - interspersed landmarks on the terrain

"""

import random
import math
import copy
#import numpy
from layer import *
from constants import *


#########################################################################
# Base Classes: Landmark and LandmarkGenerator
#########################################################################

class Landmark(Filter):
    """
    A chunk generator for a single landmark somewhere in the world.

    Override editChunk() to create your own landmarks.
    Override __copy__() if you keep pointers to data as member variables in your subclasses, since LandmarkGenerator WILL
    copy instances of your subclass.
    """
    seed = None
    x = None
    z = None
    y = None
    
    # Viewrange is generally a property of a class, but an instance may choose to modify it.
    viewrange = 0
    # Set to TRUE if you want to cancel generation of this landmark.
    drawcancelled = None

    def __init__(self, inputlayer, seed = 0, x = 0, z = 0, y = 0):
        """
        Landmark constructor. Random seed necessary. terrainlayer necessary.
        if x and z are None, we generate at a random point? I don't really like that behavior
        how about we generate at 0,0. Layermask can prevent us from spawning in
        certain places, or give us a random probability that we won't spawn in an area.
        """
        Filter.__init__(self, inputlayer)
        self.seed = seed
        self.x = x
        self.z = z
        self.y = y
        self.drawcancelled = False

    def setPos(self, x, z, y):
        """
        Set the position of this landmark. 
        """
        self.x = x
        self.z = z
        self.y = y

    def setSeed(self, seed):
        self.seed = seed

    def isLandmarkInChunk(self, cx, cz):
        """
        Determine whether the given chunk contains a portion of this landmark.
        """
        bxrange = (cx*CHUNK_WIDTH_IN_BLOCKS - self.viewrange, (cx+1)*CHUNK_WIDTH_IN_BLOCKS + self.viewrange)
        bzrange = (cz*CHUNK_WIDTH_IN_BLOCKS - self.viewrange, (cz+1)*CHUNK_WIDTH_IN_BLOCKS + self.viewrange)

        if ( bxrange[0] <= self.x < bxrange[1] ) and ( bzrange[0] <= self.z < bzrange[1] ):
            return True
        else:
            return False

    def findHighestGround(self, airid = MAT_AIR):
        # Find our actual Y at the x,z spawn coordinates.
        # but before that, we need the correct chunk.
        originchunkx = self.x / CHUNK_WIDTH_IN_BLOCKS
        originchunkz = self.z / CHUNK_WIDTH_IN_BLOCKS
        originchunk = self.inputlayer.getChunk(originchunkx, originchunkz).blocks
        # now that we have the correct origin chunk, let's search for the tree's ground height.
        downrange = range( 0, CHUNK_HEIGHT_IN_BLOCKS - 1 )
        downrange.reverse()
        actualy = None
        actualyid = None
        chunkoffsetx = self.x % CHUNK_WIDTH_IN_BLOCKS
        chunkoffsetz = self.z % CHUNK_WIDTH_IN_BLOCKS
        for y in downrange:
            actualyid = originchunk[chunkoffsetx][chunkoffsetz][y]
            if actualyid != airid:
                actualy = y + 1
                break
        # Set proper return value
        if actualy == None: return None
        else: return (actualy, actualyid)

    def stampToChunk(self, inputstamp, outputchunk, offsetx, offsetz, offsety):
        """
        Hoo boy. How to explain this one...?

        Stamp a 3D array of blocks onto the output chunk
        The offset parameters represent the offset of inputarray's lower-north-east corner
        to the current chunk's lower-north-east corner
        """
        # Write the static array into the map. # TODO: MAKE THIS A FUNCTION
        # offsets of lower north-east corner of the array relative to corner block.

        # iterate between the overlapping range, in chunk-space.
        for outx in xrange( max(0, offsetx), min(CHUNK_WIDTH_IN_BLOCKS, offsetx + len(inputstamp) ) ):
            # get the current coordinate in input-space.
            inx = outx - offsetx
            for outz in xrange( max(0, offsetz), min(CHUNK_WIDTH_IN_BLOCKS, offsetz + len(inputstamp[inx]) ) ):
                inz = outz - offsetz
                for outy in xrange( max(0, offsety), min(CHUNK_HEIGHT_IN_BLOCKS, offsety + len(inputstamp[inx][inz]) ) ):
                    iny = outy - offsety
                    if (inputstamp[inx][inz][iny] != MAT_TRANSPARENT):
                        outputchunk[outx][outz][outy] = inputstamp[inx][inz][iny]


    def editChunk(self, cornerblockx, cornerblockz, terrainchunk):
        """
        Edit the input chunk. Override this function to create beautiful procedural
        Landmarks. 
        """
        terrainblocks = terrainchunk.blocks
        # Dummy: output a wood column
        # where in the array does this block belong?
        relx = self.x - cornerblockx
        relz = self.z - cornerblockz
        # only place this down if we're not going to overflow the array
        if ( 0 <= relx < CHUNK_WIDTH_IN_BLOCKS ) and ( 0 <= relz < CHUNK_WIDTH_IN_BLOCKS ):
            for i in xrange(CHUNK_HEIGHT_IN_BLOCKS):
                terrainblocks[relx][relz][i] = MAT_WOOD
            terrainblocks[relx][relz][self.y] = MAT_WATER
        
    def getChunk(self, cx, cz):
        """
        Output a chunk for processing. Do not override! use editChunk instead
        """
        
        # If we aren't in this chunk, either act as a passthru or return an opaque chunk.
        if self.drawcancelled or (not self.isLandmarkInChunk(cx, cz)):
            return self.inputlayer.getChunk(cx, cz)
        # If we are in the chunk, let's write our blocks to the output chunk
        terrainchunk = self.inputlayer.getChunk(cx, cz)
        outputchunk = terrainchunk
        self.editChunk(cx*CHUNK_WIDTH_IN_BLOCKS, cz*CHUNK_WIDTH_IN_BLOCKS, terrainchunk)
        return outputchunk


class LandmarkGenerator(Filter):
    """
    A chunk generator for a random smattering of landmarks throughout the worldde
    """
    seed = None
    landmarklist = None
    density = None
    layermask = None

    # { dict where key is (rx, rz) and value is {dict where key is (cx, cz) and value is [list of Landmarks ] } }
    worldspawns = None 

    def __init__(self, inputlayer, seed, landmarklist = [Landmark], density = 200, layermask = None, rangebottom = 0, rangetop = CHUNK_HEIGHT_IN_BLOCKS):
        # Input landmark list needs to be doublechecked.
        for lmtype in landmarklist:
            if not issubclass(type(lmtype), Landmark): raise TypeError, "landmarklist must only contain Landmark objects."
        # We need to enforce that a cachefilter is placed before the handmark generator, for performance purposes.
        if not issubclass(type(inputlayer), CacheFilter):
            #print "LandmarkGenerator works much faster with a cachefilter at its input, since it requests chunks multiple times."
            #print "Screw it, I'm adding one because the performance boost is eightfold."
            inputlayer = CacheFilter(inputlayer)
        Filter.__init__(self, inputlayer)
        self.seed = seed
        self.density = density
        self.rangetop = rangetop
        self.rangebottom = rangebottom
        self.layermask = layermask
        self.landmarklist = landmarklist
        # This data structure has a lot of indexing structure so we can find relevant points quickly
        self.worldspawns = {} 
        self.layermask = layermask

    def getMaxViewRange(self):
        mvr = 0
        for lmtype in self.landmarklist:
            if lmtype.viewrange > mvr: mvr = lmtype.viewrange
        return mvr

    def getSpawnsInRegion(self, rx, rz):
        # Generate each spawn point and store in regionspawns, otherwise we just get the cached spawnpoints.
        if not (rx, rz) in self.worldspawns:
            # Seed the random number gen with all 64 bits of region coordinate data by using both seed and jumpahead
            random.seed( self.seed ^ ((rx & 0xFFFF0000) | (rz & 0x0000FFFF)) )
            random.jumpahead( ((rx & 0xFFFF0000) | (rz & 0x0000FFFF)) ) 
            # First number should be number of points in region
            numspawns = self.density
            rangetop = self.rangetop
            rangebottom = self.rangebottom

            self.worldspawns[ (rx,rz) ] = {}
            currentregion = self.worldspawns[ (rx,rz) ]
            for ix in xrange(numspawns):
                blockx = random.randint( 0, CHUNK_WIDTH_IN_BLOCKS * REGION_WIDTH_IN_CHUNKS - 1 ) + rx * CHUNK_WIDTH_IN_BLOCKS * REGION_WIDTH_IN_CHUNKS
                blockz = random.randint( 0, CHUNK_WIDTH_IN_BLOCKS * REGION_WIDTH_IN_CHUNKS - 1 ) + rz * CHUNK_WIDTH_IN_BLOCKS * REGION_WIDTH_IN_CHUNKS
                blocky = random.randint( max(0, rangebottom), min(CHUNK_HEIGHT_IN_BLOCKS - 1, rangetop) ) 
                currchunkx = blockx / CHUNK_WIDTH_IN_BLOCKS
                currchunkz = blockz / CHUNK_WIDTH_IN_BLOCKS
                # We store the points for each chunk indexed by chunk
                if not (currchunkx, currchunkz) in currentregion:
                    currentregion[ (currchunkx, currchunkz) ] = []
                # We make a landmark for each point
                lmtypeix = random.randint(0, len(self.landmarklist) - 1)
                lmtype = self.landmarklist[lmtypeix] 
                #lm = lmtype(self.seed, self.terrainlayer, blockx, blockz, blocky)
                lm = copy.copy(lmtype)
                lm.setPos(blockx, blockz, blocky)
                # Lastly we append the landmark to the chunk
                currentregion[ (currchunkx, currchunkz) ].append( lm )
        return self.worldspawns[ (rx,rz) ]
        

    def getSpawnsInChunk(self, cx, cz):
        """
        Gets the spawn points for the selected chunk (reading from the appropriate region cache) 
        """
        rx = cx / REGION_WIDTH_IN_CHUNKS
        rz = cz / REGION_WIDTH_IN_CHUNKS
        regionspawns = self.getSpawnsInRegion(rx, rz)
        if (cx, cz) in regionspawns:
            return regionspawns[ (cx,cz) ]
        else:
            return None
        

    def getSpawnsTouchingChunk(self, cx, cz):
        """
        Gets the spawns within the maximum view range for this landmark generator, rounded up
        to the nearest chunk multiple (for speed of moving the data around.) The landmark generator
        can check on its own whether it's within rendering range of the chunk.
        """
        mvr = self.getMaxViewRange()
        chunkviewrange = (mvr + CHUNK_WIDTH_IN_BLOCKS - 1) / CHUNK_WIDTH_IN_BLOCKS # ceiling div
        spawnlist = []
        for chunkrow in xrange( cx - chunkviewrange, cx + chunkviewrange + 1):
            for chunkcol in xrange( cz - chunkviewrange, cz + chunkviewrange + 1):
                chunkspawns = self.getSpawnsInChunk( chunkrow, chunkcol )
                if chunkspawns != None: spawnlist.extend( chunkspawns )
        return spawnlist

    def getChunk(self, cx, cz):
        """
        Add the landmarks to the existing terrain
        """
        # We build a graph of landmarks, then get a chunk from the entire graph.
        graph = self.inputlayer
        landmarks = self.getSpawnsTouchingChunk(cx,cz)
        if landmarks == None:
            return self.inputlayer.getChunk( cx, cz )
        for mark in landmarks:
            # insert this landmark at the end of the graph    
            mark.setInputLayer( graph )
            graph = mark
        
        return graph.getChunk( cx, cz )



#########################################################################
# Various fun and exciting landmarks
#########################################################################

class StaticTreeLandmark(Landmark):

    # 5x5x5 static tree array, indexed ( x,z,y ) for compatability
    
    statictree =    [
                    [[MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_LEAVES, MAT_TRANSPARENT, MAT_TRANSPARENT],
                    [MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_LEAVES, MAT_TRANSPARENT, MAT_TRANSPARENT],
                    [MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_LEAVES, MAT_TRANSPARENT, MAT_TRANSPARENT],
                    [MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_LEAVES, MAT_TRANSPARENT, MAT_TRANSPARENT],
                    [MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_LEAVES, MAT_TRANSPARENT, MAT_TRANSPARENT]],

                    [[MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_LEAVES, MAT_TRANSPARENT, MAT_TRANSPARENT],
                    [MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_LEAVES, MAT_LEAVES, MAT_TRANSPARENT],
                    [MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_LEAVES, MAT_LEAVES, MAT_LEAVES],
                    [MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_LEAVES, MAT_LEAVES, MAT_TRANSPARENT],
                    [MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_LEAVES, MAT_TRANSPARENT, MAT_TRANSPARENT]],

                    [[MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_LEAVES, MAT_TRANSPARENT, MAT_TRANSPARENT],
                    [MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_LEAVES, MAT_LEAVES, MAT_LEAVES],
                    [MAT_WOOD, MAT_WOOD, MAT_WOOD, MAT_WOOD, MAT_WOOD, MAT_LEAVES],
                    [MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_LEAVES, MAT_LEAVES, MAT_LEAVES],
                    [MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_LEAVES, MAT_TRANSPARENT, MAT_TRANSPARENT]],

                    [[MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_LEAVES, MAT_TRANSPARENT, MAT_TRANSPARENT],
                    [MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_LEAVES, MAT_LEAVES, MAT_TRANSPARENT],
                    [MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_LEAVES, MAT_LEAVES, MAT_LEAVES],
                    [MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_LEAVES, MAT_LEAVES, MAT_TRANSPARENT],
                    [MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_LEAVES, MAT_TRANSPARENT, MAT_TRANSPARENT]],

                    [[MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_LEAVES, MAT_TRANSPARENT, MAT_TRANSPARENT],
                    [MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_LEAVES, MAT_TRANSPARENT, MAT_TRANSPARENT],
                    [MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_LEAVES, MAT_TRANSPARENT, MAT_TRANSPARENT],
                    [MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_LEAVES, MAT_TRANSPARENT, MAT_TRANSPARENT],
                    [MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_TRANSPARENT, MAT_LEAVES, MAT_TRANSPARENT, MAT_TRANSPARENT]]
                    ]

    viewrange = max( len(statictree), len(statictree[0]) ) / 2

    """
    """
    def editChunk(self, cornerblockx, cornerblockz, terrainchunk):
        """
        Place the tree in this chunk!
        """

        # Find our actual Y: place us on the ground.
        ground = self.findHighestGround()

        if ground == None:
            self.drawcancelled = True
            return 
        if ground[1] != MAT_DIRT and ground[1] != MAT_GRASS:
            self.drawcancelled = True
            return
        
        actualy = ground[0]
        # Write the static array into the map. # TODO: MAKE THIS A FUNCTION
        # offsets of lower north-east corner of the array relative to corner block.
        offsetx = self.x - cornerblockx - self.viewrange
        offsetz = self.z - cornerblockz - self.viewrange
        offsety = actualy 

        self.stampToChunk( self.statictree, terrainchunk.blocks, offsetx, offsetz, offsety )


class CubicOreLandmark(Landmark):

    viewrange = None
    sizex = None
    sizez = None
    sizey = None
    stamp = None

    def __init__(self, inputlayer, seed = 0, ore = MAT_DIAMONDORE, x = 0, z = 0, y = 0, sizex = 2, sizez = 2, sizey = 2, density = 0.33):
        
        Landmark.__init__(self, inputlayer, seed, x, z, y)
        self.ore = ore
        self.sizex = sizex
        self.sizez = sizez
        self.sizey = sizey
        self.viewrange = max(sizex, sizez) / 2
        self.stamp = None
        self.density = density

    def editChunk(self, cornerblockx, cornerblockz, terrainchunk):
        """
        Edit the input chunk and add ores.
        """
        if self.stamp == None:
            self.stamp = [[[MAT_TRANSPARENT for vert in xrange(self.sizey)] for col in xrange(self.sizez)] for row in xrange(self.sizex)]
            # Add shit to the stamp here!
            random.seed( self.seed ^ (( (self.x << 16) & 0xFFFF0000) | ( self.z & 0x0000FFFF)) )
            random.jumpahead( self.y )
            for row in self.stamp:
                for col in row:
                    for ix in xrange(len(col)) :
                        if random.random() < self.density:
                            col[ix] = self.ore
        offsetx = self.x - cornerblockx
        offsetz = self.z - cornerblockz
        offsety = self.y
        self.stampToChunk( self.stamp, terrainchunk.blocks, offsetx, offsetz, offsety )

    def __copy__(self):
        newcopy = CubicOreLandmark(self.inputlayer, self.seed, self.ore, self.x, self.z, self.y, self.sizex, self.sizez, self.sizey, self.density)
        newcopy.stamp = copy.deepcopy(self.stamp)
        return newcopy
        



