from PySide6.QtGui import QPainter, QPen, QPalette, QColor
from PySide6.QtWidgets import QFrame, QWidget
from PySide6.QtCore import QRectF, QTimer, QSize


class QBBoxes(QFrame):
    def __init__(self, target:QWidget):
        super().__init__()
        self.palette = self.palette()
        self.target = target
        self.ratio = 1
        self.positions = [[[0.0,0.0,0.0,0.0]]]
        self.current_frame = -1
        self.palette.setColor(QPalette.Window, QColor(255, 0, 0))
        self.setPalette(self.palette)
        self.setAutoFillBackground(False)
        self.pen = QPen()
        self.pen.setWidth(1)
        self.pen.setColor('red')
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(100)
        self.value = None
        
    def setBoundingBoxes(self,positions):
        self.positions = positions
        
    def increment(self):
        self.current_frame += 1
        
    def set_current_frame(self, frame:int, value):
        self.current_frame = frame
        self.value = value
        
    def get_position(self,idx):
        return self.positions[int(idx/4)-1]
        
    def updateSize(self,video_size : QSize,instance_size : QSize):
        #ratio = width/heigth
        print(self.geometry())
        old_geo = self.geometry()
        scale = video_size.height() / instance_size.height()
        scaled_h = video_size.height() / scale
        scaled_w = video_size.width() / scale
        delta = old_geo.width() - scaled_w
        self.setGeometry((old_geo.x() + delta/2)-1,old_geo.y(),old_geo.width() - delta,old_geo.height())
        print(self.geometry())
        
    def paintEvent(self, arg__1):
        #Create the painter and pen for drawing bounding boxes
        if self.current_frame == -1:
            return

        self.painter = QPainter()
        
        self.painter.begin(self)
        self.painter.setRenderHints(QPainter.RenderHint.Antialiasing, True)        
        self.painter.setPen(self.pen)
        try:
            current_list = self.positions[int(self.current_frame/4)-1]
            if current_list == [] and self.value == 1.0:
                current_list = self.positions[int(self.current_frame/4)]
            if current_list != [] and self.value == 0.0:
                current_list = []
        except:
            self.painter.end()
            return
        self.painter.setWindow(0,0,100,100)
        for pos in current_list:
            self.painter.drawRect(QRectF(pos[0]*100, pos[1]*100, (pos[2]-pos[0])*100, (pos[3]-pos[1])*100))
        self.painter.end()
        ##############