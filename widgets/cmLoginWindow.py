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


from django.utils.translation import ugettext as _

class cmLoginWindow(QtSvg.QSvgWidget):
    def __init__(self, parent, File):
        super(cmLoginWindow, self).__init__(parent)

        #Gui components
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.lblUsername = QtGui.QLabel(self)
        self.lblUsername.setMaximumSize(QtCore.QSize(200, 16777215))
        self.lblUsername.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblUsername.setObjectName("lblUsername")
        self.gridLayout.addWidget(self.lblUsername, 0, 1, 1, 1)
        self.editUsername = QtGui.QLineEdit(self)
        self.editUsername.setMaximumSize(QtCore.QSize(200, 16777215))
        self.editUsername.setObjectName("editUsername")
        self.gridLayout.addWidget(self.editUsername, 0, 2, 1, 1)
        self.lblPassword = QtGui.QLabel(self)
        self.lblPassword.setMaximumSize(QtCore.QSize(200, 16777215))
        self.lblPassword.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblPassword.setObjectName("lblPassword")
        self.gridLayout.addWidget(self.lblPassword, 1, 1, 1, 1)
        self.editPassword = QtGui.QLineEdit(self)
        self.editPassword.setMaximumSize(QtCore.QSize(200, 16777215))
        self.editPassword.setObjectName("editPassword")
        self.gridLayout.addWidget(self.editPassword, 1, 2, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 3, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.btnExit = QtGui.QPushButton(self)
        self.btnExit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.btnExit.setObjectName("btnExit")
        self.horizontalLayout.addWidget(self.btnExit)
        self.btnLogin = QtGui.QPushButton(self)
        self.btnLogin.setMinimumSize(QtCore.QSize(150, 0))
        self.btnLogin.setMaximumSize(QtCore.QSize(200, 16777215))
        self.btnLogin.setDefault(True)
        self.btnLogin.setObjectName("btnLogin")
        self.horizontalLayout.addWidget(self.btnLogin)
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem4)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem5 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem5)


        self.editPassword.setEchoMode(QtGui.QLineEdit.Password)
        #Enter texts
        self.lblUsername.setText("<b><i>" + _("Username:") + "</i></b>")
        self.lblPassword.setText("<b><i>" + _("Password:") + "</i></b>")
        self.lblUsername.setStyleSheet("color:white")
        self.lblPassword.setStyleSheet("color:white")
        self.editPassword.setPlaceholderText(_("Enter your password"))
        self.editUsername.setPlaceholderText(_("Enter your username"))
        self.btnExit.setText(_("Exit"))
        self.btnLogin.setText(_("Log in"))
        
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
        self.load(File)

        #animation
        self.timeLine  = QtCore.QTimeLine(self.animRate, self)
        self.timeLine.finished.connect(self.onAnimationFinished)
        self.timeLine.frameChanged[int].connect(self.animate)


    def getUserName(self):
        return self.editUsername.text()

    def getPassword(self):
        return self.editPassword.text()

    def setFile(self, File):
        self.load(File)

    def setMaxHeight(self, m):
        self.setMaximumHeight(m)
        self.maxHeight = m

    def setMaxWidth(self,m):
        self.setMaximumWidth(m)
        self.maxWidth = m

    def setSize(self, w, h):
        self.setMaxWidth(w)
        self.setMaxHeight(h)
    
    def hideDialog(self):
        self.timeLine.setEasingCurve(QtCore.QEasingCurve.InExpo)
        self.timeLine.toggleDirection() #reverse!
        #NOTE: Anyone using this class must be aware of THIS, the aboutBox parent must have a disableUi/actions & enableUi/actions Methods.
        self.timeLine.start()
        self.parent.enableUi()
        self.parent.enableActions()
        self.editPassword.clear()
        self.editUsername.clear()

    def onAnimationFinished(self):
        if self.timeLine.direction() == QtCore.QTimeLine.Backward :
            self.close()
            self.shakeTimer.stop()

    def shake(self):
        self.shakeTimer.start()
        if self.shakeTimeToLive > 0 :
            QtCore.QTimer.singleShot(self.shakeTimeToLive, self.shakeTimer.stop)


    def shakeIt(self):
        print 'shaking...  par:%s  parTimes:%s'%(self.par, self.parTimes)
        if self.par:
            if self.parTimes < 10 :
                if self.parTimes % 2 == 0 :
                    self.setGeometry(self.geometry().x()-5, self.geometry().y()+5, self.geometry().width(), self.geometry().height())
                else:
                    self.setGeometry(self.geometry().x()+5, self.geometry().y()+5, self.geometry().width(), self.geometry().height())
            else:
                self.parTimes = 0
            self.parTimes += 1
        else:
            if self.parTimes < 10 :
                if  self.parTimes % 2 == 0 :
                    self.setGeometry(self.geometry().x()+5, self.geometry().y()-5, self.geometry().width(), self.geometry().height())
                else:
                    self.setGeometry(self.geometry().x()-5, self.geometry().y()-5, self.geometry().width(), self.geometry().height())
            else:
                self.parTimes = 0
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

        if (midPointX-(self.maxWidth/2)) < 0 :
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


    def showDialog(self):
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

        #NOTE: Anyone using this class must be aware of THIS, the aboutBox parent must have a disableUi/actions & enableUi/actions Methods.
        self.parent.disableUi()
        self.parent.disableActions()

        self.editUsername.setFocus()

