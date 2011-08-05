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

#our components
from widgets.cmPasswordDialog import *
from widgets.cmAboutDialog import *
from widgets.cmLoginWindow import *
from widgets.cmFloatPanel import *

#django imports
import os, sys
from django.utils.translation import ugettext as _

if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ['DJANGO_SETTINGS_MODULE']='settings'

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from backend.models import *

class MainWindow(QtGui.QMainWindow, Ui_mainForm):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        #NOTE: Next code is for django to know where settings.py is.
        if 'DJANGO_SETTINGS_MODULE' not in os.environ:
            os.environ['DJANGO_SETTINGS_MODULE']='settings'
        # and to add to the sys path the path where this app is. not needed now.
        #sys.path+= [os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]]
        
        
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

        self.clearWidgets()
        self.setupInputFilters()
        self.createActions()
        self.createToolBars()

        #TODO: Decide which method use to get payment options.
        #      By default is CASH, a button to launch a dialog to get debit/credit card data. Another payment method?
        self.groupPayment.setVisible(False) #reparent this to the dialog -use mibit dialogs when ported to python.

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

        QtCore.QTimer.singleShot(1000, self.setupSalesWidget) #wait some time to let the widget take its final size.

        #Lock Password Dialog
        self.lockDialog = cmPasswordDialog(self, ":/icons/images/dialog.svg", "Screen Locked.", ":/icons/images/lemon-lock-screen.png")
        self.lockDialog.setTextColor("white")
        self.lockDialog.setSize(300,150)
        self.lockDialog.editPassword.returnPressed.connect(self.unlockScreen)

        #About box
        self.aboutBox = cmAboutDialog(self, ":/icons/images/about.svg",
            _("<b>LemonPy v 0.0</b> <br><i>&copy;2011 Miguel Chavez Gamboa.<br>miguel@lemonpos.org</i><br><br>" \
            #"<a href='http://www.lemonpos.org/'>www.lemonpos.org</a>, <a href='http://sourceforge.net/apps/mediawiki/lemonpos/index.php?title=Main_Page'>the project Wiki</a><br>" \
            "<b>LemonPy</b> is an <i>open source</i> Point of Sale software targeted for micro, small and medium businesses.<br><br>" \
            "Licensed under the <a href='http://www.gnu.org/licenses/old-licenses/gpl-2.0.html'>GNU General Public License</a>" \
            ))
        self.aboutBox.setTextColor("white")
        self.aboutBox.setSize(350,350)
        self.aboutBox.button.clicked.connect(self.aboutBox.hideDialog)

        #login window
        self.loginWindow = cmLoginWindow(self, ":/icons/images/about.svg")
        self.loginWindow.setSize(350, 350)
        self.loginWindow.btnLogin.clicked.connect(self.doAuth)
        self.loginWindow.editUsername.returnPressed.connect(self.loginWindow.editPassword.setFocus)
        self.loginWindow.editPassword.returnPressed.connect(self.doAuth)
        self.loginWindow.btnExit.clicked.connect(self.close)

        #a float panel
        self.floatPanel = cmFloatPanel(self, ":/icons/images/panel_top.svg", PanelPosition.Top, 550,250)
        self.floatPanel.addWidget(self.groupPayment)
        self.floatPanel.setMode(PanelMode.Auto)
        self.floatPanel.setPosition(PanelPosition.Top)
        self.floatPanel.setHiddenCompletely(False)
        self.floatPanel.show()
        self.groupPayment.setVisible(True)

        #Launch login-dialog
        QtCore.QTimer.singleShot(800, self.login)

    def closeEvent(self, event):
        #TODO:  Can we close? Is there any sale in process? Ask the user to really exit and discard the sale?
        self.writeSettings()
        event.accept()


    def about(self):
        self.aboutBox.showDialog()


    def setupInputFilters(self):
        #Amount Validator
        amountExpr = QtCore.QRegExp("[0-9]*[//.]{0,1}[0-9]{0,5}")
        amountValidator = QtGui.QRegExpValidator(amountExpr, self)
        self.editTendered.setValidator(amountValidator)

        #Code validator.
        codeExpr = QtCore.QRegExp("[0-9]*[//.]{0,1}[0-9]{0,5}[//*]{0,1}[0-9]*[A-Za-z_0-9\\\\/\\-]{0,30}")
        codeValidator = QtGui.QRegExpValidator(codeExpr, self)
        self.editItemCode.setValidator(codeValidator)

        #TODO: Card number validators. and more payment options when implemented.

    def clearWidgets(self):
        self.editItemCode.clear()
        self.editTendered.clear()
        self.tableSale.clearContents()
        self.tableSale.setRowCount(0)
        

    def createActions(self):
        print 'creating actions...'
        self.exitAction = QtGui.QAction(_("E&xit (Ctrl+Q)"), self, shortcut="Ctrl+Q", triggered=self.close)
        self.aboutAction = QtGui.QAction(_("&About"), self, statusTip=_("About"),  triggered=self.about)
        self.showPaymentOptionsAction = QtGui.QAction(_("Show Payment Options (Ctrl+P)"), self, shortcut="Ctrl+P", triggered=self.showPaymentOptions)
        self.balanceAction = QtGui.QAction(_("Balance (Ctrl+B)"), self, shortcut="Ctrl+B",  triggered=self.balance )
        self.loginAction = QtGui.QAction(_("Login (Ctrl+L)"), self, shortcut="Ctrl+L",  triggered=self.login )
        self.codeFocusAction = QtGui.QAction(_("Enter Code (F2)"), self, shortcut="F2",  triggered=self.editItemCode.setFocus )
        self.searchAction = QtGui.QAction(_("Search Products (F3)"), self, shortcut="F3",  triggered=self.showSearch )
        self.removeItemAction = QtGui.QAction(_("Remove Item"), self,  triggered=self.removeSelectedItem )
        self.finishTransactionAction = QtGui.QAction(_("Finish Transaction (F12)"), self, shortcut="F12",  triggered=self.finishTransaction )
        self.cancelTransactionAction = QtGui.QAction(_("Cancel Transaction (F10)"), self, shortcut="F10",  triggered=self.cancelTransaction )
        self.cancelTicketAction = QtGui.QAction(_("Cancel Ticket (F11)"), self, shortcut="F11",  triggered=self.cancelTicket )
        self.startOperationsAction = QtGui.QAction(_("Start Operations (Ctrl+N)"), self, shortcut="Ctrl+N",  triggered=self.startOperations ) #FIXME: QKeySequence::New
        self.goPayAction = QtGui.QAction(_("Enter Payment (F4)"), self, shortcut="F4",  triggered=self.editTendered.setFocus )
        self.priceCheckerAction = QtGui.QAction(_("Price Checker (F9)"), self, shortcut="F9",  triggered=self.showPriceChecker )
        self.reprintTicketAction = QtGui.QAction(_("Reprint Ticket (F5)"), self, shortcut="F5",  triggered=self.reprintTicket )
        self.cashInAction = QtGui.QAction(_("Cash In (F8)"), self, shortcut="F8",  triggered=self.cashIn )
        self.cashOutAction = QtGui.QAction(_("Cash Out (F7)"), self, shortcut="F7",  triggered=self.cashOut )
        self.cashAvailableAction = QtGui.QAction(_("Cash Available (F6)"), self, shortcut="F6",  triggered=self.cashAvailable )
        self.endOfDayAction = QtGui.QAction(_("End Of Day (Ctrl+W)"), self, shortcut="Ctrl+W",  triggered=self.endOfDay ) #FIXME: QKeySequence::Close
        self.lockScreenAction = QtGui.QAction(_("Lock Screen (Ctrl+Space)"), self, shortcut="Ctrl+Space",  triggered=self.lockScreen ) #FIXME: Qt::CTRL+Qt::Key_Space
        self.suspendSaleAction = QtGui.QAction(_("Suspend Sale (Ctrl+Backspace)"), self, shortcut="Ctrl+Backspace",  triggered=self.suspendSale ) #FIXME: Qt::CTRL+Qt::Key_Backspace
        self.discountAction = QtGui.QAction(_("Apply Discount (Ctrl+D)"), self, shortcut="Ctrl+D",  triggered=self.applyDiscount )
        self.resumeSaleAction = QtGui.QAction(_("Resume Sale (Ctrl+R)"), self, shortcut="Ctrl+R",  triggered=self.resumeSale )
        self.currencyConversionAction = QtGui.QAction(_("Currency Conversion"), self,  triggered=self.showCurrencyConv )
        self.configAction = QtGui.QAction(_("Configure Lemon"), self,  triggered=self.config )
        

        self.exitAction.setIcon(QtGui.QIcon(":/icons/images/lemon-exit.png"))
        self.aboutAction.setIcon(QtGui.QIcon(":/icons/images/lemon-tag.png"))
        self.showPaymentOptionsAction.setIcon(QtGui.QIcon(":/icons/images/card.png"))
        self.loginAction.setIcon(QtGui.QIcon(":/icons/images/lemon-user.png"))
        self.balanceAction.setIcon(QtGui.QIcon(":/icons/images/lemon-balance.png"))
        self.codeFocusAction.setIcon(QtGui.QIcon(":/icons/images/lemon-barcode.png"))
        self.searchAction.setIcon(QtGui.QIcon(":/icons/images/lemon-search.png"))
        self.removeItemAction.setIcon(QtGui.QIcon(":/icons/images/lemon-eraser.png"))
        self.finishTransactionAction.setIcon(QtGui.QIcon(":/icons/images/lemon-transaction-accept.png"))
        self.cancelTransactionAction.setIcon(QtGui.QIcon(":/icons/images/lemon-transaction-cancel.png"))
        self.cancelTicketAction.setIcon(QtGui.QIcon(":/icons/images/lemon-ticket-cancel.png"))
        self.startOperationsAction.setIcon(QtGui.QIcon(":/icons/images/lemon-start.png"))
        self.goPayAction.setIcon(QtGui.QIcon(":/icons/images/lemon-pay.png"))
        self.priceCheckerAction.setIcon(QtGui.QIcon(":/icons/images/lemon-price-checker.png"))
        self.reprintTicketAction.setIcon(QtGui.QIcon(":/icons/images/lemon-print-ticket.png"))
        self.cashInAction.setIcon(QtGui.QIcon(":/icons/images/lemon-cashin.png"))
        self.cashOutAction.setIcon(QtGui.QIcon(":/icons/images/lemon-cashout.png"))
        self.cashAvailableAction.setIcon(QtGui.QIcon(":/icons/images/lemon-money.png"))
        self.endOfDayAction.setIcon(QtGui.QIcon(":/icons/images/lemon-calendar-small.png"))
        self.lockScreenAction.setIcon(QtGui.QIcon(":/icons/images/lemon-lock-screen.png"))
        self.suspendSaleAction.setIcon(QtGui.QIcon(":/icons/images/lemon-inbox.png"))
        self.discountAction.setIcon(QtGui.QIcon(":/icons/images/lemon-discount.png"))
        self.resumeSaleAction.setIcon(QtGui.QIcon(":/icons/images/lemon-outbox.png"))
        self.currencyConversionAction.setIcon(QtGui.QIcon(":/icons/images/lemon-currency.png"))
        self.configAction.setIcon(QtGui.QIcon(":/icons/images/lemon-configure.png"))


    def createToolBars(self):
        #Adding the left toolbar. non-movable.
        self.toolBarLeft  = QtGui.QToolBar("Left Toolbar")
        self.toolBarLeft.setMovable(False)
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolBarLeft)
        self.toolBarLeft.addAction(self.aboutAction)
        self.toolBarLeft.addAction(self.loginAction)
        self.toolBarLeft.addAction(self.startOperationsAction)
        self.toolBarLeft.addAction(self.balanceAction)
        self.toolBarLeft.addAction(self.endOfDayAction)
        self.toolBarLeft.addAction(self.lockScreenAction)
        self.toolBarLeft.addAction(self.suspendSaleAction)
        self.toolBarLeft.addAction(self.resumeSaleAction)
        self.toolBarLeft.addAction(self.configAction)
        self.toolBarLeft.addAction(self.exitAction)
        #NOTE: Why the shortcuts dont work if the actions are not visible in the ui via a toolbar or menubar?

        #Adding the top toolbar, non-movable for some important actions. This toolbar is not on the toolbarArea, it is aside the code input box.
        self.toolBarTop = QtGui.QToolBar("Top Toolbar", self.toolWidget)
        self.toolBarTop.setMovable(False)
        self.toolBarTop.addAction(self.codeFocusAction)
        self.toolBarTop.addAction(self.removeItemAction)
        self.toolBarTop.addAction(self.goPayAction)
        self.toolBarTop.addAction(self.discountAction)
        self.toolBarTop.addAction(self.finishTransactionAction)
        self.toolBarTop.addAction(self.cancelTransactionAction)
        self.toolBarTop.addAction(self.cancelTicketAction)
        self.toolBarTop.addAction(self.reprintTicketAction)
        self.toolBarTop.addAction(self.cashInAction)
        self.toolBarTop.addAction(self.cashOutAction)
        self.toolBarTop.addAction(self.cashAvailableAction)
        self.toolBarTop.addAction(self.priceCheckerAction)
        
        self.toolWidgetLayout.addWidget(self.toolBarTop)

        #Adding the tendered widget toolbar.
        self.tenderedToolBar = QtGui.QToolBar("Tendered Toolbar", self.tenderedWidget)
        self.tenderedToolBar.setMovable(False)
        self.tenderedToolBar.addAction(self.showPaymentOptionsAction)
        self.tenderedToolBar.addAction(self.currencyConversionAction)
        self.tenderedWidgetLayout.addWidget(self.tenderedToolBar)

        self.toolBarTop.setIconSize(QtCore.QSize(32,32))
        self.toolBarLeft.setIconSize(QtCore.QSize(32,32))


    ########################## METHODS ###########################

    def setupSalesWidget(self):
        tableSize = self.tableSale.size()
        piece = tableSize.width()/10
        self.tableSale.horizontalHeader().setResizeMode(QtGui.QHeaderView.Interactive)
        self.tableSale.horizontalHeader().resizeSection(0, piece/2)
        self.tableSale.horizontalHeader().resizeSection(1, piece*5*0.98)
        self.tableSale.horizontalHeader().resizeSection(2, piece*1.5)
        self.tableSale.horizontalHeader().resizeSection(3, piece*1.5)
        self.tableSale.horizontalHeader().resizeSection(4, piece*1.5)

    
    def showPaymentOptions(self):
        #Not coded yet...
        pass

    def login(self):
        self.loginWindow.showDialog()
    
    def balance(self):
        pass
    
    def showSearch(self):
        pass
    
    def removeSelectedItem(self):
        pass
    
    def finishTransaction(self):
        pass
    
    def cancelTransaction(self):
        pass
    
    def cancelTicket(self):
        pass
    
    def startOperations(self):
        pass
    
    def showPriceChecker(self):
        pass
    
    def reprintTicket(self):
        pass
    
    def cashIn(self):
        pass
    
    def cashOut(self):
        pass
    
    def cashAvailable(self):
        pass
    
    def endOfDay(self):
        pass

    def lockScreen(self):
        #first disable the actions and ui.
        self.disableActions()
        self.disableUi()
        self.lockDialog.showDialog(_("<b>This terminal is locked.</b> <br><i>Please enter the user's password to unlock it</i>."))
        #now update balance and transaction.
        #self.updateTransaction() #FIXME: I think this is not ui related, so it must be out of this class!

    def unlockScreen(self):
        if self.authenticateUser( self.loggedUser, self.lockDialog.getPassword(), False ):
            self.enableUi()
            self.enableActions()
            self.lockDialog.hideDialog()
            self.editItemCode.setFocus()
        else:
            self.lockDialog.shake()

    def suspendSale(self):
        pass

    def applyDiscount(self):
        pass

    def resumeSale(self):
        pass

    def showCurrencyConv(self):
        pass

    def config(self):
        pass

    def toogleActions(self, status):
        self.exitAction.setEnabled(status)
        self.aboutAction.setEnabled(status)
        self.showPaymentOptionsAction.setEnabled(status)
        self.loginAction.setEnabled(status)
        self.balanceAction.setEnabled(status)
        self.codeFocusAction.setEnabled(status)
        self.searchAction.setEnabled(status)
        self.removeItemAction.setEnabled(status)
        self.finishTransactionAction.setEnabled(status)
        self.cancelTransactionAction.setEnabled(status)
        self.cancelTicketAction.setEnabled(status)
        self.startOperationsAction.setEnabled(status)
        self.goPayAction.setEnabled(status)
        self.priceCheckerAction.setEnabled(status)
        self.reprintTicketAction.setEnabled(status)
        self.cashInAction.setEnabled(status)
        self.cashOutAction.setEnabled(status)
        self.cashAvailableAction.setEnabled(status)
        self.endOfDayAction.setEnabled(status)
        self.lockScreenAction.setEnabled(status)
        self.suspendSaleAction.setEnabled(status)
        self.discountAction.setEnabled(status)
        self.resumeSaleAction.setEnabled(status)
        self.currencyConversionAction.setEnabled(status)
        self.configAction.setEnabled(status)
        

    def disableUi(self):
        self.mainWidget.setEnabled(False)

    def enableUi(self):
        self.mainWidget.setEnabled(True)

    def enableActions(self):
        self.toogleActions(True)

    def disableActions(self):
        self.toogleActions(False)

    def updateClock(self):
        time = QtCore.QTime.currentTime()
        timeString = time.toString("hh:mm")
        if time.second() % 2 == 0:
            timeString = timeString.replace(':', '.')
        else:
            timeString = timeString.replace('.',':')

        self.lblStatusTime.setText(timeString)
        
        if time.hour() == 0 and time.minute() == 0 and (time.second() == 0 or time.second() == 1 ):
            updateDate()


    def updateDate(self):
        date = QtCore.QDate.currentDate()
        dateString = date.toString("dddd MMM d")
        self.lblStatusDate.setText(dateString)


    def doAuth(self):
        if self.authenticateUser(self.loginWindow.getUserName(), self.loginWindow.getPassword(), True ):
            self.loginWindow.hideDialog()
            display = '%s %s (%s)'%(self.loggedUser.first_name, self.loggedUser.last_name, self.loggedUser.username)
            self.lblStatusCashier.setText(display)
        else:
            self.loginWindow.shake()
            

    def authenticateUser(self, user, passwd, cleanUser):
        user = authenticate(username=user, password=passwd)
        if user is not None and user.is_active and (user.is_staff or user.is_superuser):
            self.loggedUser = user
            return True
        else:
            if cleanUser:
                self.loggedUser = None
            return False


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
