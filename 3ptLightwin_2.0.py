'''
Created on Oct 14, 2013

@author: Nicolas Kendall-Bar
'''

import maya.cmds as cmds
import math
import cPickle
import os

kLightFileExtension = 'lgt'


class KB_3PtLightWin(object):
    """A class for a window that helps create a default 3 point lighting setup"""
    ## reference to the most recent instance
    use = None
    lights = []
    currentLight = "keyLightShape"

    @classmethod
    def showUI(cls, uiFile):
        """A function to instantiate the window"""
        win = cls(uiFile)
        win.create()
        return win

    def __init__(self, filePath):
        """Initialize data attributes"""
        ## allow controls to initialize using class attribute
        KB_3PtLightWin.use = self
        ## unique window handle
        self.window = 'kb_3ptLightwin'
        ## name of rotation input field
        self.intensitySlider = 'intensitySlider'
        ## the path to the .ui file
        self.uiFile = filePath

    def create(self, verbose=False):
        """Draw the window"""
        # delete the window if its handle exists
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window)
            # initialize the window
        self.window = cmds.loadUI(
            uiFile=self.uiFile,
            verbose=verbose
        )
        cmds.showWindow(self.window)

    def createBtnCmd(self, *args):
        """Function to execute when Create button is pressed"""

        # create 3 lights and place them in the right location
        self.lights.append(cmds.spotLight(n='keyLight'))
        cmds.setAttr('keyLight.translate', -2, 3, 10, type="double3")
        self.lights.append(cmds.spotLight(n='fillLight'))
        cmds.setAttr('fillLight.translate', 6, 0, 2, type="double3")
        self.lights.append(cmds.spotLight(n='backLight'))
        cmds.setAttr('backLight.translate', -1, 8, -10, type="double3")
        self.findLightAngle('keyLight')
        self.findLightAngle('fillLight')
        self.findLightAngle('backLight')

        #flip backlight back towards the origin
        cmds.select('backLight')
        cmds.rotate(180, y=1, r=1, os=1)

        cmds.group('keyLight', 'fillLight', 'backLight', n='Three_Point_Lights')

    def softBtnCmd(self, *args):
        """Function that softens shadows to a default starting point"""
        for l in self.lights:
            cmds.setAttr('%s.penumbraAngle' % l, 4)
            cmds.setAttr('%s.shadowRays' % l, 4)
            cmds.setAttr('%s.lightRadius' % l, .25)

    def shadowsBtnCmd(self, *args):
        """Function turns on ray trace shadows for lights"""
        for l in self.lights:
            cmds.spotLight(l, e=1, rs=1);

    def setIntensityCmd(self, *args):
        """Function called when Global intensity slider is changed, and updates intensity"""
        intensity = None
        # obtain input as a float
        try:
            ctrlPath = '|'.join(
                [self.window, 'centralwidget', self.intensitySlider]
            )
            intensity = .02 * float(
                cmds.intSlider(ctrlPath, q=True, value=True)
            )
        except:
            raise
        for l in self.lights:
            if (l == 'fillLightShape'):
                adjIntensity = intensity * .6
            elif (l == 'keyLightShape'):
                adjIntensity = intensity
            else:
                adjIntensity = intensity * .9
            cmds.spotLight(l, e=1, i=adjIntensity)

    def findLightAngle(self, light):
        """Function to find angles to point light to origin"""
        pivot = cmds.xform('%s' % light, q=1, ws=1, rp=1)
        rotX = -math.degrees(math.atan(pivot[1] / pivot[2]))
        rotY = math.degrees(math.atan(pivot[0] / pivot[2]))
        cmds.setAttr('%s.rotate' % light, rotX, rotY, 0, type="double3")

    def getSelection(self):
        """Function to grab and validate current selected node as light root"""
        rootNodes = cmds.ls(sl=True, type='transform')
        if rootNodes is None or len(rootNodes) < 1:
            cmds.confirmDialog(t='Error', b=['OK'],
                               m='Please select the root of the light setup.')
            return None
        else:
            return rootNodes

    def saveBtnCmd(self, *args):
        """Called when the Save Light Setup button is pressed, saves data to file"""
        print("Save Menu Btn has been clicked")
        cmds.select("Three_Point_Lights")
        rootNodes = self.getSelection()
        if rootNodes is None:
            try:
                rootNodes = self.getSelection()
            except:
                return
         #defaults to home directory for the moment
        filePath = ''
        # Maya 2011 and newer use fileDialog2
        try:
            filePath = cmds.fileDialog2(
                ff=self.fileFilter, fileMode=0
            )
        # BUG: Maya 2008 and older may, on some versions of OS X, return the
        # path with no separator between the directory and file names:
        # e.g., /users/adam/Desktopuntitled.pse
        except:
            filePath = cmds.fileDialog(
                dm='*.%s' % kLightFileExtension, mode=1
            )
            # early out of the dialog was canceled
        if filePath is None or len(filePath) < 1: return
        if isinstance(filePath, list): filePath = filePath[0]
        exportSetup(filePath, cmds.ls(sl=True, type='transform'))

    def loadBtnCmd(self, *args):
        """Called when the Load Light Setup button is pressed, loads light data from file"""
        filePath = ''
        # Maya 2011 and newer use fileDialog2
        try:
            filePath = cmds.fileDialog2(
                ff=self.fileFilter, fileMode=1
            )
        except:
            filePath = cmds.fileDialog(
                dm='*.%s' % kLightFileExtension, mode=0
            )
            # early out of the dialog was canceled
        if filePath is None or len(filePath) < 1: return
        if isinstance(filePath, list): filePath = filePath[0]
        importSetup(filePath)

    def helpBtnCmd(self, *args):
        """for now this Function launches blogpost on website"""
        print("DEBUG: help pressed")
        cmds.launch(web='http://nicolaskendallbar.wordpress.com/2014/01/15/quick-3-point-lighting-python-tool/')

    def adjustLights(self, *args):
        """Function that looks through the next light for Camera adjustment"""
        #Look through a light for easy adjustment
        print("adjustLights called\n")
        for l in self.lights:
            if l == self.currentLight:
                lxform = cmds.listRelatives(l, p=1)
                print("DEBUG: looking thru: " + lxform[0])
                cmds.lookThru("modelPanel4", lxform[0],  nc=.001, fc=1000)
        if self.currentLight == "keyLightShape":
            self.currentLight = "fillLightShape"
        elif self.currentLight == "fillLightShape":
            self.currentLight = "backLightShape"
        else:
            self.currentLight = "keyLightShape"


