#!/usr/bin/env python
# -*- coding: utf-8 -*-

#/***************************************************************************
#*   Copyright (C) 2011 by Miguel Chavez Gamboa                            *
#*   miguel@lemonpos.org                                                   *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU General Public License as published by  *
#*   the Free Software Foundation; either version 2 of the License, or     *
#*   (at your option) any later version.                                   *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU General Public License for more details.                          *
#*                                                                         *
#*   You should have received a copy of the GNU General Public License     *
#*   along with this program; if not, write to the                         *
#*   Free Software Foundation, Inc.,                                       *
#*   51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.         *
#***************************************************************************/

from PySide import QtCore, QtGui
from ui_mainview import *

class MainWindow(QtGui.QMainWindow, Ui_mainForm):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.setCentralWidget(self.mainWidget)
        #NOTE: I dont know if this is a bug, but i need to include a QWidget container which is parent of all widgets and its layouts
        #      to be able to set this "mainWidget" as the central widget. If i dont use this, im not able to set one widget as central
        #      and all the widgets to be displayed in the main window. And if i do not assign a central widget then all widgets appear
        #      at the left,top corner with the default size without any layout (size of widgets according to window size). This does not
        #      happens on the C++ side of Qt.
        #      Also note that im a beginner with PySide and Python.

        self.readSettings()
        self.setUnifiedTitleAndToolBarOnMac(True)

        self.createActions()

        print 'finish init...'
        print 'MainWindow size: %s x %s'%(self.width(), self.height())


    def closeEvent(self, event):
        self.writeSettings()
        event.accept()
        print 'Close Event...'


    def about(self):
        QtGui.QMessageBox.about(self, "About LemonPy",
                "<b>LemonPy</b> is the prototype for the new lemonPOS."
                "The name means Lemon Pie and also refers to Python.")


    def createActions(self):
        print 'creating actions...'
        self.exitAction = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q", statusTip="Exit lemonPy", triggered=self.close)
        self.aboutAction = QtGui.QAction("&About", self, statusTip="Show the lemonPy's About box",  triggered=self.about)

        self.exitAction.setIcon(QtGui.QIcon(":/images/icons/images/money.png"))
        self.aboutAction.setIcon(QtGui.QIcon(":/images/icons/images/card.png"))

        #FIXME: Remember to change the next toolbar name!
        self.toolBarOne  = QtGui.QToolBar("Toolbar one")
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolBarOne)
        self.toolBarOne.addAction(self.exitAction)
        self.toolBarOne.addAction(self.aboutAction)
        #NOTE: Why the shortcuts dont work if the actions are not visible in the ui via a toolbar or menubar?



    def readSettings(self):
        print 'Reading settings...'
        settings = QtCore.QSettings("codea.me", "lemonPy")
        pos = settings.value("pos", QtCore.QPoint(200, 200))
        size = settings.value("size", QtCore.QSize(400, 400))
        self.resize(size)
        self.move(pos)
        print 'settings readed'


    def writeSettings(self):
        print 'writing settings'
        settings = QtCore.QSettings("codea.me", "lemonPy")
        settings.setValue("pos", self.pos())
        settings.setValue("size", self.size())
        print 'settings written'
