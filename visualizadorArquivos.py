from PySide6.QtWidgets import QTreeView, QFileSystemModel, QGridLayout, QWidget, QHeaderView
from PySide6.QtCore import QDir
import os

class FileSystemManager(QWidget):
    fileSystemManager = None
    def __init__(self):
        super().__init__()
        self.fileSystemView = QFileSystemModel()
        self.fileSystemView.setOption(QFileSystemModel.Option.DontUseCustomDirectoryIcons,True)
        self.fileSystemView.setRootPath(QDir.currentPath())
        self.tree = QTreeView()
        self.tree.setUniformRowHeights(True)
        self.tree.setModel(self.fileSystemView)
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.layout = QGridLayout()
        self.layout.addWidget(self.tree)
        self.setLayout(self.layout)
        
    def getCurrentIndex(self):
        return self.tree.currentIndex()
    
    def getCurrentFilePath(self):
        return self.fileSystemView.filePath(self.tree.currentIndex())
        
    def instance(self):
        if self.fileSystemManager == None:
            self.fileSystemManager = FileSystemManager()
        return self.fileSystemManager
    
    def grabVideosFromFolder(self,folder):
        videos = []
        folder = self.fileSystemView.filePath(folder)
        for path in os.listdir(folder):
            if path.lower().endswith(('.mp4','.avi','.asf','.gif','.m4v','.mkv','.mov','.mpeg','.mpg','.ts','.wmv','.webm')):
                videos.append(folder+"/"+path)
        return videos
        

#fileSystemManager = FileSystemManager()