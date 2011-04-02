#!/usr/bin/env python

"""

Unit testing for diamondsquare module

"""

import unittest

# Dependencies
import os
import random
import numpy
from saveutils import saveedgeimage, savechunkimage

# Modules to test
from diamondsquare import *

def isvalidheight( num ):
    return type(num) == float and num <= 1.0 and num >= 0.0

class DiamondSquare2dTestCase(unittest.TestCase):
    """
    DiamondSquare2d is a plasma noise algorithm that should satisfy the following conditions:
    - it should work on an array of size (2**n) + 1 (extremely even and nicely halved by the algorithm; a base case!)
    - arrays that are odd sized but not of the formula (2**n) + 1, so that there are cases where we have to skip certain areas early.
    - arrays that are even sized
    - arrays that are not square
    - arrays where the corners have been initialized
    - without a random seed
    - with a random seed seed
    - of small volatility (<0.5)
    - of a non-default initial depth
    It should also fail on the following cases:
    - bad array input (None, not 2D, not of float type, not rectangular)
    - bad random seed (what IS a bad random seed? A list?)
    - bad volatility (None, a list, or something else)
    - bad init depth (None, a list, or something else)

    Hopy shit this is a lot of tests. But it's worth it.
    """
    def setUp(self):
        # Save directory for visual checks
        if not os.path.isdir("renders"):
            os.mkdir("renders")

    def test_elegant_array(self):
        size = ( 2**(4) ) + 1
        m = [[-1 for col in xrange(size)] for row in xrange(size)]
        diamondsquare2D( m )
        # test that all values were filled
        for row in m:
            for col in row:
                self.assertTrue( isvalidheight( col ), "Not a valid height value or was not filled:" + str(col) )

        # Save so we can visually check
        savechunkimage(m, "visualcheck_DiamondSquare2dTestCase_test_elegant_array")

    def test_empty_odd_seeded(self):
        random.seed()
        m = [[-1 for col in xrange(5)] for row in xrange(5)]
        diamondsquare2D( m, seed = random.random())
        # test that all values were filled
        for row in m:
            for col in row:
                self.assertTrue( isvalidheight( col ), "Not a valid height value or was not filled:" + str(col) )

    def test_cornered_even_volatility(self):
        m = [[-1 for col in xrange(4)] for row in xrange(4)]; m[0][0] = 0.5; m[3][0] = 0.5; m[0][3] = 0.5; m[3][3] = 0.5
        diamondsquare2D( m, volatility = 0.2 )
        # test that all values were filled
        for row in m:
            for col in row:
                self.assertTrue( isvalidheight( col ), "Not a valid height value or was not filled:" + str(col) )

    def test_rectangular_initdepth(self):
        m = [[-1 for col in xrange(4)] for row in xrange(7)]; m[0][0] = 0.5; m[6][0] = 0.6; m[0][3] = 0.7; m[6][3] = 0.8
        diamondsquare2D( m, initdepth = 1 )
        # test that all values were filled
        for row in m:
            for col in row:
                self.assertTrue( isvalidheight( col ), "Not a valid height value or was not filled:" + str(col) )

    def test_elegant_init_depth(self):
        size = ( 2**(4) ) + 1
        m = [[-1 for col in xrange(size)] for row in xrange(size)]
        random.seed()
        diamondsquare2D( m, initdepth = random.randint(1,65535) )
        # test that all values were filled
        for row in m:
            for col in row:
                self.assertTrue( isvalidheight( col ), "Not a valid height value or was not filled:" + str(col) )

    def test_bad_inputs(self):
        size = ( 2**(3) ) + 1
        m = [[-1 for col in xrange(size)] for row in xrange(size)]

        # bad types of input
        try:
            diamondsquare2D( m, seed = [] )
        except Exception as e:
            pass
        else:
            self.fail("diamondsquare2D should fail on bad seed input ")

        try:
            diamondsquare2D( m, volatility = None )
        except Exception as e:
            pass
        else:
            self.fail("diamondsquare2D should fail on bad volatility input ")

        try:
            diamondsquare2D( m, initdepth = None )
        except Exception as e:
            pass
        else:
            self.fail("diamondsquare2D should fail on bad initdepth input ")

        # input is out of valid range
        try:
            diamondsquare2D( m, volatility = -0.4 )
        except Exception as e:
            pass
        else:
            self.fail("diamondsquare2D should fail on bad volatility input ")
            
        try:
            diamondsquare2D( m, volatility = 1.1 )
        except Exception as e:
            pass
        else:
            self.fail("diamondsquare2D should fail on bad volatility input ")

        try:
            diamondsquare2D( m, initdepth = -1 )
        except Exception as e:
            pass
        else:
            self.fail("diamondsquare2D should fail on bad initdepth input ")

