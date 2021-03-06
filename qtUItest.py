#!/usr/bin/python
# -----------------------------------------------------------------------------
# Name:        XAqtUItest.py
#
# Purpose:     This module is used to test the Qt ui widgets.
#
# Author:      Yuancheng Liu
#
# Created:     2019/03/27
# Copyright:   YC
# License:     YC
# -----------------------------------------------------------------------------

import sys
from collections.abc import Iterable

# import QT UI lib
from PyQt5.QtCore import (Qt, QObject, QDate, QTime, QDateTime,
                          QBasicTimer, QDate, QMimeData, pyqtSignal)

from PyQt5.QtWidgets import(
    # Qt main widget:
    QApplication, QMainWindow, QWidget, QDesktopWidget, QFrame,
    # Qt Layout:
    QHBoxLayout, QVBoxLayout, QGridLayout, QSplitter,
    # Qt components:
    QToolTip, QPushButton, QMessageBox, QMenu, QAction, QLabel, QComboBox,
    QLCDNumber, QSlider, QLineEdit, QCheckBox, QProgressBar, QCalendarWidget,
    # Qt dialogs:
    QInputDialog, QColorDialog, QFontDialog, QFileDialog,
    qApp)

from PyQt5.QtGui import (QIcon, QFont, QPixmap, QDrag)

nowStr = QDate.currentDate()
dateTimeStr = QDateTime.currentDateTime()
timeStr = QTime.currentTime()

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


class Communicate(QObject):
    """ function used to emit contorl. 
    """
    closeApp = pyqtSignal()

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


class popUpwindow(QWidget):
    """ Create a pop-up window. 
    """

    def __init__(self):
        super().__init__()
        self.initUI()
    # -----------------------------------------------------------------------------

    def initUI(self):
        self.lbl = QLabel(self)
        qle = QLineEdit(self)
        qle.move(60, 100)
        self.lbl.move(60, 40)
        qle.textChanged[str].connect(self.onChanged)
        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('QLineEdit')
        self.show()
    # -----------------------------------------------------------------------------
    def onChanged(self, text):

        self.lbl.setText(text)
        self.lbl.adjustSize()

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


class dragButton(QPushButton):
    """ A button can be dragged to a new position by holding mouse right button. 
    """

    def __init__(self, title, parent):
        super().__init__(title, parent)

    # -----------------------------------------------------------------------------
    def mouseMoveEvent(self, e):
        if e.buttons() != Qt.RightButton:
            return
        print("move mv in action")
        mineData = QMimeData()
        drag = QDrag(self)
        drag.setMimeData(mineData)
        drag.setHotSpot(e.pos() - self.rect().topLeft())
        drag.exec_(Qt.MoveAction)

    # -----------------------------------------------------------------------------
    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        if e.button() == Qt.LeftButton:
            print("button pressed")

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


class dropButton(QPushButton):
    """ A button user can drop text to replace the button's orignal text.
    """

    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.setAcceptDrops(True)
    # -----------------------------------------------------------------------------

    def dragEnterEvent(self, e):
        if e.mimeData().hasFormat('text/plain'):
            e.accept()
        else:
            e.ignore()
    # -----------------------------------------------------------------------------

    def dropEvent(self, e):
        self.setText(e.mimeData().text())

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


