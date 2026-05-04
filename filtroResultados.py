from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSlider, QComboBox, QPushButton, QHeaderView, QStackedLayout, QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt
from graphs import Graph_Filtro_Resultados
import memory
import pontesManager


class FiltroResultados(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Resultados")
        self.changing_layou = QStackedLayout()
        self.base_layou = QVBoxLayout()
        
        self.dropdown = QComboBox(self)
        self.dropdown.addItem("Percentual dos quadros com algum animal")
        self.dropdown.addItem("Distribuição das detecções ao longo do vídeo (Gráfico)")
        self.dropdown.currentIndexChanged.connect(self.trocar_layout)
        
        self.base_layou.addWidget(QLabel("Tela Resultados",self),alignment=Qt.AlignmentFlag.AlignCenter)
        self.base_layou.addWidget(self.dropdown)
        self.base_layou.addStretch(5)
        self.base_layou.addLayout(self.changing_layou)
                
        self.criar_layout_0()
        self.criar_layout_1()
        
        self.setLayout(self.base_layou)
        
    def criar_layout_0(self):
        self.slider = QSlider(self)
        self.slider.setMaximum(1000)
        self.slider.setOrientation(Qt.Orientation.Horizontal)
        self.slider.valueChanged.connect(self.change_percent)
        self.percent = QLabel("0%",self)
        self.slider_layout = QHBoxLayout()
        self.slider_layout.addWidget(self.slider)
        self.slider_layout.addWidget(self.percent)
        
        self.filtro_pontes = QTableWidget(self)
        self.filtro_pontes.setColumnWidth(0,self.filtro_pontes.width())
        self.filtro_pontes.setColumnCount(2)
        self.filtro_pontes.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.ResizeToContents)
        self.filtro_pontes.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeMode.Stretch)
        self.filtro_pontes.horizontalHeader().setVisible(False)
        self.filtro_pontes.verticalHeader().setVisible(False)
        self.filtro_pontes.setRowCount(len(pontesManager.pontes()))
        for i, ponte in enumerate(pontesManager.pontes()):
            item = QTableWidgetItem(ponte)
            item.setFlags(Qt.ItemFlag.ItemIsSelectable|Qt.ItemFlag.ItemIsEnabled)
            select = QTableWidgetItem("")
            select.setFlags(Qt.ItemFlag.ItemIsUserCheckable|Qt.ItemFlag.ItemIsEnabled)
            select.setCheckState(Qt.CheckState.Unchecked)
            self.filtro_pontes.setItem(i,0,select)
            self.filtro_pontes.setItem(i,1,item)
            
                
        
        self.button_slider = QPushButton(text="Filtrar",parent=self)
        self.button_slider.pressed.connect(self.filter)

        self.results = None
        
        self.new_layou_0_w = QWidget()
        self.new_layou_0 = QVBoxLayout()
        self.new_layou_0.addLayout(self.slider_layout)
        self.new_layou_0.addStretch(5)
        self.new_layou_0.addWidget(QLabel("Escolha as Pontes",self),alignment=Qt.AlignmentFlag.AlignCenter)
        self.new_layou_0.addWidget(self.filtro_pontes)
        self.new_layou_0.addStretch(5)
        self.new_layou_0.addWidget(self.button_slider)
        
        self.new_layou_0_w.setLayout(self.new_layou_0)
        self.changing_layou.addWidget(self.new_layou_0_w)
    
    def criar_layout_1(self):
        self.new_layou_1 = QVBoxLayout()
        self.new_layou_1_w = QWidget()
        
        self.filtro_pontes2 = QTableWidget(self)
        self.filtro_pontes2.setColumnWidth(0,self.filtro_pontes2.width())
        self.filtro_pontes2.setColumnCount(2)
        self.filtro_pontes2.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.ResizeToContents)
        self.filtro_pontes2.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeMode.Stretch)
        self.filtro_pontes2.horizontalHeader().setVisible(False)
        self.filtro_pontes2.verticalHeader().setVisible(False)
        self.filtro_pontes2.setRowCount(len(pontesManager.pontes()))
        for i, ponte in enumerate(pontesManager.pontes()):
            item = QTableWidgetItem(ponte)
            item.setFlags(Qt.ItemFlag.ItemIsSelectable|Qt.ItemFlag.ItemIsEnabled)
            select = QTableWidgetItem("")
            select.setFlags(Qt.ItemFlag.ItemIsUserCheckable|Qt.ItemFlag.ItemIsEnabled)
            select.setCheckState(Qt.CheckState.Unchecked)
            self.filtro_pontes2.setItem(i,0,select)
            self.filtro_pontes2.setItem(i,1,item)
        self.button_graph = QPushButton(text="Gerar Gráfico",parent=self)
        self.button_graph.pressed.connect(self.grafico)
        
        
        self.new_layou_1.addWidget(QLabel("Escolha as Pontes",self),alignment=Qt.AlignmentFlag.AlignCenter)
        self.new_layou_1.addWidget(self.filtro_pontes2)
        self.new_layou_1.addStretch(5)
        self.new_layou_1.addWidget(self.button_graph)
        self.new_layou_1_w.setLayout(self.new_layou_1)
        self.changing_layou.addWidget(self.new_layou_1_w)
    
    def trocar_layout(self):
        self.changing_layou.setCurrentIndex(self.dropdown.currentIndex())

        
    def change_percent(self):
        self.percent.setText(str.format("{0}%",self.slider.value()/10.0))
        
    def filter(self):
        condicao = self.dropdown.currentText().replace("Percentual ","")
        condicao_id = self.dropdown.currentIndex()
        pontes = []
        for i in range(self.filtro_pontes.rowCount()):
            if self.filtro_pontes.item(i,0).checkState() == Qt.CheckState.Checked:
                pontes.append(pontesManager.name_to_id(self.filtro_pontes.item(i,1).text()))
        percentage = self.slider.value()/1000.0
        results = memory.filter_results(pontes,percentage,0.0,condicao_id)
        total = results[0]+results[1]
        if total == 0:
            # Aviso que tem 0 vídeos
            return
        if self.results != None:
            self.results.setText(str.format("Condição: {3}\n{0}/{1} vídeos\n{2:.2f}% cumprem as condições",results[0],total,(results[0]/total)*100, "Mais de "+str(self.slider.value()/10)+"% "+condicao))
        else:
            self.results = QLabel(str.format("Condição: {3}\n{0}/{1} vídeos\n{2:.2f}% cumprem as condições",results[0],total,(results[0]/total)*100, "Mais de "+str(self.slider.value()/10)+"% "+condicao),self)
            self.results.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.base_layou.addWidget(self.results)
            
    def grafico(self):
        condicao_id = self.dropdown.currentIndex()
        pontes = []
        for i in range(self.filtro_pontes2.rowCount()):
            if self.filtro_pontes2.item(i,0).checkState() == Qt.CheckState.Checked:
                pontes.append(pontesManager.name_to_id(self.filtro_pontes2.item(i,1).text()))
        if pontes == []:
            return
        results = memory.filter_results(pontes,0.0,0.0,condicao_id)
        self.graph = Graph_Filtro_Resultados(results)

    def closeEvent(self, event):
        try:
            self.graph.close()
        except:
            1
        return super().closeEvent(event)