class DiamondSquare1dTestCase(unittest.TestCase):
    """
    DiamondSquare1d is a plasma noise algorithm that should satisfy the following conditions:
    - it should work on an array of size (2**n) + 1 (extremely even and nicely halved by the algorithm; a base case!)
    - arrays that are odd sized but not of the formula (2**n) + 1, so that there are cases where we have to skip certain areas early.
    - arrays that are even sized
    - arrays where the corners have been initialized
    - without a random seed
    - with a random seed seed
    - of small volatility (<0.5)
    - of a non-default initial depth
    It should also fail on the following cases:
    - bad array input (None, not 2D, not of float type, not rectangular)
    - bad random seed (what IS a bad random seed? A list?)
    - bad volatility (None, a list, or something else)
    - bad init depth (None, a list, or something else)

    Hopy shit this is a lot of tests. Just like the 2d tests.
    """
    def setUp(self):
        # Save directory for visual checks
        if not os.path.isdir("renders"):
            os.mkdir("renders")

    def test_elegant_array(self):
        size = ( 2**(4) ) + 1
        m = [-1 for col in xrange(size)]
        diamondsquare1D( m )
        # test that all values were filled
        for row in m:
            self.assertTrue( isvalidheight( row ), "Not a valid height value or was not filled:" + str(row) )

        # Save so we can visually check
        saveedgeimage(m, "visualcheck_DiamondSquare1dTestCase_test_elegant_array")

    def test_empty_odd_seeded(self):
        random.seed()
        m = [-1 for col in xrange(5)]
        diamondsquare1D( m, seed = random.random())
        # test that all values were filled
        for row in m:
            self.assertTrue( isvalidheight( row ), "Not a valid height value or was not filled:" + str(row) )

    def test_cornered_even_volatility(self):
        m = [-1 for col in xrange(4)]; m[0] = 0.5; m[3] = 0.5
        diamondsquare1D( m, volatility = 0.2 )
        # test that all values were filled
        for row in m:
            self.assertTrue( isvalidheight( row ), "Not a valid height value or was not filled:" + str(row) )

    def test_rectangular_initdepth(self):
        m = [-1 for row in xrange(7)]; m[0] = 0.5; m[6] = 0.6;
        diamondsquare1D( m, initdepth = 1 )
        # test that all values were filled
        for row in m:
            self.assertTrue( isvalidheight( row ), "Not a valid height value or was not filled:" + str(row) )

    def test_elegant_init_depth(self):
        size = ( 2**(4) ) + 1
        m = [-1 for row in xrange(size)]
        random.seed()
        diamondsquare1D( m, initdepth = random.randint(1,65535) )
        # test that all values were filled
        for row in m:
            self.assertTrue( isvalidheight( row ), "Not a valid height value or was not filled:" + str(row) )

    def test_bad_inputs(self):
        size = ( 2**(3) ) + 1
        m = [-1 for row in xrange(size)]

        # bad types of input
        try:
            diamondsquare1D( m, seed = [] )
        except Exception as e:
            pass
        else:
            self.fail("diamondsquare1D should fail on bad seed input ")

        try:
            diamondsquare1D( m, volatility = None )
        except Exception as e:
            pass
        else:
            self.fail("diamondsquare1D should fail on bad volatility input ")

        try:
            diamondsquare1D( m, initdepth = None )
        except Exception as e:
            pass
        else:
            self.fail("diamondsquare1D should fail on bad initdepth input ")

        # input is out of valid range
        try:
            diamondsquare1D( m, volatility = -0.4 )
        except Exception as e:
            pass
        else:
            self.fail("diamondsquare1D should fail on bad volatility input ")
            
        try:
            diamondsquare1D( m, volatility = 1.1 )
        except Exception as e:
            pass
        else:
            self.fail("diamondsquare1D should fail on bad volatility input ")

        try:
            diamondsquare1D( m, initdepth = -1 )
        except Exception as e:
            pass
        else:
            self.fail("diamondsquare1D should fail on bad initdepth input ")

if __name__ == '__main__':
    unittest.main()

