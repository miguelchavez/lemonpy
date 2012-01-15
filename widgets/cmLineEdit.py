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


#from django.utils.translation import ugettext as _
from gettext import gettext as _

class cmLineEdit(QtGui.QLineEdit):
    '''
    Important, when using this class, do not set the placeholderText. Because, even clearing it here, it is drawn over our text.
    '''

    #NOTE: create the signal -- This must be created outside of the __init__ . Not for the current instance as inside __init__ does.
    #http://groups.google.com/group/pyside/browse_thread/thread/a4090f6014a5ebdf
    plusKeyPressed = QtCore.Signal()
    
    def __init__(self, parent):
        super(cmLineEdit, self).__init__(parent)

        self.parent = parent
        self.drawEmptyMsg = True
        self.actualColor  = 0
        self.autoClear = True
        self.timer = QtCore.QTimer(self)
        self.shakeTimeToLive = 0
        self.par = False
        self.parTimes = 0

        self.shakeTimer = QtCore.QTimer(self)
        self.shakeTimer.setInterval(20)
        self.timer.setInterval(30)
        self.emptyMessage = _("Type here...")

        self.textEdited[unicode].connect(self.onTextChange)
        self.timer.timeout.connect(self.stepColors)
        self.shakeTimer.timeout.connect(self.shakeIt)

        #self.setPlaceholderText("")


    def getEmptyMessage(self):
        return self.emptyMessage

    def setEmptyMessage(self, msg):
        self.emptyMessage = msg
        self.drawEmptyMsg = True if self.text() == '' else False
        print 'textIsEmpty %s'%self.drawEmptyMsg
        self.update()

    def shake(self):
        self.shakeTimer.start()
        QtCore.QTimer.singleShot(3000,self.shakeTimer.stop())

    def paintEvent(self, ev):
        super(cmLineEdit, self).paintEvent(ev)
        if self.text() == '':
            p = QtGui.QPainter(self)
            f = QtGui.QFont()
            f.setItalic(True)
            p.setFont(f)

            color = QtGui.QColor(self.palette().color(self.foregroundRole()))
            color.setAlphaF(0.5)
            p.setPen(color)

            #FIXME: fugly alert!
            #qlineedit uses an internal qstyleoption set to figure this out
            #and then adds a hardcoded 2 pixel interior to that.
            #probably requires fixes to Qt itself to do this cleanly
            #see define horizontalMargin 2 in qlineedit.cpp
            opt = QtGui.QStyleOptionFrame()
            self.initStyleOption(opt)
            cr = self.style().subElementRect(QtGui.QStyle.SE_LineEditContents, opt, self)
            cr.setLeft(cr.left() + 2)
            cr.setRight(cr.right() - 2)

            p.drawText(cr, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, self.emptyMessage)

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

    def setError(self, msg):
        self.timer.start() #for colors
        self.setToolTip(msg)
        if self.autoClear:
            #create a timer to clear the error.
            QtCore.QTimer.singleShot(5000,self.clearError)

    def stepColors(self):
        if actualColor > 199:
            self. actualColor = 0
            self.timer.stop()
        else:
            self.actualColor = actualColor + 2
            self.setStyleSheet(" QLineEdit { background: rgb(255,%s,0); color:white; font-weight: bold;}"%(actualColor))

    def clearError(self):
        self.setStyleSheet("")
        self.setToolTip("")

    def setAutoClearError(self, state):
        '''
        This function needs to be called before the setError() one... to enable the Qtimer::singleShot
        '''
        self.autoClear = state

    def onTextChange(self, text):
        self.clearError()


    def focusInEvent(self, ev):
        if self.drawEmptyMsg:
            self.drawEmptyMsg = False
            self.update()
        super(cmLineEdit, self).focusInEvent(ev)

    def focusOutEvent(self, ev):
        if self.text() == '':
            self.drawEmptyMsg = True
            self.update()
        super(cmLineEdit, self).focusOutEvent(ev)

    def keyPressEvent(self, ev):
        '''
        Check for our special keys +,Enter (specific for lemonPOS)
        The Enter key is the one located at the numeric pad. The other is called RETURN.
        '''
        if ev.key() == QtCore.Qt.Key_Plus or ev.key() == QtCore.Qt.Key_Enter:
            self.plusKeyPressed.emit()
        #anyway we must send enter and + key events...
        super(cmLineEdit, self).keyPressEvent(ev)