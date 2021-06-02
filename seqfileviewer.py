import sys
import os
import re
from PySide import QtGui, QtCore

# File browser widget with list view that collapses image sequences to a single file format and shows expanded list on button click

# main window class
class MainWindow(QtGui.QMainWindow):

    # Set window title, root path and list of image formats here
    ROOT_PATH = "/Users/abhishekravi/Desktop"
    WINDOW_TITLE = 'Sequence Selector'
    FORMAT_LIST = {'jpg', 'png', 'tif', 'exr'}

    # window initialization
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.resize(800, 600)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.createUI()
        self.connectUI()

    # Create window UI
    def createUI(self):

        self.browserLabel = QtGui.QLabel()
        self.browserLabel.setText("Browser")
        self.browserLabel.setFixedHeight(20)

        self.listLabel = QtGui.QLabel()
        self.listLabel.setText("List of Files")
        self.listLabel.setFixedHeight(20)

        # Main widget
        self.fileBrowserWidget = QtGui.QWidget(self)
        self.setCentralWidget(self.fileBrowserWidget)
        self.dirmodel = QtGui.QFileSystemModel()
        self.dirmodel.setRootPath(self.ROOT_PATH)

        # Filter to display only folders and not files
        self.dirmodel.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllDirs)
        self.folderView = QtGui.QTreeView()
        self.folderView.setModel(self.dirmodel)
        self.folderView.setRootIndex(self.dirmodel.index(self.ROOT_PATH))

        # Hiding header and columns for size, file type, and last modified
        self.folderView.setHeaderHidden(True)
        self.folderView.hideColumn(1)
        self.folderView.hideColumn(2)
        self.folderView.hideColumn(3)

        # List widget for files
        self.selectionModel = self.folderView.selectionModel()
        self.filemodel = QtGui.QFileSystemModel()
        self.fileView = QtGui.QListWidget()

        # Enable multi selection
        self.fileView.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        # Button for displaying full file sequence list
        self.expandButton = QtGui.QPushButton("Display All Files")
        self.expandButton.setMinimumSize(400, 22)

        # Adding splitter between both views
        splitter_filebrowser = QtGui.QSplitter()
        splitter_filebrowser.addWidget(self.folderView)
        splitter_filebrowser.addWidget(self.fileView)

        # Setting Layout for widgets
        vertLayout = QtGui.QVBoxLayout()
        topBox = QtGui.QHBoxLayout()
        bottomBox = QtGui.QHBoxLayout()

        vertLayout.setContentsMargins(0, 0, 0, 0)
        topBox.setContentsMargins(0, 0, 0, 0)
        bottomBox.setContentsMargins(0, 0, 0, 0)

        topBox.addWidget(self.browserLabel)
        topBox.addWidget(self.listLabel)

        vertLayout.addLayout(topBox)
        vertLayout.addWidget(splitter_filebrowser)

        bottomBox.addStretch(1)
        bottomBox.addWidget(self.expandButton)
        vertLayout.addLayout(bottomBox)
        self.fileBrowserWidget.setLayout(vertLayout)

    # Connect browser click and button functions
    def connectUI(self):
        self.folderView.clicked[QtCore.QModelIndex].connect(self.folderOnClick)
        self.expandButton.clicked.connect(self.expandSequenceSelection)

    # Returns index of current folder selection

    def getCurrentIndex(self):
        currentIndex = self.selectionModel.currentIndex()
        return currentIndex

    # Returns path of current folder selection
    def getCurrentPath(self):
        currentPath = self.dirmodel.filePath(self.getCurrentIndex())
        return currentPath

    # Checks if file is part of an image sequence by checking list of extensions and text format
    def isSequence(self, file):

        return re.match("^(.+?)([0-9]+)\.(.{3,4})$", file)
        #fileParts = file.split(".")
        #length = len(fileParts)

        # if (fileParts[length - 1] in self.FORMAT_LIST and length > 2):
        # return True

    # Called on clicking folder in folder view
    def folderOnClick(self, index):
        currentPath = self.getCurrentPath()
        self.filemodel.setRootPath(currentPath)
        self.fileView.setRootIndex(self.filemodel.index(currentPath))
        self.populateList(currentPath)

    # Populates list of files for file view including collapsed image sequence entries
    def populateList(self, currentPath):
        self.fileView.clear()
        fileList = list(set(os.listdir(currentPath)) - set(self.returnSequenceFiles(currentPath)))

        for file in self.createSequenceDictionary(currentPath):
            fileList.append(file)
        for file in fileList:
            self.fileView.addItem(file)

    # Returns list of all image sequence files in given folder path
    def returnSequenceFiles(self, currentPath):
        sequenceList = []

        for file in sorted(os.listdir(currentPath)):
            if (self.isSequence(file)):
                sequenceList.append(file)
        return sequenceList

    # Creates dictionary of image sequences with filename as key and list of sequence info as value\
    def createSequenceDictionary(self, currentPath):
        sequenceDict = {}
        counter = 0
        root = ''
        filename = ''

        for file in sorted(os.listdir(currentPath)):

            # Extracting filename, index, and extension using regular expressions
            match = self.isSequence(file)
            if match:
                splitList = match.groups()
                filename = splitList[0][:-1]
                index = splitList[1]
                extension = splitList[2]
                padding = len(index)

                if not filename in sequenceDict:
                    sequenceDict[filename] = {
                        'ext': extension,
                        'startIndex': int(index),
                        'endIndex': int(index),
                        'padding': padding}

                sequenceDict[filename]['endIndex'] = int(index)
                filename = ''

        # Calling function to convert dictionary to collapsed file format
        return self.returnCollapsedSequence(sequenceDict)

    # Accepts image sequence dictionary as parameter and returns collapsed image sequence format for display in list view
    def returnCollapsedSequence(self, sequenceDict):
        outputString = ''
        for key, seqInfo in sequenceDict.items():

            if seqInfo['startIndex'] == seqInfo['endIndex']:
                outputString += '{}.{}.{}\n'.format(key, seqInfo['startIndex'], seqInfo['ext'])
                continue

            outputString += '{}.%{}d.{} {}-{}\n'.format(key, str(seqInfo['padding']).zfill(2), seqInfo['ext'], seqInfo['startIndex'], seqInfo['endIndex'])
        return outputString.split("\n")

    # Checks for image sequences in selection from list view and displays full sequences in message box
    def expandSequenceSelection(self):
        sequenceList = []
        sequenceText = ''
        currentPath = self.getCurrentPath()
        msgBox = QtGui.QMessageBox()
        selection = self.fileView.selectedItems()
        if not selection:
            sequenceText = 'No files selected'
        for item in selection:
            for file in os.listdir(currentPath):
                s1 = item.text()
                s2 = str(file)
                if s1.split(".")[0] == s2.split(".")[0]:
                    sequenceList.append(s2)

        for file in sorted(sequenceList):
            sequenceText += file
            sequenceText += '\n'
        msgBox.setText(sequenceText)
        msgBox.exec_()


# Launch main window
app = QtGui.QApplication(sys.argv)
main = MainWindow()
main.show()

sys.exit(app.exec_())
