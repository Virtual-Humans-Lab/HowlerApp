from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QComboBox, QWidget, QPushButton, QHBoxLayout, QLineEdit, QMessageBox
import os
import logg
import memory
import pandas as pd

save_dir = os.path.expanduser("~/Documents")

# Pensar em um nome
if not os.listdir(save_dir).__contains__("AppBugios"):
    os.mkdir(save_dir+"/AppBugios")

save_dir = save_dir+"/AppBugios/"

if not os.path.exists(save_dir+"pontes.csv"):
    with open(save_dir+'pontes.csv', 'w') as fp:
        fp.write("Cod;Nome")
        pass
    
def pontes():
    file = pd.read_csv(save_dir+'pontes.csv',encoding="latin-1",sep=";")
    return file.loc[:,'Nome'].values

def name_to_id(name):
    file = pd.read_csv(save_dir+'pontes.csv',encoding="latin-1",sep=";")
    for i,line in enumerate(file.loc[:,'Nome'].values):
        if line == name:
            return i
    return -1

def adicionar_ponte(nome):
    logg.log("Método: adicionar ponte\nnome: "+str(nome))
    file = pd.read_csv(save_dir+'pontes.csv',encoding="latin-1",sep=";")
    logg.log("file: "+str(file))
    if file.loc[:,'Nome'].values.__contains__(nome):
        logg.log("return: False")
        logg.log("\n")
        return False
    if file.iloc[:,0].values.size == 0:
        next_id = -1
    else:
        next_id = file.iloc[:,0].values.max()
    logg.log("next_id: "+str(next_id))
    with open(save_dir+'pontes.csv', 'a', encoding='latin-1') as fp:
        logg.log("fp: "+str(fp))
        text = str.format("\n{0};{1}", str(next_id+1), nome)
        logg.log("text: "+str(text))
        write = fp.write(text)
        logg.log("written chracters: "+str(write))
    logg.log("return: True")
    logg.log("\n")
    return True

def renomear_ponte(index,novo_nome):
    file = pd.read_csv(save_dir+'pontes.csv',encoding="latin-1",sep=";")
    file.loc[index,'Nome'] = novo_nome
    file.to_csv(save_dir+'pontes.csv',sep=";",encoding="latin-1",index=False)

def deletar_pontes(name):
    file = pd.read_csv(save_dir+'pontes.csv',encoding="latin-1",sep=";")
    idx = file.loc[:,'Nome'].to_list().index(name)
    #print(file.loc[:'Cod'].iloc[idx].values[0])    
    file = file.drop(labels=idx)
    memory.deletar_da_ponte(idx)
    #print(file)
    file.to_csv(save_dir+'pontes.csv',sep=";",encoding="latin-1",index=False)


class PonteDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Escolha uma ponte")
        
        QBtn = (
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.verify)
        self.buttonBox.rejected.connect(self.reject)
        
        self.dropdown = QComboBox()
        self.dropdown.setInsertPolicy(QComboBox.InsertPolicy.InsertAlphabetically)
        self.dropdown.addItems(pontes())
        self.dropdown.setPlaceholderText("")
        self.dropdown.setCurrentIndex(-1)
        self.dropdown.currentIndexChanged.connect(self.save)
        
        self.choice = None
        
        layout = QVBoxLayout()
        message = QLabel("Escolha uma ponte, para adicionar novas pontes use o botão \"Pontes\"")
        layout.addWidget(message)
        layout.addWidget(self.dropdown)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
        
    def verify(self):
        if self.dropdown.currentIndex() == -1:
            QMessageBox.warning(self,"Aviso","Nenhuma Ponte selecionada.",buttons=QMessageBox.StandardButton.Ok)
            return
        self.accept()
        
    def save(self):
        self.choice = self.dropdown.currentIndex()
        
    def retrieve(self):
        return self.choice
        
