from tkinter.filedialog import askopenfilenames, askdirectory
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal
import os

class OSFilePicker(QWidget):
    
    signal = Signal((int,), (list,))
    # -1 => pasta vazia
    
    def __init__(self):
        super().__init__()
        
        buttonFile = QPushButton("Select Videos", self)
        buttonFolder = QPushButton("Select a Folder", self)
        
        buttonFile.clicked.connect(self.requestFile)
        buttonFolder.clicked.connect(self.requestFolder)
        
        layout = QHBoxLayout()
        layout.addWidget(buttonFile)
        layout.addSpacing(1)
        layout.addWidget(buttonFolder)
        self.setLayout(layout)
        
    def requestFile(self):
        result = askopenfilenames(
            filetypes=
                [
                    ('Video Files','*.mp4 *.avi *.asf *.gif *.m4v *.mkv *.mov *.mpeg *.mpg *.ts *.wmv *.webm')
                ]
            )
        print(result)
        if result == '':
            self.signal[int].emit(-1)
        print([i for i in result])
        self.signal[list].emit([i for i in result])
        

    def requestFolder(self):
        result = askdirectory()
        print(result)
        if result == "":
            self.signal[int].emit(-1)
        else:
            videos = []
            try:
                for f in os.listdir(result):
                    if f.lower().endswith(('.mp4','.avi','.asf','.gif','.m4v','.mkv','.mov','.mpeg','.mpg','.ts','.wmv','.webm')):
                        videos.append(result+"/"+f)
                self.signal[list].emit(videos)
            except Exception as e:
                print("Algo deu ruim:",e)
                