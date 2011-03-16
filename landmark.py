#!/usr/bin/env python

"""

Landmark generation - interspersed landmarks on the terrain

"""

import random
import math
import numpy
from layer import *
from constants import *


treesskipped = [0]

class Landmark(Layer):
    """
    A chunk generator for a single landmark somewhere in the world.
    """
    seed = None
    terrainlayer = None
    x = None
    z = None
    y = None
    layermask = None
    
    # Viewrange is a class property only. This is the maximum number of blocks from
    # the centerpoint that this Landmark will generate blocks.
    viewrange = 0    
    drawcancelled = False

    def __init__(self, seed, terrainlayer, x = 0, z = 0, y = 0, layermask = None):
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
        self.y = y
        self.layermask = layermask
        self.drawcancelled = False

    def setpos(self, x, z, y):
        """
        Set the position of this landmark. 
        """
        self.x = x
        self.z = z
        self.y = y

    def setTerrainLayer(self, terrainlayer):
        self.terrainlayer = terrainlayer

    def isLandmarkInChunk(self, cx, cz):
        """
        Determine whether the given chunk contains a portion of this landmark.
        """
        bxrange = (cx*16 - self.viewrange, (cx+1)*CHUNK_WIDTH_IN_BLOCKS + self.viewrange)
        bzrange = (cz*16 - self.viewrange, (cz+1)*CHUNK_WIDTH_IN_BLOCKS + self.viewrange)

        if ( bxrange[0] <= self.x < bxrange[1] ) and ( bzrange[0] <= self.z < bzrange[1] ):
            return True
        else:
            return False

    def editChunk(self, cornerblockx, cornerblockz, terrainchunk):
        """
        Edit the input chunk. Override this function to create beautiful procedural
        Landmarks. 
        """
        # Dummy: output a wood column
        # where in the array does this block belong?
        relx = self.x - cornerblockx
        relz = self.z - cornerblockz
        # only place this down if we're not going to overflow the array
        if ( 0 <= relx < CHUNK_WIDTH_IN_BLOCKS ) and ( 0 <= relz < CHUNK_WIDTH_IN_BLOCKS ):
            terrainchunk[relx, relz, 0:CHUNK_HEIGHT_IN_BLOCKS] = MAT_WOOD
            terrainchunk[relx, relz, self.y] = MAT_WATER
        
    def getChunk(self, cx, cz):
        """
        Output a chunk for processing. Do not override! use editChunk instead
        """
            
        # If we aren't in this chunk, either act as a passthru or return an opaque chunk.
        if self.drawcancelled or (not self.isLandmarkInChunk(cx, cz)):
            return self.terrainlayer.getChunk(cx, cz)
        # If we are in the chunk, let's write our blocks to the output chunk
        terrainchunk = self.terrainlayer.getChunk(cx, cz)
        outputchunk = terrainchunk
        self.editChunk(cx*CHUNK_WIDTH_IN_BLOCKS, cz*CHUNK_WIDTH_IN_BLOCKS, terrainchunk)
        return outputchunk


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
        global treesskipped

        # Find our actual Y: place us on the ground. TODO: MAKE THIS A FUNCTION
        # but before that, we need the correct chunk.
        originchunk = terrainchunk
        if not ( 0 <= (self.x - cornerblockx) < CHUNK_WIDTH_IN_BLOCKS and 0 <= (self.z - cornerblockz) < CHUNK_WIDTH_IN_BLOCKS ):
            originchunkx = self.x / CHUNK_WIDTH_IN_BLOCKS
            originchunkz = self.z / CHUNK_WIDTH_IN_BLOCKS
            originchunk = self.terrainlayer.getChunk(originchunkx, originchunkz)
        # now that we have the correct origin chunk, let's search for the tree's ground height.
        downrange = range( 0, 127 )
        downrange.reverse()
        actualy = -1
        actualyid = -1
        for y in downrange:
            #print "checking x,z,y:", self.x - cornerblockx, self.z - cornerblockz, y
            actualyid = originchunk[self.x % CHUNK_WIDTH_IN_BLOCKS][self.z % CHUNK_WIDTH_IN_BLOCKS][y]
            if actualyid != MAT_AIR:
                actualy = y + 1
                break

        if actualy == -1: 
            self.drawcancelled = True
            treesskipped[0] += 1
            return 
        if actualyid != MAT_DIRT and actualyid != MAT_GRASS:
            self.drawcancelled = True
            treesskipped[0] += 1
            return
        
        # Write the static array into the map. # TODO: MAKE THIS A FUNCTION
        # offsets of lower north-east corner of the array relative to corner block.
        offsetx = self.x - cornerblockx - self.viewrange
        offsetz = self.z - cornerblockz - self.viewrange
        offsety = actualy 
        inputarray = self.statictree

        # iterate between the overlapping range, in output-space.
        for outx in xrange( max(0, offsetx), min(CHUNK_WIDTH_IN_BLOCKS, offsetx + len(inputarray) ) ):
            # get the current coordinate in input-space.
            inx = outx - offsetx
            for outz in xrange( max(0, offsetz), min(CHUNK_WIDTH_IN_BLOCKS, offsetz + len(inputarray[inx]) ) ):
                inz = outz - offsetz
                for outy in xrange( max(0, offsety), min(CHUNK_HEIGHT_IN_BLOCKS, offsety + len(inputarray[inx][inz]) ) ):
                    iny = outy - offsety
                    if (inputarray[inx][inz][iny] != MAT_TRANSPARENT):
                        terrainchunk[outx][outz][outy] = self.statictree[inx][inz][iny]

