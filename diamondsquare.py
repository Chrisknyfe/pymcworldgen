#!/usr/bin/env python

"""
Diamond-square algorithm for creating fractal cloud maps in 2D and 3D.

"""

import random
import math

"""
diamondsquare1D

- arr is a one dimensional array.
- seed is anything!
- volatility is a numer that should range from 1.0 to 0.5. This is the fraction we multiply by the
    random value so that each time we reduce the size of the random displacement. 1.0 will not reduce
    the random displacement at all. 0.5 will reduce it by half each iteration.
- initdepth is the initial depth into the recursion that we begin at. We can cut down on noise using this.
"""

def diamondsquare1D( arr, seed = None, volatility = 0.5, initdepth = 0):

    """
    recurse:

    each ix is an integer for accessing the elements of the array.

    Left is towards the beginning of the array, right is towards the end of the array. ( I really should have called these startx and endx or something )
    """
    def recurse( left, right, depth):
        # Check to make sure that we need to recurse because there may be unfilled values.
        if ( abs(left - right) < 2 ):
            #print "Size-rejected area", (left,right)
            return
        # do a midpoint recursion on the data.
        #print "recursing between", left, "and", right

        # Get the center coordinates (used in both steps)        
        centerix = int(math.floor( (left + right) / 2))
        volatilityscale = pow(volatility, depth);
        randadd = (random.random() - 0.5) * volatilityscale

        # Midpoint step: well, midpoint (durr)
        if ( arr[centerix] < 0.0 ):
            avg = (arr[left] + arr[right]) / 2.0
            arr[centerix] = min( max(avg + randadd, 0.0), 1.0)
            #print "filling midpoint", (centerix), "with", arr[centerix], "given", arr[left], "and", arr[right]    

        # Recursive step: left
        recurse( left, centerix, depth + 1 )
        # Recursive step: right
        recurse( centerix, right, depth + 1 )

    # truly random values for the corners
    random.seed(seed)
    # Initialize the corners with random values if they're empty.
    if( arr[len(arr)-1] < 0.0 ): arr[len(arr)-1] = random.random()
    if( arr[0] < 0.0 ):          arr[0] = random.random()

    # Seed the random number generator:
    cornerseed = arr[len(arr)-1]*37*37 + arr[0]*37*37*37
    if (seed == None):
        # When no seed is provided, seed the randomness using the corner values. In this way, if you have two 2D diamond-square spaces
        # you want to generate side-by-side, and want them to seam correctly, generate their shared edge and 
        # just leave seed == None for both edges.
        random.seed(cornerseed)
    else:
        random.seed(seed + cornerseed);
    
    # Initiate the recursion
    recurse( 0, len(arr)-1, initdepth )


"""
diamondsquare2D

- arr should be a 2D row-major, row index array, increasing going south, col index increasing going west. 
    (direction doesn't really matter since we're only using averages.)
    We're going to mutate the fuck out of this array. Any value that is negative will be rewritten
    with a value between 0 and 1. Any value you initialize will affect the surrounding geometry.
- seed is anything!
- volatility is a numer that should range from 1.0 to 0.5. This is the fraction we multiply by the
    random value so that each time we reduce the size of the random displacement. 1.0 will not reduce
    the random displacement at all. 0.5 will reduce it by half each iteration.
"""

