from PySide6.QtWidgets import QPushButton, QWidget, QMessageBox, QMainWindow, QProgressDialog, QHBoxLayout
from PySide6.QtCore import QThread, Slot, Qt, QEvent, QThreadPool
from PySide6.QtGui import QAction, QIcon
from yolo import *
from graphs import *
from memory import *
import visualizadorArquivos
import pontesManager
from sys import exit
from os import path
from filtroResultados import FiltroResultados
from listarResultados import ListaResultados
from media_player_pyside6 import MediaPlayer
from osFilePicker import OSFilePicker
#from settings import SettingsMenu

basedir = path.dirname(__file__)

class MainWindow(QMainWindow):
    mainWindow = None
    def __init__(self, parent = None, debug=False):
        global mainWindow, settings
        super(MainWindow, self).__init__(parent)
        print(debug)
        #settings = SettingsMenu() To be implemented
        self.janela_resultados = None
        self.setWindowTitle("Aplicativo Bugios")
        if debug:
            print(basedir)
        self.setWindowIcon(QIcon(path.join(basedir, 'resources/icons/icon.png')))
        self.setGeometry(0,0,1440,900)
        mainWindow = self
        self.setCentralWidget(MainWidget())
        menu_bar = self.menuBar()
        # File menu
        file_menu = menu_bar.addMenu("File")
        pontes_menu = menu_bar.addMenu("Bridges")
        results_menu = menu_bar.addMenu("Results")
        #settings_menu = menu_bar.addMenu("Config")
        # Add actions to file menu
        quit_action = QAction("Exit", self)
        pontes_action = QAction("Register", self)
        results_lista_menu_action = QAction("List",self)
        results_menu_action = QAction("Filter",self)
        #instructions_menu_action = QAction("Settings",self)

        file_menu.addAction(quit_action)
        pontes_menu.addAction(pontes_action)
        results_menu.addAction(results_lista_menu_action)
        results_menu.addAction(results_menu_action)
        #settings_menu.addAction(instructions_menu_action)
        
        results_lista_menu_action.triggered.connect(self.mostrar_lista_resultados)
        results_menu_action.triggered.connect(self.mostrar_filtro_resultados)
        pontes_action.triggered.connect(self.mostrar_pontes)
        quit_action.triggered.connect(exit)
        #instructions_menu_action.triggered.connect(self.mostrar_config)

    def mostrar_filtro_resultados(self):
        self.janela_resultados = FiltroResultados()
        self.janela_resultados.show()
        
    def mostrar_lista_resultados(self):
        self.janela_lista = ListaResultados()
        self.janela_lista.show()
        
    def mostrar_pontes(self):
        self.janela_pontes = pontesManager.PonteJanela()
        self.janela_pontes.show()
        
    #def mostrar_config(self):
    #    settings.show()
        
    def closeEvent(self, event):
        try:
            self.janela_resultados.close()
        except:
            pass
        try:
            self.janela_lista.close()
        except:
            pass
        try:
            self.janela_pontes.close()
        except:
            pass
        try:
            self.centralWidget().yolo_thread.quit()
        except:
            pass
        try:
            self.centralWidget().model.progress.close()
        except:
            pass
        try:
            self.janela_config.close()
        except:
            pass
        return super().closeEvent(event)

