#!/usr/bin/env python

"""

pyMCWorldGen Constants and assumptions

"""

CHUNK_WIDTH_IN_BLOCKS = 16
CHUNK_HEIGHT_IN_BLOCKS = 128
REGION_WIDTH_IN_CHUNKS = 32

# Block ID constants
try:
    from pymclevel import materials
    MAT_AIR = materials.materials.Air.ID
    MAT_STONE = materials.materials.Stone.ID
    MAT_DIRT = materials.materials.Dirt.ID
    MAT_WOOD = materials.materials.Wood.ID
    MAT_WATER = materials.materials.WaterActive.ID
    MAT_SNOW = materials.materials.Snow.ID
    MAT_BEDROCK = materials.materials.Bedrock.ID
    MAT_LEAVES = materials.materials.Leaves.ID
    MAT_GRASS = materials.materials.Grass.ID
    MAT_DIAMONDORE = materials.materials.DiamondOre.ID
    MAT_REDSTONEORE = materials.materials.RedstoneOre.ID
    MAT_LAPISORE = materials.materials.LapisLazuliOre.ID
    MAT_GOLDORE = materials.materials.GoldOre.ID
    MAT_IRONORE = materials.materials.IronOre.ID
    MAT_COALORE = materials.materials.CoalOre.ID
except ImportError:
    MAT_AIR = 0
    MAT_STONE = 1
    MAT_DIRT = 3
    MAT_WOOD = 17
    MAT_WATER = 8
    MAT_SNOW = 78
    MAT_BEDROCK = 7
    MAT_LEAVES = 18
    MAT_GRASS = 2
    MAT_DIAMONDORE = 56
    MAT_REDSTONEORE = 73
    MAT_LAPISORE = 21
    MAT_GOLDORE = 14
    MAT_IRONORE = 15
    MAT_COALORE = 16
MAT_TRANSPARENT = -1

# LayerMask height constants
MASK_HEIGHT_MAX = 1.0
MASK_HEIGHT_MIN = 0.0
MASK_HEIGHT_TRANSPARENT = -1.0
