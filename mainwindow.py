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

import decimal
from decimal import *

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

        #self.readSettings() FIXME: Just remember to uncomment later
        self.setUnifiedTitleAndToolBarOnMac(True)

        # go fullscreen
        self.showFullScreen() #TODO:Add an option to not show fullscreen.

        #Create the actions...
        self.createActions()

        #TODO: Decide which method use to get payment options.
        #      By default is CASH, a button to launch a dialog to get debit/credit card data. Another payment method?
        self.groupPaymentClient.setVisible(False) #reparent this to the dialog -use mibit dialogs when ported to python.

        #flags setup
        self.loggedUser = None #This will be a django model instance.
        self.config     = None #This will be a django model instance.
        self.products   = None #This will be a django model instance.
        self.saleInProgress = False;
        self.totalSum = Decimal()
        self.subtotal = Decimal()
        self.taxes = Decimal()
        self.drawerCreated = False #TODO: investigate about open a device -same as qt....
        self.currentBalanceId = 0
        self.operationStarted = False

        #Create timer for the clock/date
        self.timerClock = QtCore.QTimer(self)
        self.timerClock.setInterval(1000)
        self.timerClock.timeout.connect(self.updateClock)
        self.timerClock.start()
        self.updateDate()
        self.lblStatusCashier.setText("Unattended")


    def closeEvent(self, event):
        #TODO:  Can we close? Is there any sale in process? Ask the user to really exit and discard the sale?
        self.writeSettings()
        event.accept()


    def about(self):
        QtGui.QMessageBox.about(self, "LemonPy v0.0 (C) 2011 Miguel Chavez Gamboa",
                "<b>LemonPy</b> is the prototype for the new lemonPOS."
                "The name means Lemon Pie and also refers to Python.")


    def createActions(self):
        print 'creating actions...'
        self.exitAction = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q", statusTip="Exit lemonPy", triggered=self.close)
        self.aboutAction = QtGui.QAction("&About", self, statusTip="Show the lemonPy's About box",  triggered=self.about)
        self.showPaymentOptionsAction = QtGui.QAction("Show Payment Options", self, shortcut="Ctrl+P", statusTip="Show more payment options...",  triggered=self.showPaymentOptions)

        self.exitAction.setIcon(QtGui.QIcon(":/images/icons/images/money.png"))
        self.aboutAction.setIcon(QtGui.QIcon(":/images/icons/images/card.png"))
        self.showPaymentOptionsAction.setIcon(QtGui.QIcon(":/images/icons/images/card.png"))

        #Adding the left toolbar. non-movable.
        self.toolBarLeft  = QtGui.QToolBar("Left Toolbar")
        self.toolBarLeft.setMovable(False)
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolBarLeft)
        self.toolBarLeft.addAction(self.exitAction)
        self.toolBarLeft.addAction(self.aboutAction)
        #NOTE: Why the shortcuts dont work if the actions are not visible in the ui via a toolbar or menubar?

        #Adding the top toolbar, non-movable for some important actions. This toolbar is not on the toolbarArea, it is aside the code input box.
        self.toolBarTop = QtGui.QToolBar("Top Toolbar", self.toolWidget)
        self.toolBarTop.setMovable(False)
        self.toolBarTop.addAction(self.aboutAction)
        self.toolWidgetLayout.addWidget(self.toolBarTop)

        #Adding the tendered widget toolbar.
        self.tenderedToolBar = QtGui.QToolBar("Tendered Toolbar", self.tenderedWidget)
        self.tenderedToolBar.setMovable(False)
        self.tenderedToolBar.addAction(self.showPaymentOptionsAction)
        self.tenderedWidgetLayout.addWidget(self.tenderedToolBar)


    def showPaymentOptions(self):
        #Not coded yet...
        print 'selecting payment options...'


    def updateClock(self):
        time = QtCore.QTime.currentTime()
        timeString = time.toString("hh:mm")
        if time.second() % 2 == 0:
            timeString = timeString.replace(':', '.')
        else:
            timeString = timeString.replace('.',':')

        self.lblStatusTime.setText(timeString)
        
        if time.hour() == 0 and time.minute() == 0 and time.second() == 0:
            updateDate()


    def updateDate(self):
        date = QtCore.QDate.currentDate()
        dateString = date.toString("dddd MMM d")
        self.lblStatusDate.setText(dateString)


    def readSettings(self):
        #settings = QtCore.QSettings("codea.me", "lemonPy")
        pass
        #pos = settings.value("pos", QtCore.QPoint(200, 200))
        #size = settings.value("size", QtCore.QSize(400, 400))
        #self.resize(size)
        #self.move(pos)


    def writeSettings(self):
        pass
        #settings = QtCore.QSettings("codea.me", "lemonPy")
        #settings.setValue("pos", self.pos())
        #settings.setValue("size", self.size())