class PonteJanela(QWidget):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerenciar Pontes")
        
        self.button = QPushButton("Sair")
        self.button.pressed.connect(self.close)
        
        self.dropdown = QComboBox()
        self.dropdown.setInsertPolicy(QComboBox.InsertPolicy.InsertAlphabetically)
        self.dropdown.addItems(pontes())
        self.dropdown.setPlaceholderText("")
        self.dropdown.setCurrentIndex(-1)
        self.dropdown.currentIndexChanged.connect(self.show_options)
        
        self.edit_layout = None
        
        self.mini_widget = QWidget(self)
        self.mini_widget_layout = QHBoxLayout()
        self.text_box = QLineEdit()
        self.add_button = QPushButton("Adicionar")
        self.add_button.clicked.connect(self.adicionar)
        self.mini_widget_layout.addWidget(self.text_box)
        self.mini_widget_layout.addWidget(self.add_button)
        self.mini_widget.setLayout(self.mini_widget_layout)
        
        layout = QVBoxLayout()
        message = QLabel("Escolha uma ponte para editar, ou digite na caixa de texto para adicionar uma nova")
        layout.addWidget(message)
        layout.addWidget(self.dropdown)
        layout.addWidget(self.mini_widget)
        layout.addWidget(self.button)
        self.setLayout(layout)
    
    def adicionar(self):
        logg.log("Método: adicionar")
        self.dropdown.currentIndexChanged.disconnect(self.show_options)
        text = self.text_box.text()
        logg.log("text: "+text)
        if str.replace(text, ' ', '') == '':
            QMessageBox.warning(self,"Texto Vazio","Insira texto no espaço à esquerda do botão para adicionar uma ponte")
            return
        adicionar_ponte(text)
        self.dropdown.clear()
        self.dropdown.addItems(pontes())
        self.dropdown.setPlaceholderText("")
        self.dropdown.setCurrentIndex(-1)
        self.dropdown.currentIndexChanged.connect(self.show_options)
    
    def show_options(self):
        if self.edit_layout == None:
            self.edit_widget = QWidget(self)
            self.edit_options = QLineEdit()
            self.delete_button = QPushButton("Remover")
            self.rename_button = QPushButton("Renomear")
            self.rename_button.clicked.connect(self.rename_event)
            self.delete_button.clicked.connect(self.delete_event)
            
            self.edit_layout = QHBoxLayout()
            self.edit_layout.addWidget(self.edit_options)
            self.edit_layout.addWidget(self.rename_button)
            self.edit_layout.addWidget(self.delete_button)
            self.edit_widget.setLayout(self.edit_layout)
            self.layout().insertWidget(2,self.edit_widget)
        else:
            self.edit_options.clear()
        
    def delete_event(self):
        if self.dropdown.currentIndex() == -1:
            return
        count = memory.index_count(self.dropdown.currentText())
        ver = QMessageBox.question(self,"Confirmação",str.format("Tem certeza que deseja apagar essa ponte? Essa ação também removerá {0} entradas dos resultados.",count))
        if ver == QMessageBox.StandardButton.Yes:
            deletar_pontes(self.dropdown.currentText())
            self.dropdown.clear()
            self.dropdown.addItems(pontes())
            self.dropdown.setCurrentIndex(-1)
        
        
    def rename_event(self):
        if self.edit_options.text() == "":
            QMessageBox.warning(self,"Texto Vazio","Insira texto no espaço à esquerda do botão para renomear")
            return
        ver = QMessageBox.question(self,"Confirmação",str.format("Deseja renomear a ponte \"{0}\" para \"{1}\"?",self.dropdown.currentText(),self.edit_options.text()))
        if ver == QMessageBox.StandardButton.Yes:
            cur_idx = self.dropdown.currentIndex()
            renomear_ponte(self.dropdown.currentIndex(),self.edit_options.text())
            self.dropdown.clear()
            self.dropdown.addItems(pontes())
            self.dropdown.setCurrentIndex(cur_idx)
