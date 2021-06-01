import sys
import os
from PySide import QtGui, QtCore

# File browser widget with list view that collapses image sequences to a single file format and shows expanded list on button click

# main window class
class MainWindow(QtGui.QMainWindow):

    # Set window title, root path and list of image formats here
    path = "/Users/abhishekravi/Desktop"
    winTitle = 'Sequence Selector'
    formatList = ['jpg', 'png', 'tif', 'exr']

    # window initialization
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.resize(800, 600)
        self.setWindowTitle(self.winTitle)

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
        self.dirmodel.setRootPath(self.path)

        # Filter to display only folders and not files
        self.dirmodel.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllDirs)
        self.folder_view = QtGui.QTreeView()
        self.folder_view.setModel(self.dirmodel)
        self.folder_view.setRootIndex(self.dirmodel.index(self.path))
        self.folder_view.clicked[QtCore.QModelIndex].connect(self.folderClick)

        # Hiding header and columns for size, file type, and last modified
        self.folder_view.setHeaderHidden(True)
        self.folder_view.hideColumn(1)
        self.folder_view.hideColumn(2)
        self.folder_view.hideColumn(3)

        # List widget for files
        self.selectionModel = self.folder_view.selectionModel()
        self.filemodel = QtGui.QFileSystemModel()
        self.file_view = QtGui.QListWidget()

        # Enable multi selection
        self.file_view.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        # Button for displaying full file sequence list
        self.expandButton = QtGui.QPushButton("Display All Files")
        self.expandButton.setMinimumSize(400, 22)
        self.expandButton.clicked.connect(self.expandList)

        # Adding splitter between both views
        splitter_filebrowser = QtGui.QSplitter()
        splitter_filebrowser.addWidget(self.folder_view)
        splitter_filebrowser.addWidget(self.file_view)

        # Setting Layout for widgets
        vBox = QtGui.QVBoxLayout()
        topBox = QtGui.QHBoxLayout()
        bottomBox = QtGui.QHBoxLayout()

        vBox.setContentsMargins(0, 0, 0, 0)
        topBox.setContentsMargins(0, 0, 0, 0)
        bottomBox.setContentsMargins(0, 0, 0, 0)

        topBox.addWidget(self.browserLabel)
        topBox.addWidget(self.listLabel)

        vBox.addLayout(topBox)
        vBox.addWidget(splitter_filebrowser)

        bottomBox.addStretch(1)
        bottomBox.addWidget(self.expandButton)
        vBox.addLayout(bottomBox)
        self.fileBrowserWidget.setLayout(vBox)

    # Returns index of current folder selection

    def get_index(self):
        index = self.selectionModel.currentIndex()
        return index

    # Returns path of current folder selection

    def get_path(self):
        path = self.dirmodel.filePath(self.get_index())
        return path

    # Checks if file is part of an image sequence by checking list of extensions and text format

    def checkSeq(self, file):
        if (file.split(".")[len(file.split(".")) - 1] in self.formatList and file.split(".") > 2):
            return True

    # Called on clicking folder in folder view

    def folderClick(self, index):
        dir_path = self.get_path()
        self.filemodel.setRootPath(dir_path)
        self.file_view.setRootIndex(self.filemodel.index(dir_path))
        self.populateList(dir_path)

    # Populates list of files for file view including collapsed image sequence entries

    def populateList(self, dir_path):
        self.file_view.clear()
        fileList = list(set(os.listdir(dir_path)) - set(self.listSeq(dir_path)))

        for file in self.SortSeq(dir_path):
            fileList.append(file)
        for file in fileList:
            self.file_view.addItem(file)

    # Returns list of all image sequence files in given folder path

    def listSeq(self, dir_path):
        seqList = []

        for file in sorted(os.listdir(dir_path)):
            if (self.checkSeq(file)):
                seqList.append(file)
        return seqList

    # Creates dictionary of image sequences with filename as key and list of sequence info as value

    def SortSeq(self, dir_path):
        seqList = {}
        counter = 0
        root = ''
        filename = ''

        for file in sorted(os.listdir(dir_path)):

            # Extracting filename and checking exception for files with extra "." in the filename
            if (self.checkSeq(file)):
                for x in range(0, len(file.split(".")) - 2):
                    filename += file.split(".")[x]
                    filename += "."
                filename = filename[:-1]

                index = file.split(".")[len(file.split(".")) - 2]
                extension = file.split(".")[len(file.split(".")) - 1]

                if not filename in seqList:
                    seqList[filename] = {
                        'ext': extension,
                        'start_index': int(index),
                        'end_index': int(index), }

                seqList[filename]['end_index'] = int(index)
                filename = ''

        # Calling function to convert dictionary to collapsed file format
        return self.seqFormat(seqList)

    # Accepts image sequence dictionary as parameter and returns collapsed image sequence format for display in list view

    def seqFormat(self, seqList):
        output_string = ''
        for key, seq_info in seqList.items():

            if seq_info['start_index'] == seq_info['end_index']:
                output_string += '{}.{}.{}\n'.format(key, seq_info['start_index'], seq_info['ext'])
                continue

            output_string += '{}.%{}d.{} {}-{}\n'.format(key, str(seq_info['end_index'] + 1).zfill(2), seq_info['ext'], seq_info['start_index'], seq_info['end_index'])
        return output_string.split("\n")

    # Checks for image sequences in selection from list view and displays full sequences in message box

    def expandList(self):
        seqList = []
        seqTxt = ''
        dir_path = self.get_path()
        msgBox = QtGui.QMessageBox()
        selection = self.file_view.selectedItems()
        if not selection:
            seqTxt = 'No files selected'
        for item in selection:
            for file in os.listdir(dir_path):
                s1 = item.text()
                s2 = str(file)
                if s1.split(".")[0] == s2.split(".")[0]:
                    seqList.append(s2)

        for file in sorted(seqList):
            seqTxt += file
            seqTxt += '\n'
        msgBox.setText(seqTxt)
        msgBox.exec_()


# Launch main window
app = QtGui.QApplication(sys.argv)
main = MainWindow()
main.show()

sys.exit(app.exec_())
