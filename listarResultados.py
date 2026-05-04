from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHeaderView, QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt
import memory
import pontesManager


class ListaResultados(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Resultados")
        self.resize(600,300)
        self.layou = QVBoxLayout()
        
        self.filtro_pontes = QTableWidget(self)
        self.filtro_pontes.setColumnCount(4)
        self.filtro_pontes.horizontalHeader().setDefaultSectionSize(120)
        self.filtro_pontes.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.Stretch)
        self.filtro_pontes.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeMode.Stretch)
        self.filtro_pontes.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeMode.Fixed)
        self.filtro_pontes.horizontalHeader().setSectionResizeMode(3,QHeaderView.ResizeMode.Fixed)
        self.filtro_pontes.verticalHeader().setVisible(False)
        self.filtro_pontes.setRowCount(memory.count())
        self.filtro_pontes.setHorizontalHeaderLabels(["Vídeo","Ponte","Presença","Confiança Média*"])
        
        for i,line in enumerate(memory.results_bruto().values):
            name = line[1]
            ponte_id = line[2]
            frames = line[4]
            valores = line[5]
            valores_count = len([i for i in list(map(int,valores.replace('[','').replace(']','').split(', '))) if i == 1]) * 4
            confiaca = line[6]
            confiaca_lista = list(map(float,confiaca.replace('[','').replace(']','').split(', ')))
            confiaca_lista_sem_zero = [i for i in confiaca_lista if i != 0.0]
            if len(confiaca_lista_sem_zero) == 0:
                confiaca_lista_sem_zero = [1.0]
            posicoes = line[7]
            itemN = QTableWidgetItem(str(name).split('/')[-1].split('.')[0])
            itemP = QTableWidgetItem(pontesManager.pontes()[ponte_id])
            itemQ = QTableWidgetItem(str.format("{0}/{1} ({2:.2f}%)",valores_count,frames,valores_count/frames*100))
            itemC = QTableWidgetItem(str(sum(confiaca_lista_sem_zero)/len(confiaca_lista_sem_zero)*100)[0:4]+'%')
            itemN.setFlags(Qt.ItemFlag.ItemIsEnabled)
            itemP.setFlags(Qt.ItemFlag.ItemIsEnabled)
            itemQ.setFlags(Qt.ItemFlag.ItemIsEnabled)
            itemC.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.filtro_pontes.setItem(i,0,itemN)
            self.filtro_pontes.setItem(i,1,itemP)
            self.filtro_pontes.setItem(i,2,itemQ)
            self.filtro_pontes.setItem(i,3,itemC)
        
        self.layou.addWidget(QLabel("Lista dos Resultados Salvos",self),alignment=Qt.AlignmentFlag.AlignCenter)
        self.layou.addWidget(self.filtro_pontes)
        self.layou.addWidget(QLabel("*Confiança Média: Média da confiança do modelo nos quadros em que há detecção"))
        self.setLayout(self.layou)