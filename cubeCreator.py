__author__ = 'Nicolas'

"""
This Script Creates a Cluster of Objects.
They are randomly stacked into columns of different heights and grouped together.
"""

import maya.cmds as cmds
import random

xIter = 0.5
yIter = 0.5
zIter = 0.5
baseName = "cubeCluster_"
gravity = True

"""pileDimensions"""
Width = 10 + xIter
Height = 10 + xIter
Depth = 10 + xIter
totalObjs = 500
actualObjs = 0
randThresh = 8

groupName = cmds.group(em=1, n="Cluster_01")

for i in range(0, totalObjs, 1):
    newObjName = baseName + str(i).zfill(2)
    cmds.polyCube(n= newObjName)
    cmds.parent("|" + newObjName, groupName)
    cmds.move(xIter, yIter, zIter, (groupName + "|" + newObjName))

    #start building cubes in columns until random triggers to move on
    if (yIter < Height) & (random.randint(0, 10) < randThresh):
        yIter += 1
    else:
        yIter = .5
        if xIter < Width:
            xIter += 1
        else:
            xIter = .5
            if zIter < Depth:
                zIter += 1
    if zIter == Depth:
        actualObjs = i
        print("Only had enough space to create " + str(actualObjs) +
              " objects. For more: Increase Dimensions, or Lower Rand Threshold.")
        break