#The following functions deal with exporting and importing saved Light Setups


def exportSetup(filepath, rootNodes):
    '''Open file and call save func'''
    try:
        f = open(filepath, 'w')
    except:
        cmds.confirmDialog(t='Error', b=['OK'], m='Unable to write file: %s' % filepath)
        raise;
    data = saveSetup(rootNodes, [])
    cPickle.dump(data, f)
    f.close


def saveSetup(rootNodes, data):
    for node in rootNodes:
        nodeType = cmds.nodeType(node)
        keyableAttrs = cmds.listAttr(node, keyable=True)
        if keyableAttrs is not None:
            for attr in keyableAttrs:
                data.append(['%s.%s' % (node, attr), cmds.getAttr('%s.%s' % (node, attr))])
        children = cmds.listRelatives(node, children=True)
        if children is not None: saveSetup(children, data)
    return data


def importSetup(filePath):
    """Import the Light setup data stored in filePath"""
    # try to open the file
    try:
        f = open(filePath, 'r')
    except:
        cmds.confirmDialog(
            t='Error', b=['OK'],
            m='Unable to open file: %s' % filePath
        )
        raise
        # uncPickle the data
    lightAttrs = cPickle.load(f)
    # close the file
    f.close()
    # set the attributes to the stored pose
    errAttrs = []
    for attrValue in lightAttrs:
        try:
            cmds.setAttr(attrValue[0], attrValue[1])
        except:
            try:
                errAttrs.append(attrValue[0])
            except:
                errAttrs.append(attrValue)
                # display error message if needed
    if len(errAttrs) > 0:
        importErrorWindow(errAttrs)
        sys.stderr.write('Not all attributes could be loaded.')

#create window when script is run
win = KB_3PtLightWin(
    os.path.join(os.getenv('HOME'), '3ptLight.ui'))
win.create(verbose=True)