class LandmarkGenerator(Layer):
    """
    A chunk generator for a random smattering of landmarks throughout the worldde
    """
    seed = None
    terrainlayer = None
    landmarklist = None
    density = None

    # { dict where key is (rx, rz) and value is {dict where key is (cx, cz) and value is [list of Landmarks ] } }
    worldspawns = None 

    def __init__(self, seed, terrainlayer, landmarklist = [Landmark], density = 200):
        self.seed = seed        
        self.terrainlayer = terrainlayer
        self.density = density
        # Input landmark list needs to be doublechecked.
        for lmtype in landmarklist:
            if not issubclass(lmtype, Landmark): raise TypeError, "landmarklist must only contain Landmark types."
        self.landmarklist = landmarklist
        # This data structure has a lot of indexing structure so we can find relevant points quickly
        self.worldspawns = {} 

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

            self.worldspawns[ (rx,rz) ] = {}
            currentregion = self.worldspawns[ (rx,rz) ]
            for ix in xrange(numspawns):
                blockx = random.randint( 0, CHUNK_WIDTH_IN_BLOCKS * REGION_WIDTH_IN_CHUNKS - 1 ) + rx * CHUNK_WIDTH_IN_BLOCKS * REGION_WIDTH_IN_CHUNKS
                blockz = random.randint( 0, CHUNK_WIDTH_IN_BLOCKS * REGION_WIDTH_IN_CHUNKS - 1 ) + rz * CHUNK_WIDTH_IN_BLOCKS * REGION_WIDTH_IN_CHUNKS
                blocky = random.randint( 0, CHUNK_HEIGHT_IN_BLOCKS - 1 ) 
                currchunkx = blockx / CHUNK_WIDTH_IN_BLOCKS
                currchunkz = blockz / CHUNK_WIDTH_IN_BLOCKS
                # We store the points for each chunk indexed by chunk
                if not (currchunkx, currchunkz) in currentregion:
                    currentregion[ (currchunkx, currchunkz) ] = []
                # We make a landmark for each point
                lmtypeix = random.randint(0, len(self.landmarklist) - 1)
                lmtype = self.landmarklist[lmtypeix] 
                lm = lmtype(self.seed, self.terrainlayer, blockx, blockz, blocky)
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
        graph = self.terrainlayer
        landmarks = self.getSpawnsTouchingChunk(cx,cz)
        if landmarks == None:
            return self.terrainlayer.getChunk( cx, cz )
        for mark in landmarks:
            # insert this landmark at the end of the graph    
            mark.setTerrainLayer( graph )
            graph = mark
        
        return graph.getChunk( cx, cz )
        
