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


class cmAboutDialog(QtSvg.QSvgWidget):
    def __init__(self, parent, File, msg):
        super(cmAboutDialog, self).__init__(parent)

        #Gui components
        self.message = QtGui.QLabel()
        #self.icon    = QtGui.QLabel()
        #self.hLayout = QtGui.QHBoxLayout()
        self.vLayout = QtGui.QVBoxLayout()
        self.vLayout.setContentsMargins(20,70,20,20)
        self.spring = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        self.button = QtGui.QPushButton(self)
        self.button.setDefault(True)
        self.button.setShortcut("Esc") #FIXME:This does not works! Try capture key events...
        self.button.setText("Ok")
        self.button.setMaximumWidth(150)

        #setting member properties
        self.parent = parent
        self.maxHeight = 0
        self.maxWidth = 0
        #self.animType = aType #NOT USED FOR NOW. Will implement later...
        self.setMinimumHeight(100)
        self.setFixedSize(0,0)
        self.setMaxHeight(300)
        self.setMaxWidth(300)
        self.animRate = 2500 #default animation speed (half second rate).
        self.shakeTimeToLive = 1500 #default shake time..
        self.par = False
        self.parTimes = 0

        #The timer
        self.shakeTimer = QtCore.QTimer(self)
        self.shakeTimer.setInterval(20)
        self.shakeTimer.timeout.connect(self.shakeIt)

        #Setting gui properties
        self.message.setText(msg)
        self.message.setWordWrap(True)
        self.message.setAlignment(QtCore.Qt.AlignJustify | QtCore.Qt.AlignVCenter)
        self.message.setMargin(5)
        #self.icon.setPixmap(icon)
        #self.icon.setMaximumHeight(70)
        #self.icon.setMaximumWidth(70)
        #self.icon.setAlignment(QtCore.Qt.AlignLeft)
        #self.icon.setMargin(4)
        self.load(File)
        
        self.setLayout(self.vLayout)
        #self.hLayout.addWidget(self.icon,0,QtCore.Qt.AlignCenter)
        self.vLayout.addWidget(self.message)
        #self.vLayout.addLayout(self.hLayout,2)
        self.vLayout.addItem(self.spring)
        self.vLayout.addWidget(self.button, 0, QtCore.Qt.AlignCenter)
        

        #animation
        self.timeLine  = QtCore.QTimeLine(self.animRate, self)
        self.timeLine.finished.connect(self.onAnimationFinished)
        self.timeLine.frameChanged[int].connect(self.animate)
        

    def setFile(self, File):
        self.load(File)

    def setMessage(self, msg):
        self.message.setText(msg)

    def setMaxHeight(self, m):
        self.setMaximumHeight(m)
        self.maxHeight = m

    def setMaxWidth(self,m):
        self.setMaximumWidth(m)
        self.maxWidth = m

    def setSize(self, w, h):
        self.setMaxWidth(w)
        self.setMaxHeight(h)
    
    def setTextColor(self, c):
        self.message.setStyleSheet("color:%s"%(c))

    def hideDialog(self):
        self.timeLine.setEasingCurve(QtCore.QEasingCurve.InExpo)
        self.timeLine.toggleDirection() #reverse!
        self.timeLine.start()

    def onAnimationFinished(self):
        if self.timeLine.direction() == QtCore.QTimeLine.Backward :
            self.close()
            self.shakeTimer.stop()

    def shake(self):
        self.shakeTimer.start()
        if self.shakeTimeToLive > 0 :
            QtCore.QTimer.singleShot(self.shakeTimeToLive, self.shakeTimer.stop)


    def shakeIt(self):
        if self.par:
            if self.parTimes < 15 :
                if self.parTimes % 2 == 0 :
                    self.setGeometry(self.geometry().x()-3, self.geometry().y()+3, self.geometry().width(), self.geometry().height())
                else:
                    self.setGeometry(self.geometry().x()+3, self.geometry().y()+3, self.geometry().width(), self.geometry().height())
            self.parTimes += 1
            if self.parTimes > 39 :
                self.parTimes = 0
        else:
            if self.parTimes < 15 :
                if  self.parTimes % 2 == 0 :
                    self.setGeometry(self.geometry().x()+3, self.geometry().y()-3, self.geometry().width(), self.geometry().height())
                else:
                    self.setGeometry(self.geometry().x()-3, self.geometry().y()-3, self.geometry().width(), self.geometry().height())
        #change direction
        self.par = not self.par


    def animate(self, step):
        #This just animates from up to down. Maybe later port the other animations.
        windowGeom = self.parent.geometry()
        midPointX = (windowGeom.width()/2)
        midPointY = (windowGeom.height()/2)
        newY = 0
        newX = 0
        dRect = QtCore.QRect()
        
        if (midPointY-(self.maxHeight/2)) < 0 :
            newY = 0
        else:
            newY = midPointY - self.maxHeight/2
        
        dRect.setX(step)
        dRect.setY(newY)
        dRect.setWidth(self.maxWidth)
        dRect.setHeight(self.maxHeight)
        self.setGeometry(dRect)
        self.setFixedHeight(self.maxHeight)
        self.setFixedWidth(self.maxWidth)


    def showDialog(self, msg):
        if msg:
            self.setMessage( msg )
        self.setGeometry(-1000,-1000,0,0)
        self.show()
        maxStep = 0
        minStep = 0

        maxStep = (self.parent.geometry().width()/2)-(self.maxWidth/2)
        minStep = -self.maxWidth

        #NOTE: We assume everybody has qt 4.6+.. how to check it? (in c++ -> with #if QT_VERSION >= 0x040600)
        self.timeLine.setEasingCurve(QtCore.QEasingCurve.OutElastic) #OutBounce
        self.timeLine.setFrameRange(minStep,maxStep)
        self.timeLine.setDirection(QtCore.QTimeLine.Forward)
        self.timeLine.start()
        self.button.setFocus()

    #def returnPressed(self):
        #We can let the widget user (the app) to connect the editPassword returnPressed signal to its own method to authenticate the user.
        #Example: self.lockDialog.editPassword.returnPressed.connect(self.unlockScreen)
        #pass
        
