#!/usr/bin/env python

"""

Utilities for saving chunk data in various forms (minecraft level or scipy graph)

"""

# Dependencies
import time
import os
import subprocess
import numpy
import pymclevel as mcl
from scipy import *
from pylab import *

from layer import Chunk

__all__ = ["rm_rf", "saveedgeimage", "savechunkimage", "createWorld", "saveWorld", "renderWorld", "getWorldChunk", "setWorldChunk"]


# Convenient rm -rf python function
# http://code.activestate.com/recipes/552732-remove-directories-recursively/
def rm_rf(d):
    for path in (os.path.join(d,f) for f in os.listdir(d)):
        if os.path.isdir(path):
            rm_rf(path)
        else:
            os.unlink(path)
    os.rmdir(d)

def saveedgeimage( edge, name='randomedge' ):
    figure()
    plot(range(len(edge)), edge)
    xlabel('position along string')
    ylabel('height')
    title(name)
    grid(True)
    savefig(os.path.join("renders", name) )

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
def setWorldChunk(world, inchunk, cx, cz):
    global chunksBeforeNextSave

    assert( issubclass(inchunk.__class__, Chunk) )
    arr = inchunk.blocks
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


