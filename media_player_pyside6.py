from PySide6.QtWidgets import  QWidget, QVBoxLayout, QSlider, QPushButton, QGraphicsScene, QHBoxLayout, QGraphicsView, QSizePolicy
from PySide6.QtGui import QIcon, QPixmap, QBrush
from PySide6.QtCore import Qt, QTimer, QSize, Slot, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QMediaMetaData
from PySide6.QtMultimediaWidgets import QGraphicsVideoItem
from desenhaBBoxes import *
import cv2 as cv
from os import path

basedir = path.dirname(__file__)

def extract_fps(filename):
    cap = cv.VideoCapture(filename)
    return int(cap.get(cv.CAP_PROP_FPS))

class MediaPlayer(QWidget):

    def __init__(self, master=None):
        super().__init__(master)
        
        self.setMinimumSize(715,465)
        self.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
    
        self.master = master
        self.flag = True
        self.fps = 25
        self.view = QGraphicsView()
        self.view.setParent(self)
        self.scene = QGraphicsScene()
        self.instance = QGraphicsVideoItem()
        self.instance.setParent(self)
        self.bounding_boxes = QBBoxes(self)
        self.bounding_boxes.setParent(self)
        # hard-coded
        self.bounding_boxes.setGeometry(self.view.geometry().x()+145,self.view.geometry().y()+70,self.view.geometry().width(),self.view.geometry().height()-120)
        self.bounding_boxes.setGeometry(self.view.geometry().x()+28,self.view.geometry().y()+17,self.view.geometry().width()+20,self.view.geometry().height()-110)
                                                                #offset do lado do widget até o vídeo
        self.bounding_boxes.raise_()
        self.media = None

        self.mediaplayer = QMediaPlayer()
        self.mediaplayer.setParent(self)
        self.mediaplayer.setVideoOutput(self.instance)

        self.create_ui()
        self.is_paused = False
        self.mediaplayer.durationChanged.connect(self.update_slider)
    
    def create_ui(self):

        self.positionslider = QSlider(Qt.Orientation.Horizontal, self)
        self.positionslider.setToolTip("Position")
        self.positionslider.setMaximum(1000)
        self.positionslider.valueChanged.connect(self.set_position_slider)

        self.hbuttonbox = QHBoxLayout()
        self.playbutton = QPushButton("Play")
        self.playbutton.setIcon(QIcon(QPixmap(path.join(basedir, 'resources/icons/play.jpg'))))
        self.hbuttonbox.addWidget(self.playbutton)
        self.playbutton.clicked.connect(self.play_pause)

        self.stopbutton = QPushButton("Stop")
        self.hbuttonbox.addWidget(self.stopbutton)
        self.stopbutton.clicked.connect(self.stop)

        self.hbuttonbox.addStretch(1)
        self.hbuttonbox.addSpacing(100)

        self.scene.addItem(self.instance)
        self.scene.setBackgroundBrush(QBrush('black'))
        self.view.setScene(self.scene)

        self.vboxlayout = QVBoxLayout()
        #self.vboxlayout.addWidget(self.instance)
        self.vboxlayout.addWidget(self.view)
        self.vboxlayout.addWidget(self.positionslider)
        self.vboxlayout.addLayout(self.hbuttonbox)

        self.setLayout(self.vboxlayout)
        
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.late_start)
        self.timer.start()
        #self.mediaplayer.audio_set_volume(50)

    def late_start(self):
        geo = self.instance.size()
        self.scene.setSceneRect(self.scene.itemsBoundingRect())

        
        self.view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.OGsize = self.size()
        self.BBOGsize = self.bounding_boxes.geometry()
        self.timer.timeout.disconnect(self.late_start)
        self.timer.stop()
        self.timer.timeout.connect(self.update_ui)


    def play_pause(self):
        if self.mediaplayer.isPlaying():
            self.mediaplayer.pause()
            self.playbutton.setText("Play")
            self.playbutton.setIcon(QIcon(QPixmap(path.join(basedir, 'resources/icons/play.jpg'))))
            self.is_paused = True
            self.timer.stop()
        else:
            if self.mediaplayer.play() == -1:
                return
            self.mediaplayer.play()
            self.playbutton.setText("Pause")
            self.playbutton.setIcon(QIcon(QPixmap(path.join(basedir, 'resources/icons/pause.png'))))
            self.timer.start()
            self.is_paused = False

    def stop(self):
        self.mediaplayer.stop()
        self.playbutton.setText("Play")
        self.playbutton.setIcon(QIcon(QPixmap(
        path.join(basedir, 'resources/icons/play.jpg'))))
        self.set_position_slider(0)

    def open_file(self,filename):

        self.media = QUrl.fromLocalFile(filename)
        self.mediaplayer.setSource(self.media)
        self.positionslider.setMaximum(self.mediaplayer.duration())
        size = self.calculate_size(filename)
        print(size)
        self.instance.setSize(size)
        self.fps = extract_fps(filename)
        try:
            self.fps = extract_fps(filename)
            if self.fps <= 0:
                self.fps = 25
        except:
            print("Exception")
            self.fps = 25

    def calculate_size(self, file):
        temp = cv.VideoCapture(file)
        w = temp.get(cv.CAP_PROP_FRAME_WIDTH)
        h = temp.get(cv.CAP_PROP_FRAME_HEIGHT)
        size = QSize(w,h)
        max_space = self.view.size()
        print("video",size)
        video_ratio = size.width()/size.height()
        print("video ratio",video_ratio)
        player_ratio = max_space.width()/max_space.height()
        if video_ratio == player_ratio:
            new_size = QSize(int(max_space.width()*0.95),int(max_space.height()*0.95))
            self.bounding_boxes.updateSize(size,new_size)
            return new_size
        
        # player é mais largo / vídeo é mais alto
        if player_ratio > video_ratio:
            new_size = QSize(int(max_space.height()*player_ratio*0.95),int(max_space.height()*0.95))   # Altura do player e largura escalada
            self.bounding_boxes.updateSize(size,new_size)
            return new_size
        
        # player é mais alto / vídeo é mais largo
        if video_ratio > player_ratio:
            new_size = QSize(int(max_space.width()*0.95),int(max_space.width()*player_ratio*0.95))   # Altura do player e largura escalada
            self.bounding_boxes.updateSize(size,new_size)
            return new_size
        
    def update_slider(self):
        self.positionslider.setMaximum(self.mediaplayer.duration())
        
    def set_volume(self, volume):
        pass

    @Slot(int)
    def set_position_slider(self, position):
        #postion é entre 0 e 30000
        self.positionslider.valueChanged.disconnect(self.set_position_slider)
        self.positionslider.setValue(position)
        self.mediaplayer.setPosition(position)
        frames = (self.mediaplayer.duration()/1000)*self.fps 
        self.bounding_boxes.set_current_frame(int((position/30000) * frames), None)
        self.positionslider.valueChanged.connect(self.set_position_slider)

    @Slot(list)
    def set_position(self, position):
        #[postion é entre 0 e 1, e na segunda posição 0.0 ou 1.0]
        self.positionslider.valueChanged.disconnect(self.set_position_slider)
        pos = int(position[0]*self.mediaplayer.duration())
        self.positionslider.setValue(pos)
        self.mediaplayer.setPosition(pos)
        frames = (self.mediaplayer.duration()/1000)*self.fps 
        self.bounding_boxes.set_current_frame(int(position[0]*frames), position[1])
        self.positionslider.valueChanged.connect(self.set_position_slider)

    def update_ui(self):
        self.positionslider.valueChanged.disconnect(self.set_position_slider)
        media_pos = int(self.mediaplayer.position())
        self.positionslider.setValue(media_pos)
        self.bounding_boxes.set_current_frame((media_pos/1000)*self.fps, None) 
        if not self.mediaplayer.isPlaying():
            self.timer.stop()
            if not self.is_paused:
                self.stop()
        self.positionslider.valueChanged.connect(self.set_position_slider)
