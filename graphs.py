import pyqtgraph as pg
from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSizePolicy
from PySide6.QtGui import QFont

class Graph_Filtro_Resultados(QWidget):
    def __init__(self,data):
        super().__init__()
        self.setWindowTitle("Gráfico")
        total = sum(data)
        self.data = list(map(lambda a : (a/total)*100,data))

        
        self.plot_graph_dif = pg.plot(left="Detecções (%)",bottom="Percentil do Vídeo (%)")
        self.plot_graph = self.plot_graph_dif.getPlotItem()
        self.plot = self.plot_graph.plot()
        self.plot.setData(x=[10,20,30,40,50,60,70,80,90,100],y=self.data,left="Detecções (%)",bottom="Percentil do Vídeo (%)", 
                          pen=(200,200,200), symbolBrush=(255,0,0), symbolPen='w')
        self.plot_graph.setMouseEnabled(x=False,y=False)
        
        self.button = QPushButton("Mostrar Valores Exatos",self)
        self.button.clicked.connect(self.mostrar_valores)
        self.toogle = False
        self.label = QLabel(self)
        self.label.setFont(QFont(self.label.font().family(),10))
        self.layou = QVBoxLayout()
        self.layou.addWidget(self.plot_graph_dif)
        self.layou.addWidget(self.button)
        self.layou.addWidget(self.label)
        self.setLayout(self.layou)
        self.show()
        
    def mostrar_valores(self):
        if self.toogle == False:
            data = self.plot.yData
            string = ""
            for i, data in enumerate(data):
                string += str.format("{0}-{1}%: {2:.2f}%    ",i*10,(i+1)*10,data)
                if i == 4:
                    string+="\n"
            self.label.setText(string)
            self.button.setText("Esconder Valores Exatos")
        else:
            self.label.setText("")
            self.button.setText("Mostrar Valores Exatos")
        self.toogle = not self.toogle
        
    def graph(self):
        return self.win
    
    def set_data(self,data):
        # data = [values,confidance,boxes,fps]
        self.data = data
      
        self.plot.setData(x=[0,10,20,30,40,50,60,70,80,90],y=data,pen=(200,200,200), symbolBrush=(255,0,0), symbolPen='w',
                          left="Detecções (%)",bottom="Percentil do Vídeo (%)")
        
        ay = self.plot_graph.getAxis('left')  # This is the trick
        dy = [(value, str(value)) for value in list((range(int(min(data)), round(max(data)+6,-1))))]
        ay.setTicks([dy, []])
        
        
class Histogram_Filtro_Resultados(QWidget):
    def __init__(self,data):
        super().__init__()
        self.setWindowTitle("Gráfico")
        total = sum(data)
        self.data = list(map(lambda a : (a/total)*100,data))

        
        self.plot_graph_dif = pg.plot(left="Detecções (%)",bottom="Percentil do Vídeo (%)")
        self.plot_graph = self.plot_graph_dif.getPlotItem()
        self.plot = self.plot_graph.plot()
        self.plot.setData(x=[10,20,30,40,50,60,70,80,90,100],y=self.data,left="Detecções (%)",bottom="Percentil do Vídeo (%)", 
                          pen=(200,200,200), symbolBrush=(255,0,0), symbolPen='w')
        self.plot_graph.setMouseEnabled(x=False,y=False)
        
        self.button = QPushButton("Mostrar Valores Exatos",self)
        self.button.clicked.connect(self.mostrar_valores)
        self.toogle = False
        self.label = QLabel(self)
        self.label.setFont(QFont(self.label.font().family(),10))
        self.layou = QVBoxLayout()
        self.layou.addWidget(self.plot_graph_dif)
        self.layou.addWidget(self.button)
        self.layou.addWidget(self.label)
        self.setLayout(self.layou)
        self.show()
        
    def mostrar_valores(self):
        if self.toogle == False:
            data = self.plot.yData
            string = ""
            for i, data in enumerate(data):
                string += str.format("{0}-{1}%: {2:.2f}%    ",i*10,(i+1)*10,data)
                if i == 4:
                    string+="\n"
            self.label.setText(string)
            self.button.setText("Esconder Valores Exatos")
        else:
            self.label.setText("")
            self.button.setText("Mostrar Valores Exatos")
        self.toogle = not self.toogle
        
    def graph(self):
        return self.win
    
    def set_data(self,data):
        # data = [values,confidance,boxes,fps]
        self.data = data
      
        self.plot.setData(x=[0,10,20,30,40,50,60,70,80,90],y=data,pen=(200,200,200), symbolBrush=(255,0,0), symbolPen='w',
                          left="Detecções (%)",bottom="Percentil do Vídeo (%)")
        
        ay = self.plot_graph.getAxis('left')  # This is the trick
        dy = [(value, str(value)) for value in list((range(int(min(data)), round(max(data)+6,-1))))]
        ay.setTicks([dy, []])
    
class Graph(QObject):
    lastClicked = []
    clickedPen = pg.mkBrush((10,255,10,255))
    change_video_frame = Signal(list)
    def __init__(self):
        super().__init__()
        self.win = pg.GraphicsLayoutWidget()
        self.plot_graph = pg.PlotItem(left="Bugios",bottom="Frame")
        self.plot = self.plot_graph.plot()
        self.plot_graph.setMouseEnabled(x=False,y=False)
        self.win.addItem(self.plot_graph)
        self.win.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Expanding)
        self.win.setMinimumWidth(715)
        
    def graph(self):
        return self.win
    
    def set_data(self,data):
        self.data = data[0]
        self.yPos = []
        for y in data[0]:
            self.yPos.append(156 if y == 0.0 else 12)
        self.plot.setData(data[0],pen=(200,200,200), symbolBrush=(255,0,0), symbolPen='w')
        
        ay = self.plot_graph.getAxis('left')  # This is the trick
        dy = [(value, str(value)) for value in list((range(int(min(data[0])), int(max(data[0])+1))))]
        ay.setTicks([dy, []])
        
        self.plot.scatter.sigClicked.connect(self.mouseClickEvent)
    
    def mouseClickEvent(self, plot, points):
        for p in self.lastClicked:
            p.resetBrush()
        for p in points:
            p.setBrush(self.clickedPen)
        self.lastClicked = points
        max = len(self.plot.scatter.points())-1
        for i, point in enumerate(self.plot.scatter.points()):
            if point == points[0]:
                if i == len(self.plot.scatter.points())-1:
                    self.change_video_frame.emit([(i/max)-0.01,point.pos()[1]])
                else:
                    self.change_video_frame.emit([i/max,point.pos()[1]])
                return        
                    