class MainWidget(QWidget):
    cancel_event_code = QEvent.registerEventType()
    progress_canceled = QEvent(QEvent.Type.User)
    
    def __init__(self, parent = None):
        super(MainWidget, self).__init__(parent)
        self.model = None
        self.fileSystemView = visualizadorArquivos.FileSystemManager().instance()
        self.fileSystemView.setParent(self)
        self.button = QPushButton("Run on selected file")
        self.button.clicked.connect(self.rodarModeloBuiltIn)

        self.osFilePicker = OSFilePicker()
        self.osFilePicker.signal[int].connect(self.rodarModeloFilePicker)
        self.osFilePicker.signal[list].connect(self.rodarModeloFilePicker)
        
        # Temporários
        self.graph = Graph()
        self.graph.setParent(self)

        self.videoPlayer = MediaPlayer(self)

        #self.layout = QHBoxLayout()
 
        #self.layout.addWidget(QLabel("Selecione um arquivo ou pasta aqui:"), 0, 0, 1, 4)
        #self.layout.addWidget(self.fileSystemView, 1, 0, 6, 4)
        #self.layout.addWidget(self.button, 7, 0, 1, 4)
        label = QLabel("------------------------------------------------ OR ------------------------------------------------")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #self.layout.addWidget(label, 8, 0, 1, 4)
        #self.layout.addWidget(self.osFilePicker, 9, 0, 1, 4)
        #self.layout.addWidget(self.graph.graph(), 6, 4, 4, 6)
        #self.layout.addWidget(self.videoPlayer, 0, 4, 6, 6)
        
        self.layout = QHBoxLayout()
        sublayout1 = QVBoxLayout()
        sublayout2 = QVBoxLayout()
 
        sublayout1.addWidget(QLabel("Select a file or folder here:"))
        sublayout1.addWidget(self.fileSystemView)
        sublayout1.addWidget(self.button)
        sublayout1.addWidget(label)
        sublayout1.addWidget(self.osFilePicker)
        sublayout2.addWidget(self.videoPlayer)
        sublayout2.addWidget(self.graph.graph())
        self.layout.addLayout(sublayout1)
        self.layout.addLayout(sublayout2)
                
        #for i in range(self.layout.rowCount()):
        #    self.layout.setColumnMinimumWidth(i, 0)
        #    self.layout.setRowMinimumHeight(i, 0)
        #    if i < 5:
        #        self.layout.setColumnStretch(i,1)
        
        self.setLayout(self.layout)
        
    @Slot(list)
    def printOutput(self, data):
        if data[0] == False:
            to_show = data[1]
            self.graph.set_data(data[1])
        else:
            to_show = memory.fetch(data[1])
            self.graph.set_data(to_show)
        file = self.model.getFile()
        if file.lower().endswith(('.mp4','.avi')):
            self.videoPlayer.open_file(file)
            1
        self.videoPlayer.bounding_boxes.setBoundingBoxes(to_show[-2])
                
    def rodarModelo(self, videos):
        if self.model != None:
            mes = QMessageBox(self)
            mes.setWindowTitle("Aviso")
            mes.setText("Espere um pouco antes de rodar o modelo novamente")
            mes.setIcon(QMessageBox.Warning)
            mes.exec()
            return
        
        if isinstance(videos,list):
            if videos == []:
                mes = QMessageBox(self)
                mes.setWindowTitle("Aviso")
                mes.setText("Essa pasta não possui nenhum vídeo")
                mes.setIcon(QMessageBox.Warning)
                mes.exec()
                return
            else:
                mes = QMessageBox(self)
                mes.setWindowTitle("Aviso")
                text = str(len(videos)) + (" vídeos foram selecionados" if len(videos) > 1 else " video foi selecionado") + ", deseja rodar o modelo em todos os vídeos?"
                mes.setText(text)
                sim = QPushButton(text="Sim")
                nao = QPushButton(text="Não")
                mes.addButton(sim,QMessageBox.ButtonRole.YesRole)
                mes.addButton(nao,QMessageBox.ButtonRole.NoRole)
                mes.setDefaultButton(nao)
                mes.setIcon(QMessageBox.Question)
                mes.exec()
                if mes.clickedButton() == sim:
                    file = videos
                    if len(pontesManager.pontes()) == 0:
                        QMessageBox.warning(self,"Aviso","Nenhuma ponte cadastrada, use o botão \"Pontes\" para adicionar pontes.")
                        return
                    pontes = pontesManager.PonteDialog(self)
                    if pontes.exec():
                        ponte_escolhida = pontes.retrieve()
                    else:
                        return
                    
                else:
                    return
        else:
            file = videos
            if not memory.inResults(file):   
                if len(pontesManager.pontes()) == 0:
                    QMessageBox.warning(self,"Aviso","Nenhuma ponte cadastrada, use o botão \"Pontes\" para adicionar pontes.")
                    return
                pontes = pontesManager.PonteDialog(self)
                if pontes.exec():
                    ponte_escolhida = pontes.retrieve()
                else:
                    return
            else:
                ponte_escolhida = ""
        
        if isinstance(videos,list):
            self.progress = QProgressDialog("", "Cancelar", 0, len(videos)*750, mainWindow.mainWindow)

        else:
            self.progress = QProgressDialog("", "Cancelar", 0, 750, mainWindow.mainWindow)
        
        #self.threadpool = QThreadPool(maxThreadCount=settings.getThreads()) TO be implemented
        self.yolo_thread = QThread()
        self.model = YoloModel(basedir,self.progress)
        self.model.moveToThread(self.yolo_thread)
        self.yolo_thread.started.connect(self.model.run)
        self.model.finished.connect(self.yolo_thread.quit)
        self.model.finished.connect(self.clear_model)
        self.model.finished.connect(self.model.deleteLater)
        self.yolo_thread.finished.connect(self.yolo_thread.deleteLater)
        self.model.output.connect(self.printOutput)
        self.model.signal_reset.connect(self.progress_reset)
        self.model.signal_update.connect(self.progress_update)
        self.model.signal_set_max.connect(self.progress_set_max)
        self.graph.change_video_frame.connect(self.videoPlayer.set_position)
        
        self.progress.setAutoClose(True)
        self.progress.setAutoReset(False)
        self.progress.setWindowModality(Qt.WindowModal)
        self.progress.setWindowTitle("Modelo")
        self.progress.setValue(0)
        self.model.setFile(file)
        self.model.setPonte(ponte_escolhida)
        self.yolo_thread.start()
        
        if self.model.cudaFlag:
            self.progress.setLabelText("Rodando Inferência na GPU...")
        else:
            self.progress.setLabelText("Rodando Inferência na CPU...")

    @Slot(int)
    @Slot(list)
    def rodarModeloFilePicker(self,arg):
        print("Chegou aqui")
        print(arg, type(arg))
        if isinstance(arg,int):
            1   # Pop up dizendo que não teve vídeos
        elif isinstance(arg,list):
            self.rodarModelo(arg)
        else:
            # Algo deu MUITO errado
            raise Exception("Tipo do parâmetro da funçaõ rodarModeloFilePicker incompatível (de alguma forma)")

    @Slot()
    def rodarModeloBuiltIn(self):
        file = self.fileSystemView.getCurrentFilePath()
        fileIdx = self.fileSystemView.getCurrentIndex()
        if self.fileSystemView.fileSystemView.isDir(fileIdx):
            videos = self.fileSystemView.grabVideosFromFolder(fileIdx)
            self.rodarModelo(videos)
        else:
            self.rodarModelo(file)
        
            
    @Slot()
    def clear_model(self):
        self.model = None
        
    @Slot()
    def progress_reset(self):
        self.progress.reset()

    @Slot(int, bool)
    def progress_update(self,value,use_current):
        if use_current:
            self.progress.setValue(self.progress.value()+value)
        else:
            self.progress.setValue(value)
        
    @Slot(int, bool)
    def progress_set_max(self,value,use_current):
        if use_current:
            self.progress.setMaximum(self.progress.maximum()+value)
        else:
            self.progress.setMaximum(value)
        
        
    def closeEvent(self, event):
        self.yolo_thread.quit()
        memory.clear_temp_dir()
        self.model.progress.close()
        return super().closeEvent(event)
        
        