def diamondsquare2D( arr, seed = None, volatility = 0.5, initdepth = 0):
        
    """
    recurse:
 
    """
    def recurse( top, bottom, right, left, depth):
        #print arr
        # Check to make sure that we need to recurse because there may be unfilled values.
        if ( abs(bottom - top) < 2 and abs(left - right) < 2 ):
            #print "Size-rejected area", (top,right), "to", (bottom, left)
            return
        #print "recursing on area", (top,right), "to", (bottom, left)
        
        # do a diamond-square recursion on the data. Square step doesn't average all four corners
        # of the diamond, just uses the midpoint of the corners. I wonder what this will affect.

        # Get the center coordinates (used in both steps)        
        centerix = ( int(math.floor( (top + bottom) / 2)), int(math.floor( (right + left) / 2)) )
        volatilityscale = pow(volatility, depth);
        toprandadd = (random.random() - 0.5) * volatilityscale
        bottomrandadd = (random.random() - 0.5) * volatilityscale
        rightrandadd = (random.random() - 0.5) * volatilityscale
        leftrandadd = (random.random() - 0.5) * volatilityscale
        centerrandadd = (random.random() - 0.5) * volatilityscale

        # Square Step: top
        if ( arr[top][centerix[1]] < 0.0 ):
            topavg = (arr[top][left] + arr[top][right]) / 2.0
            arr[top][centerix[1]] = min( max( topavg + toprandadd, 0 ), 1 )
            #print "filling top", (top, centerix[1]), "with", arr[top][centerix[1]], "given", arr[top][left], "and", arr[top][right]         

        # Square Step: bottom
        if ( arr[bottom][centerix[1]] < 0.0 ):
            bottomavg = (arr[bottom][left] + arr[bottom][right]) / 2.0
            arr[bottom][centerix[1]] = min( max( bottomavg + bottomrandadd, 0 ), 1 )
            #print "filling bottom", (bottom, centerix[1]), "with", arr[bottom][centerix[1]], "given", arr[bottom][left], "and", arr[bottom][right]    

        # Square Step: right
        if ( arr[centerix[0]][right] < 0.0 ):
            rightavg = (arr[top][right] + arr[bottom][right]) / 2.0
            arr[centerix[0]][right] = min( max( rightavg + rightrandadd, 0 ), 1 )
            #print "filling right", (centerix[0], right), "with", arr[centerix[0]][right], "given", arr[top][right], "and",arr[bottom][right]

        # Square Step: left
        if ( arr[centerix[0]][left] < 0.0 ):
            leftavg = (arr[top][left] + arr[bottom][left]) / 2.0
            arr[centerix[0]][left] = min( max( leftavg + leftrandadd, 0 ), 1 )
            #print "filling left", (centerix[0], left), "with", arr[centerix[0]][left], "given", arr[top][left], "and",arr[bottom][left]

        # Diamond step: center point (comes after     
        if ( arr[centerix[0]][centerix[1]] < 0.0 ):
            centeravg = ( arr[top][left] + arr[top][right] + arr[bottom][left] + arr[bottom][right] ) / 4.0
            arr[centerix[0]][centerix[1]] = min( max( centeravg + centerrandadd, 0 ), 1 )
            
            #print "filling center", (centerix[0], centerix[1]), "with", arr[centerix[0]][centerix[1]], "given", arr[top][left], \
            #      arr[top][right], arr[bottom][left], "and", arr[bottom][right]            

        # Recursive step: top right
        recurse( top, centerix[0], right, centerix[1], depth + 1 )
            
        # Recursive step: top left
        recurse( top, centerix[0], centerix[1], left, depth + 1 )
        
        # Recursive step: bottom right
        recurse( centerix[0], bottom, right, centerix[1], depth + 1 )
            
        # Recursive step: bottom left
        recurse( centerix[0], bottom, centerix[1], left, depth + 1 )

    #print arr
    random.seed(seed)
    # Initialize the corners with random values if they're empty.
    if( arr[len(arr)-1][len(arr[0])-1] < 0.0 ): arr[len(arr)-1][len(arr[0])-1] = random.random()
    if( arr[0][len(arr[0])-1] < 0.0 ): arr[0][len(arr[0])-1] = random.random()
    if( arr[len(arr)-1][0] < 0.0 ): arr[len(arr)-1][0] = random.random()
    if( arr[0][0] < 0.0 ): arr[0][0] = random.random()

    cornerseed = (arr[len(arr)-1][len(arr[0])-1]) + (arr[0][len(arr[0])-1])*37 + (arr[len(arr)-1][0])*37*37 + (arr[0][0])*37*37*37
    #print "Corner values are:", arr[bottom][left], arr[top][left], arr[bottom][right], arr[top][right]
    if (seed == None):
        # When no seed is provided, seed the randomness using the corner values. In this way, if you have two 3D diamond-square spaces
        # you want to generate side-by-side, and want them to seam correctly, generate the shared surface and
        # just leave seed == None for both surfaces.
        random.seed( cornerseed )
        #print "seed for this recursion is", cornerseed
    else:
        random.seed( seed + cornerseed );
        #print "seed for this recursion is", seed + cornerseed
    
    # Initiate the recursion
    recurse( 0 ,len(arr)-1, 0, len(arr[0])-1, initdepth )
        
            


        
    