class TestUI(QMainWindow):
    """ Test UI used to test the QT function. 
    """

    def __init__(self):
        super().__init__()
        self.initUI()

    # -----------------------------------------------------------------------------
    def initUI(self):
        self.setTitle()
        self.setGeometry(300, 300, 400, 450)
        self.buildTileArea()
        self.showButtons = False
        # set the tool tips:
        QToolTip.setFont(QFont('SansSerif', 10))
        self.setToolTip("This is a <b> QWidget </b> widget")
        self.bgWidgets = QWidget(self)  # Init the background widget.

        # Set the box layout:
        vbox = QVBoxLayout()
        # Add the line edit used for the title area
        self.le = QLineEdit(self.bgWidgets)
        self.le.textChanged[str].connect(self.lineEditChanged)
        vbox.addWidget(self.le)
        self.lbl = QLabel(
            'Over lay a Q pix map on the label below:', self.bgWidgets)
        vbox.addWidget(self.lbl)
        # Add the QSpliter here:
        self.spliter = QSplitter(Qt.Horizontal)
        self.plbl = QLabel(self.bgWidgets)
        self.plbl.setPixmap(QPixmap('logo.jpg'))
        self.spliter.addWidget(self.plbl)
        # Add the Qframe at the right side.
        self.spliter.addWidget(self.buildDragDropFrame())
        vbox.addWidget(self.spliter)
        # Add the combo box:
        self.combo = QComboBox(self.bgWidgets)
        self.combo.addItem("exit.png")
        self.combo.addItem("icon.jpg")
        self.combo.addItem("logo.jpg")
        self.combo.addItem("open.png")
        self.combo.activated[str].connect(self.onActivated)
        vbox.addWidget(self.combo)
        # Row 1: use GridLayout set the buttons.
        if self.showButtons:
            grid = QGridLayout()
            btLabels = ['clr', 'bck',  ' ',    'close',
                        '7',   '8',    '9',    '/',
                        '4',   '5',    '6',    '*',
                        '1',   '2',    '3',    '-',
                        '0',   '.',    '=',    '+']

            positions = [(i, j) for i in range(5) for j in range(4)]
            for pos, name in zip(positions, btLabels):
                x, y = pos
                button = QPushButton(name)
                grid.addWidget(button, x, y)
            vbox.addLayout(grid)
        else:
            lcd = QLCDNumber(self.bgWidgets)
            vbox.addWidget(lcd)
            sld = QSlider(Qt.Horizontal, self.bgWidgets)
            vbox.addWidget(sld)
            sld.valueChanged.connect(lcd.display)

        # Add the buttons
        self.cb = QCheckBox("Change the window title", self)
        self.cb.setChecked(False)
        self.cb.stateChanged.connect(self.changeTitle)
        vbox.addWidget(self.cb)
        # add the progress bar
        self.pbar = QProgressBar(self.bgWidgets)
        self.pbarStep = 0
        vbox.addWidget(self.pbar)
        self.timer = QBasicTimer() # time used for the progress bar. 
        # add the calendat
        self.cal = QCalendarWidget(self.bgWidgets)
        self.cal.setGridVisible(True)
        self.cal.clicked[QDate].connect(self.showDate)
        vbox.addWidget(self.cal)
        #
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        self.okBtn = QPushButton("OK", self.bgWidgets)
        self.okBtn.clicked.connect(self.buttonClicked)
        hbox.addWidget(self.okBtn)
        self.cancelBtn = QPushButton("Cancel", self.bgWidgets)
        self.cancelBtn.clicked.connect(self.buttonClicked)
        hbox.addWidget(self.cancelBtn)
        self.btn = QPushButton("Close window", self.bgWidgets)
        self.btn.resize(self.btn.sizeHint())
        self.btn.setToolTip("This is a <b> QwidgePushButton</b> widget")
        self.btn.clicked.connect(QApplication.instance().quit)
        hbox.addWidget(self.btn)
        vbox.addLayout(hbox)
        # Set the background widgets.
        self.bgWidgets.setLayout(vbox)
        self.bgWidgets.show()
        self.setCentralWidget(self.bgWidgets)
        # emit event from mouse click event:
        self.comm = Communicate()
        self.comm.closeApp.connect(self.close)
        # Set the main widow status bar.
        self.stateB = self.statusBar()
        self.stateB.showMessage("ready")
        self.setTitle()
        self.setCenter()
        # Set mouse tracking evet
        self.setMouseTracking(True)
        # Show the applicatoin.
        self.show()

    # -----------------------------------------------------------------------------
    def buildTileArea(self):
        """ Build the window title bar. 
        """
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        # Add the file selection menu
        fileAct = QAction(QIcon('open.png'), 'Open', self)
        fileAct.setShortcut('Ctrl+O')
        fileAct.setStatusTip('Pop up file selection dialog.')
        fileAct.triggered.connect(self.popUPfillin)
        fileMenu.addAction(fileAct)
        # Add the exist menu
        exitAct = QAction(QIcon('exit.png'), '&exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip("Exit application")
        exitAct.triggered.connect(qApp.quit)
        fileMenu.addAction(exitAct)
        # Add the import menu:
        impMenu = QMenu('Import', self)
        # Add the import email action.
        impEmAct = QAction('Import email', self)
        impEmAct.triggered.connect(self.popUPfillin)
        impMenu.addAction(impEmAct)
        # Add the import color selection action.
        impCoAct = QAction('Import bgColor', self)
        impCoAct.triggered.connect(self.popUPfillin)
        impMenu.addAction(impCoAct)
        # Add the text format change selection action.
        impFtAct = QAction('Import font', self)
        impFtAct.triggered.connect(self.popUPfillin)
        impMenu.addAction(impFtAct)
        fileMenu.addMenu(impMenu)
        # Add the view bar
        viewAction = QAction('View statusbar', self, checkable=True)
        viewAction.setStatusTip('View statusbar')
        viewAction.setChecked(True)
        viewAction.triggered.connect(self.toggleMenu)
        viewMenu = menubar.addMenu('view')
        mvMenu = QMenu('Move button', self)
        mvAction = QAction('move button', self)
        mvAction.setStatusTip('Move the button to the window center postion')
        mvAction.triggered.connect(self.moveButton)
        mvMenu.addAction(mvAction)
        viewMenu.addMenu(mvMenu)
        viewMenu.addAction(viewAction)
        # Add the tool bar.
        self.toolbar = self.addToolBar('exit')
        self.toolbar.addAction(fileAct)
        self.toolbar.addAction(exitAct)

    # -----------------------------------------------------------------------------
    def buildDragDropFrame(self):
        """ build the from for the drag and drop function test. 
        """
        bgframe = QFrame(self.bgWidgets)
        bgframe.setFrameStyle(QFrame.StyledPanel)
        # put the drag and drop things in the QFrame:
        edit = QLineEdit('', bgframe)
        edit.setDragEnabled(True)
        edit.move(5, 5)

        dbt = dropButton('dropButton', bgframe)
        dbt.move(5, 40)
        self.setAcceptDrops(True)  # active this is very important.

        self.dragBt = dragButton("dragButton", bgframe)
        self.dragBt.move(5, 60)
        return bgframe

    # -----------------------------------------------------------------------------
    def buttonClicked(self):
        sender = self.sender()
        print("Button clicked:"+sender.text())
        if sender.text() == 'OK':
            #popFrame = Example()
            pass

    # -----------------------------------------------------------------------------
    def changeTitle(self, state):
        if state == Qt.Checked:
            self.setWindowTitle("Progress start")
            self.timer.start(100, self)
        else:
            self.setWindowTitle("Progress stop")
            self.timer.stop()
    # -----------------------------------------------------------------------------

    def contextMenuEvent(self, event):
        """ Add the right click pop-up context menu. 
        """
        cmenu = QMenu(self)
        newAct = cmenu.addAction("New")
        openAct = cmenu.addAction("Open")
        quitAct = cmenu.addAction("Close")
        action = cmenu.exec_(self.mapToGlobal(event.pos()))
        # Check the user selection.
        print("user selected the action:" + str(action))
        if action == quitAct:
            qApp.quit()
    # -----------------------------------------------------------------------------
    def dragEnterEvent(self, e):
        e.accept()

    # -----------------------------------------------------------------------------
    def dropEvent(self, e):
        """ Move the dragged button to a ceter position. 
        """
        position = e.pos()
        print("move to position "+repr(position))
        self.dragBt.move(40, 80)
        e.setDropAction(Qt.MoveAction)
        e.accept()
    
    # -----------------------------------------------------------------------------
    def flatten(self, items, ignoreType=(str, bytes)):
        """ This function is used to flatten the nested list. 
        """
        for x in items:
            if isinstance(x, Iterable) and not isinstance(x, ignoreType):
                yield from self.flatten(x, ignoreType)
            else:
                yield x

    # -----------------------------------------------------------------------------
    def keyPressEvent(self, e):
        """ listen the key press event. 
        """
        print("The key you pressed is :"+str(e.key()))
        if e.key() == Qt.Key_Escape:
            self.close()

    # -----------------------------------------------------------------------------
    def lineEditChanged(self, textStr):
        """ listen the line test change: 
        """
        self.lbl.setText(str(textStr))

    # -----------------------------------------------------------------------------
    def mouseMoveEvent(self, e):
        x, y = e.x(), e.y()
        self.stateB.showMessage("x :{0}, y:{1}".format(x, y))

    # -----------------------------------------------------------------------------
    def mousePressEvetn(self, e):
        self.comm.closeApp.emit()

    # -----------------------------------------------------------------------------
    def setCenter(self):
        """ set the window to the center of the screen
        """
        size = self.frameGeometry()
        centerPt = QDesktopWidget().availableGeometry().center()
        size.moveCenter(centerPt)
        self.move(size.topLeft())

    # -----------------------------------------------------------------------------
    def setTitle(self):
        """ Set the title bar of the window.
        """
        self.setWindowTitle("Icon test")
        self.setWindowIcon(QIcon('icon.jpg'))
        self.menubar = self.menuBar()

    # -----------------------------------------------------------------------------
    def toggleMenu(self, state):
        if state:
            self.stateB.show()
        else:
            self.stateB.hide()

    # -----------------------------------------------------------------------------
    def moveButton(self, evet):
        """ Test move the button to the center poition. 
        """
        print("Enter the move button method")
        size = self.frameGeometry()
        #print("this is the qusize"+str(size))
        self.btn.move(100, 100)

    # -----------------------------------------------------------------------------
    def popUPfillin(self, event):
        sender = self.sender()
        print("This is the sender: "+str(sender.text()))
        senderStr = sender.text()
        if senderStr == 'Import email':
            text, ok = QInputDialog.getText(self.bgWidgets, 'Email',
                                            'Enter your email:')
            if ok:
                self.le.setText(str(text))
        elif senderStr == 'Import bgColor':
            col = QColorDialog.getColor()
            if col.isValid():
                self.setStyleSheet(
                    "QWidget { background-color: %s }" % col.name())
        elif senderStr == 'Import font':
            font, ok = QFontDialog.getFont()
            if ok:
                self.lbl.setFont(font)
        else:
            fname = QFileDialog.getOpenFileName(self, 'Open file', 'C:')
            if fname[0]:
                with open(fname[0], 'r') as f:
                    data = f.read()
                    self.le.setText(str(data))

    # -----------------------------------------------------------------------------
    def onActivated(self, text):
        try:
            self.plbl.setPixmap(QPixmap(text))
        except:
            print("The select file is not exit: "+str(text))

    # -----------------------------------------------------------------------------
    def showDate(self, date):
        self.setWindowTitle("Date:"+str(date.toString()))

    # -----------------------------------------------------------------------------
    def timerEvent(self, event):
        if self.pbarStep >= 100:
            self.timer.stop()
            self.setWindowTitle("Progress stop")
            self.pbarStep = 0
            return
        else:
            self.pbarStep += 1
            self.pbar.setValue(self.pbarStep)

    # -----------------------------------------------------------------------------
    def closeEvent(self, event):
        """ pop-up confirm window for user to confirm quit action.
        """
        alert = QMessageBox.question(self, "Quit confirm", "Are u sure you want to quit?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if alert == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = TestUI()
    sys.exit(app.exec_())
