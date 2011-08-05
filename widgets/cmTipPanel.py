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

class TipPosition:
    Above = 1
    Below = 2

class PanelConstants:
    minH = 100
    minW = 100


class cmTipPanel(QtSvg.QSvgWidget):
    '''
     This Class shows a tip frame centered horizontally and on bottom of  its parter.
     It should be parented on a bigger widget to be visible (for example the main window)
     and also must be the same parent for the parter (must be on the same container).
     Its partner is the widget where the tip frame will be shown on.
    '''
    def __init__(self, parent, partner, File, icon, pos):
        super(cmTipPanel, self).__init__(parent)

        #member variables
        self.hideCompletely = False
        self.position = pos
        self.parent = parent
        self.partner = partner
        self.filename = File
        self.closedByUser = False
        self.timeToLive = 4000
        self.animRate = 500

        #properties
        self.setMinimumHeight(0)
        self.setFixedHeight(0)
        self.maxHeight = PanelConstants.minW
        self.maxWidth  = PanelConstants.minH

        #Gui components
        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(5,5,5,5)
        self.setLayout(self.layout)
        self.icon = QtGui.QLabel()
        self.message = QtGui.QLabel()
        self.icon.setMaximumHeight(32)
        self.icon.setAlignment(QtCore.Qt.AlignCenter)
        self.load(File)
        self.setIcon(icon)

        if self.position == TipPosition.Above :
            self.layout.addWidget(self.message)
            self.layout.addWidget(self.icon)
        else:
            self.layout.addWidget(self.icon)
            self.layout.addWidget(self.message)

        self.setLayout(self.layout)
        self.message.setWordWrap(True)
        self.message.setMargin(5)


        #animation
        self.timeLine  = QtCore.QTimeLine(self.animRate, self)
        self.timeLine.setFrameRange(0, self.maxHeight)
        #self.timeLine.finished.connect(self.onAnimationFinished)
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

    def autoHide(self):
        if not self.closedByUser:
            self.timeLine.setDirection(QtCore.QTimeLine.Backward)
            self.timeLine.start()
        else:
            self.closedByUser = not self.closedByUser

    def setIcon(self, icon):
        self.icon.setPixmap(icon)


    def showTip(self, msg, ttl):
        self.showPanel(msg, ttl) #simply a shortcut

    def showPanel(self, msg, ttl):
        self.timeToLive = ttl
        self.message.setText(msg)
        #WARNING: if a tip is showing, if another showTip() is called, it is not animated, just changed the msg.
        if self.timeLine.state() == QtCore.QTimeLine.NotRunning and self.size().height() <= 0 :
            self.show()
            #make it grow
            self.timeLine.setDirection(QtCore.QTimeLine.Forward)
            self.timeLine.start()
            #autoShrink
            QtCore.QTimer.singleShot(self.timeToLive-1000, self.autoHide)

    def animate(self, newSize):
        listRect = self.partner.rect()
        below = self.partner.mapToGlobal(listRect.bottomLeft())
        above = self.partner.mapToGlobal(listRect.topLeft())
        windowPos = self.parent.mapToGlobal(QtCore.QPoint(0,0)) #the window is the parent, we assume this.
        
        #correct global positions with current window position.
        below = below - windowPos
        above = above -windowPos
        
        #where to draw above or below its partner
        if self.position == TipPosition.Below :
            #here will grow from top to bottom
            listRect.setX(below.x()+10)
            listRect.setY(below.y()-3)
            self.setGeometry(listRect)
        else:
            # here will grow from bottom to top
            newY = above.y() - newSize + 3
            listRect.setX(above.x()+10)
            listRect.setY(newY)
            self.setGeometry(listRect)
        self.setFixedHeight(newSize);
        self.setFixedWidth(self.partner.width()-20)


    def mousePressEvent(self, event):
        self.autoHide() #we simply want to close the tip on any mouse click
        self.closedByUser = True
        super(cmTipPanel, self).keyPressEvent(event) #NOTE:Really needed?

