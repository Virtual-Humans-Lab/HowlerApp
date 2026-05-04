import os
import hashlib
import ast
import numpy as np
import cv2 as cv
import pandas as pd

# Setup inicial
save_dir = os.path.expanduser("~/Documents")

# Pensar em um nome
if not os.listdir(save_dir).__contains__("AppBugios"):
    os.mkdir(save_dir+"/AppBugios")
if not os.listdir(save_dir+"/AppBugios").__contains__("temp"):
    os.mkdir(save_dir+"/AppBugios/temp")
save_dir = save_dir+"/AppBugios/"
if not os.path.exists(save_dir+"results.csv"):
    with open(save_dir+'results.csv', 'w') as fp:
        fp.write("Hash;Video;Ponte;FPS;Frames;Valores;Confianca;Posicoes")
        pass
    
def clear_temp_dir():
    for file in os.listdir(temp_dir()):
        os.remove(file)
    
def temp_dir():
    save_dir = os.path.expanduser("~/Documents")
    return save_dir+"/AppBugios/temp/"
    
    """salva um vídeo no csv
    """
def save_entry(video,ponte,values,confidance,boxes,fps,frame_count):
    file = pd.read_csv(save_dir+'results.csv',encoding="latin-1",sep=";")
    if inResults(video):
        return
    else:
        string = str.format("\n{0};{1};{2};{3};{4};{5};{6};{7}",hash_video(video),video,ponte,fps,frame_count,values,confidance,boxes)
        # TO-DO catch excessão de permissão negada (arquivo aberto no excel)
        with open(save_dir+'results.csv', 'a') as fp:
            fp.write(string)
 
    """retorna os valores de um vídeo salvo no csv, se ele estiver no csv, senão retorna None
    """       
def fetch(video):
    file = pd.read_csv(save_dir+'results.csv',encoding="latin-1",sep=";")
    line = file.loc[file['Hash']==hash_video(video)]
    linepos = line.index.values[0]
    if line.empty:
        return None
    values = list(map(float,line.loc[linepos,'Valores'].replace('[','').replace(']','').split(',')))
    confidance = list(map(float,line.loc[linepos,'Confianca'].replace('[','').replace(']','').split(',')))
    boxes = ast.literal_eval(line.loc[linepos,'Posicoes'])
    fps = line.loc[linepos,'FPS']
    return [values,confidance,boxes,fps]

    """calcula o hash de um vídeo, mais especificamente, pega o primeiro frame como array e calcula o sha1 dele
    """
def hash_video(video):
    cap = cv.VideoCapture(video)
    success, frame = cap.read()
    cap.release()
    return hashlib.sha1(str(frame).encode("utf-8"),usedforsecurity=False).hexdigest()

    """retorna True se o hash de um vídeo está no csv, se não retorna False
    """
def inResults(video):
    file = pd.read_csv(save_dir+'results.csv',encoding="latin-1",sep=";")
    return hash_video(video) in file.loc[:,"Hash"].values

def count():
    file = pd.read_csv(save_dir+'results.csv',encoding="latin-1",sep=";")
    return file.count().iloc[0]

def results_bruto():
    file = pd.read_csv(save_dir+'results.csv',encoding="latin-1",sep=";")
    return file

def index_count(name):
    file = pd.read_csv(save_dir+'results.csv',encoding="latin-1",sep=";")
    file2 = pd.read_csv(save_dir+'pontes.csv',encoding="latin-1",sep=";")
    idx = file2.loc[:,'Nome'].to_list().index(name)
    idx = file2.loc[:,'Cod'].iloc[idx]
    try:
        return file.loc[:,'Ponte'].value_counts()[idx]
    except:
        return 0

def deletar_da_ponte(idx):
    file = pd.read_csv(save_dir+'results.csv',encoding="latin-1",sep=";")
    to_del = []
    for i,line in enumerate(file.loc[:,'Ponte'].values):
        if line == idx:
            to_del.append(i)
    for v in to_del:
        file = file.drop(index=v)
    file.to_csv(save_dir+'results.csv',sep=";",encoding="latin-1",index=False)

def filter_results(pontes:list,percentage:float,confidance:float,condition:int):
    file = pd.read_csv(save_dir+'results.csv',encoding="latin-1",sep=";")
    if condition == 0:
        to_test = []
        positive = 0
        negative = 0
        for i,line in enumerate(file.loc[:,'Ponte'].values):
            if line in pontes:
                to_test.append(i)
        for idx in to_test:
            line = file.iloc[idx].loc['Valores']
            total = len(line.replace(',','').replace('[','').replace(']','').replace(' ',''))
            sim = line.count('1')
            if sim >= total*percentage:
                positive += 1
            else:
                negative += 1
        return (positive,negative)
    
    if condition == 1:
        to_test = []
        percentile = [0,0,0,0,0,0,0,0,0,0]
        for i,line in enumerate(file.loc[:,'Ponte'].values):
            if line in pontes:
                to_test.append(i)
        for idx in to_test:
            line = file.iloc[idx].loc['Valores']
            line = list(map(int,line.replace(',','').replace('[','').replace(']','').replace(' ','')))
            lenght = len(line)
            tenth = lenght/10
            current_pos = 0
            current_limit = tenth
            for i,entry in enumerate(line):
                percentile[current_pos] += int(entry)
                if i > current_limit:
                    current_limit += tenth
                    current_pos += 1
        return percentile
        