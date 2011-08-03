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


class cmPasswordDialog(QtSvg.QSvgWidget):
    def __init__(self, parent, File, msg, icon):
        super(cmPasswordDialog, self).__init__(parent)

        #Gui components
        self.message = QtGui.QLabel()
        self.icon    = QtGui.QLabel()
        self.hLayout = QtGui.QHBoxLayout()
        self.vLayout = QtGui.QVBoxLayout()
        self.editPassword = QtGui.QLineEdit(self)

        #setting member properties
        self.parent = parent
        self.maxHeight = 0
        self.maxWidth = 0
        #self.animType = aType #NOT USED FOR NOW. Will implement later...
        self.setMinimumHeight(100)
        self.setFixedSize(0,0)
        self.setMaxHeight(300)
        self.setMaxWidth(400)
        self.animRate = 500; #default animation speed (half second rate).
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
        self.icon.setPixmap(icon)
        self.icon.setMaximumHeight(70)
        self.icon.setMaximumWidth(70)
        self.icon.setAlignment(QtCore.Qt.AlignLeft)
        self.icon.setMargin(4)
        self.load(File)
        self.editPassword.clear()
        self.editPassword.setEchoMode(QtGui.QLineEdit.Password)
        
        self.setLayout(self.vLayout)
        self.hLayout.addWidget(self.icon,0,QtCore.Qt.AlignCenter)
        self.hLayout.addWidget(self.message,1,QtCore.Qt.AlignCenter)
        self.vLayout.addLayout(self.hLayout,2)
        self.vLayout.addWidget(self.editPassword,1,QtCore.Qt.AlignCenter)

        #animation
        self.timeLine  = QtCore.QTimeLine(self.animRate, self)
        self.wTimeLine = QtCore.QTimeLine(2000, self)
        self.wTimeLine.setFrameRange(90,190);
        self.wTimeLine.setCurveShape(QtCore.QTimeLine.CosineCurve)
        #connect signals for the animators
        self.timeLine.finished.connect(self.onAnimationFinished)
        self.timeLine.frameChanged[int].connect(self.animate)
        self.wTimeLine.frameChanged[int].connect(self.waveIt)
        

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

    def getPassword(self):
        pswd = self.editPassword.text()
        #here we clean the password. We cannot doit at the ReturnPressed event because at that time the password is not still retrieved by the client app.
        #we can save the password for later if called this method again and there is not password in the editPassword
        self.editPassword.clear()
        return pswd

    def cleanPassword(self):
        self.editPassword.clear()

    def hideDialog(self):
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
            if self.parTimes < 5 :
                if self.parTimes % 2 == 0 :
                    self.setGeometry(self.geometry().x()-3, self.geometry().y()+3, self.geometry().width(), self.geometry().height())
                else:
                    self.setGeometry(self.geometry().x()+3, self.geometry().y()+3, self.geometry().width(), self.geometry().height())
            self.parTimes += 1
            if self.parTimes >39 :
                self.parTimes = 0
        else:
            if self.parTimes < 5 :
                if  self.parTimes % 2 == 0 :
                    self.setGeometry(self.geometry().x()+3, self.geometry().y()-3, self.geometry().width(), self.geometry().height())
                else:
                    self.setGeometry(self.geometry().x()-3, self.geometry().y()-3, self.geometry().width(), self.geometry().height())
        #change direction
        self.par = not self.par


    def wave(self):
        self.wTimeLine.start()

    def waveIt(self, step):
        print 'WaiveIt(step=%s)'%step
        if (self.timeLine.state() == QtCore.QTimeLine.NotRunning or not self.shakeTimer.isActive() ) :
            self.setGeometry(self.geometry().x(),step, self.geometry().width(), self.geometry().height());

    def animate(self, step):
        #This just animates from up to down. Maybe later port the other animations.
        #print 'Animate(step=%s)  maxWidth=%s, maxHeight=%s'%(step, self.maxWidth, self.maxHeight)
        windowGeom = self.parent.geometry()
        midPointX = (windowGeom.width()/2)
        midPointY = (windowGeom.height()/2)
        newY = 0
        newX = 0

        dRect = QtCore.QRect()
        
        if ((midPointX-(self.maxWidth/2)) < 0):
            newX = 0
        else:
            newX = midPointX - self.maxWidth/2
            
        dRect.setX(newX)
        dRect.setY(step)
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

        maxStep = (self.parent.geometry().height()/2)-(self.maxHeight/2)
        minStep = -self.maxHeight

        #NOTE: We assume everybody has qt 4.6+.. how to check it? (in c++ -> with #if QT_VERSION >= 0x040600)
        self.timeLine.setEasingCurve(QtCore.QEasingCurve.OutBounce)
        self.timeLine.setFrameRange(minStep,maxStep)
        self.timeLine.setDirection(QtCore.QTimeLine.Forward)
        self.timeLine.start()
        self.editPassword.setFocus()

    #def returnPressed(self):
        #We can let the widget user (the app) to connect the editPassword returnPressed signal to its own method to authenticate the user.
        #Example: self.lockDialog.editPassword.returnPressed.connect(self.unlockScreen)
        #pass
        

    #TODO: Write the event handler for the enter key!. @270
    #NOTE: How to port signals (for emitting signals)