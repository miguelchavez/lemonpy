 #***************************************************************************
 #*   Copyright (C) 2011 by Miguel Chavez Gamboa                            *
 #*   miguel@codea.me                                                       *
 #*                                                                         *
 #*   This library is free software; you can redistribute it and/or         *
 #*   modify it under the terms of the GNU Lesser General Public            *
 #*   License as published by the Free Software Foundation; either          *
 #*   version 2 of the License, or (at your option) any later version.      *
 #*                                                                         *
 #*   This library is distributed in the hope that it will be useful,       *
 #*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 #*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
 #*   GNU Lesser General Public License for more details.                   *
 #*                                                                         *
 #*   You should have received a copy of the GNU Lesser General  Public     *
 #*   License along with this program; if not, write to the                 *
 #*   Free Software Foundation, Inc.,                                       *
 #*   51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.         *
 #***************************************************************************

from PySide import QtGui, QtCore, QtSvg


class PanelPosition:
    Top = 1
    Bottom = 2
    Left = 3
    Right = 4

class PanelMode:
    Auto = 1
    Manual = 2

class PanelConstants:
    minH = 100
    minW = 100

    

class cmFloatPanel(QtSvg.QSvgWidget):
    def __init__(self, parent, File, pos, w, h):
        super(cmFloatPanel, self).__init__(parent)

        #member variables
        self.hideCompletely = False
        self.margin = 10
        self.position = pos
        self.parent = parent
        self.filename = File
        self.canBeHidden = False #for hidding when is showing.
        self.animRate = 500
        self.maxHeight = PanelConstants.minW
        self.maxWidth  = PanelConstants.minH
        self.mode = PanelMode.Auto

        #properties
        self.setMaxWidth(w)
        self.setMaxHeight(h)
        self.setFixedHeight(0)

        #Gui components
        self.hLayout = QtGui.QHBoxLayout()
        self.hLayout.setContentsMargins(self.margin,self.margin,self.margin,self.margin)
        self.setLayout(self.hLayout)
        self.load(File)
        
        #Postition it on its place
        QtCore.QTimer.singleShot(100, self.reposition)
        
        #animation
        self.timeLine  = QtCore.QTimeLine(self.animRate, self)
        self.timeLine.finished.connect(self.onAnimationFinished)
        self.timeLine.frameChanged[int].connect(self.animate)


    def setFile(self, File):
        self.load(File)

    def setMaxHeight(self, m):
        self.setMaximumHeight(m)
        self.maxHeight = m
        self.reposition()

    def setMaxWidth(self,m):
        self.setMaximumWidth(m)
        self.maxWidth = m
        self.reposition()

    def setSize(self, w, h):
        self.setMaxWidth(w)
        self.setMaxHeight(h)

    def setPosition(self, pos):
        #only changes the position when the notification is not showing..
        if self.timeLine.state() == QtCore.QTimeLine.NotRunning and not self.canBeHidden:
            self.position = pos
            #recalculate its rect and show it there...
            self.reposition()


    def addWidget(self, widget):
        self.hLayout.addWidget(widget, 1, QtCore.Qt.AlignCenter)


    def hideOnUserRequest(self):
        self.hideDialog()


    def setMode(self, mode):
        self.mode = mode


    def setHiddenCompletely(self, b):
        self.hideCompletely = b


    def hideDialog(self):
        if self.canBeHidden:
            self.timeLine.setEasingCurve(QtCore.QEasingCurve.InExpo)
            self.timeLine.toggleDirection() #reverse!
            self.timeLine.start()


    def onAnimationFinished(self):
        if self.timeLine.direction() == QtCore.QTimeLine.Forward :
            self.canBeHidden = True
        else:
            self.canBeHidden = False
        if self.hideCompletely:
            hide()


    def showPanelDelayed(self):
        if self.underMouse():
            QtCore.QTimer.singleShot(100, self.showPanel)


    def reparent(self, newparent):
        self.setParent(newparent)
        self.parent = newparent
        #update
        self.reposition()

    def fixPos(self):
        '''
        HACK:
        This is to fix position, the bad position is because when positioned if
        the parent is not showing, the parent size is small (100,30).
        Calling this method when the parent is showing ensures the position is correct.
        '''
        self.hide()
        self.reposition()
        QtCore.QTimer.singleShot(100, self.show)

    def reposition(self):
        windowGeom = self.parent.geometry()
        midPointX = (windowGeom.width()/2)
        midPointY = (windowGeom.height()/2)
        newX = 0
        newY = 0
        dRect = QtCore.QRect()

        if (midPointX-(self.maxWidth/2)) < 0:
            newX = 0
        else:
            newX = midPointX - (self.maxWidth/2)

        if (midPointY-(self.maxHeight/2)) < 0:
            newY = 0
        else:
            newY = midPointY - (self.maxHeight/2);

        #what position is it?
        if self.position == PanelPosition.Top:
            newY = self.margin-self.maxHeight
        elif self.position == PanelPosition.Bottom:
            newY = self.parent.height()+self.height()-self.margin
        elif self.position == PanelPosition.Left:
            newX = self.margin-self.maxWidth
        else: #Right
            newX = self.parent.width()-self.margin

        dRect.setX(newX)
        dRect.setY(newY)
        self.setFixedWidth(self.maxWidth) #width maybe is not yet defined.
        self.setFixedHeight(self.maxHeight)
        self.setGeometry(dRect)


    def showPanel(self):
        self.timeLine.setEasingCurve(QtCore.QEasingCurve.OutExpo)
        if self.timeLine.state() == QtCore.QTimeLine.NotRunning and not self.canBeHidden:
            self.setGeometry(-1000,-1000,0,0)
            self.show()
            #update steps for animation, now that the panel is showing.
            maxStep = 0
            minStep = 0

            if self.position == PanelPosition.Top:
                minStep = -self.maxHeight+self.margin
                maxStep = -6
            elif self.position == PanelPosition.Bottom:
                maxStep = self.parent.geometry().height()-self.maxHeight
                minStep = self.parent.geometry().height()-self.margin
            elif self.position == PanelPosition.Left:
                minStep = -self.maxWidth+self.margin
                maxStep = -6
            else: #right
                minStep = self.parent.geometry().width()-self.margin
                maxStep = self.parent.geometry().width()-self.maxWidth

            self.timeLine.setFrameRange(minStep,maxStep)
            #make it grow
            self.timeLine.setDirection(QtCore.QTimeLine.Forward)
            self.timeLine.start()


    def animate(self, step):
        windowGeom = self.parent.geometry()
        midPointX = (windowGeom.width()/2)
        midPointY = (windowGeom.height()/2)
        newY = 0
        newX = 0
        dRect = QtCore.QRect()
        
        if (midPointX-(self.maxWidth/2)) < 0:
            newX = 0
        else:
            newX = midPointX - (self.maxWidth/2)
        if (midPointY-(self.maxHeight/2)) < 0:
            newY = 0
        else:
            newY = midPointY - (self.maxHeight/2)


        if self.position == PanelPosition.Bottom or self.position ==  PanelPosition.Top:
            dRect.setX(newX)
            dRect.setY(step)
        else:
            dRect.setY(newY)
            dRect.setX(step)

        dRect.setWidth(self.maxWidth)
        dRect.setHeight(self.maxHeight)
        self.setGeometry(dRect)
        self.setFixedHeight(self.maxHeight)
        self.setFixedWidth(self.maxWidth)
        

    def enterEvent(self, event):
        if self.mode == PanelMode.Auto:
            QtCore.QTimer.singleShot(300, self.showPanelDelayed)


    def leaveEvent(self, event):
        if self.mode == PanelMode.Auto:
            QtCore.QTimer.singleShot(100, self.hideOnUserRequest)


    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            if self.mode == PanelMode.Manual:
                self.hideOnUserRequest()
        else:
            #if not ESC, then let the base clase process it..
            super(cmAboutDialog, self).keyPressEvent(event)
