#!/usr/bin/env python

"""

Run all unit tests for pyMCWorldGen

"""

import os


print os.getcwd()

execfile( os.path.join( os.getcwd(), "test/unittests_old.py") )
execfile( os.path.join( os.getcwd(), "test/test_diamondsquare.py") )

