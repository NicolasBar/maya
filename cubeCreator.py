__author__ = 'Nicolas'

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
totalObjs = 40
randThresh = 5

for i in range(0, totalObjs, 1):
    newObjName = baseName + str(i).zfill(2)
    cmds.polyCube(n= newObjName)
    cmds.move(xIter, yIter, zIter)

    while True :
        if xIter <= Width:
            xIter += 1
        else:
            xIter = .5
            if zIter <= Depth:
                zIter += 1
            else:
                yIter = .5
                if yIter <= Height:
                    yIter += 1
        if random.randint(0,10) < randThresh:
            break








