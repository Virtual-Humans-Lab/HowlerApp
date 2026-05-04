from ultralytics import YOLO
from PySide6.QtCore import QObject, Signal, Slot
import os
from torch import cuda
import time
import numpy as np
import cv2
import memory
import moviepy
import mainWindow

class YoloModel(QObject):
    signal_update = Signal(int, bool)
    signal_set_max = Signal(int, bool)
    signal_reset =  Signal()
    finished = Signal()
    output = Signal(list)
    
    file = ""
    def __init__(self, path, progress_pointer):
        super().__init__()
        self.signal_update.emit(0,False)
        self.signal_update.emit(1,True)
        self.progress = progress_pointer
        self.cudaFlag = False
        try:
            if cuda.is_available():
                self.cudaFlag = True
        except:
            self.cudaFlag = False
        print(self.cudaFlag)
        self.model = YOLO(os.path.join(path,"resources/model/best.pt"),verbose=False)
        if self.cudaFlag:
            cuda.set_device(0)
            self.model.to('cuda')
            #print("GPU")

    def setFile(self,file):
        self.file = file
        
    def setPonte(self,ponte):
        self.ponte = ponte

    def getFile(self):
        return self.file

    def run(self):
        if type(self.file) == type([]):
            self.runMultiFile()
        else:
            self.runSingleFile()
    def runMultiFile(self):
        for i, file in enumerate(self.file):
            cap = cv2.VideoCapture(file)
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if frames != 750:
                self.signal_set_max.emit(frames-750, True)
                #self.progress.setMaximum(self.progress.maximum()+(frames-750))
            if memory.inResults(file):
                self.signal_update.emit(frames, True)
                continue
            
            if not self.verification(cap):
                self.converte_para_mp4(file)
            else:
                self.true_file = file
            cap.release()
            result = self.model(self.true_file, stream=True)
            result = self.process_yolo(file,self.ponte,[False,result,fps,frames],True)
            if result == []:
                self.finished.emit()
                return result
        self.signal_reset.emit()
        self.finished.emit()
    
    def runSingleFile(self):
        if os.path.isfile(self.file):
            if self.file.lower().endswith(('.mp4','.avi','.asf','.gif','.m4v','.mkv','.mov','.mpeg','.mpg','.ts','.wmv','.webm')):
                if memory.inResults(self.file):
                    self.output.emit([True,self.file,0])
                    self.signal_reset.emit()
                    self.finished.emit()
                    return None
                else:
                    cap = cv2.VideoCapture(self.file)
                    fps = int(cap.get(cv2.CAP_PROP_FPS))
                    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    if frames > 0:
                        self.signal_set_max.emit(frames, False)
                    if self.cancela_check():
                        cap.release()
                        self.finished.emit()
                        return None                        
                    if not self.verification(cap):
                        self.converte_para_mp4(self.file)
                    else:
                        self.true_file = self.file
                    cap.release()
                    if self.cancela_check():
                        self.finished.emit()
                        return None                        
                    result = self.model(self.true_file, stream=True)
                    result = self.process_yolo(self.getFile(),self.ponte,[False,result,fps,frames],False)
                    if result == []:
                        self.finished.emit()
                        return result
                    self.output.emit([False,result,fps])
                    self.finished.emit()
                    return result
        self.finished.emit()
        return ""
    
    def cancela_check(self):
        return self.progress.wasCanceled()
    
    def process_yolo(self,video,ponte,data,multi_flag=False):
        to_graph = []
        confidance = []
        bboxes = []
        votes = []
        votes_count = []
        fps = data[2]
        frames = data[3]
        backup_frame = []
        backup_frame1 = []
        backup_frame2 = []
        frames_since_update = 0
        
        for i,frame in enumerate(data[1]):
            if self.cancela_check():
                break
            n = frame.boxes.cls.nelement()
            if not votes.__contains__(n):
                votes.append(n)
                votes_count.append(1)
            else:
                votes_count[votes.index(n)] = votes_count[votes.index(n)]+1
            if i/float(4) == int(i/float(4)) and i != 0:
                frame_list = [frame,backup_frame,backup_frame1,backup_frame2]
                to_graph.append(votes[votes_count.index(np.array(votes_count).max())])
                confidanceI = 0.0
                conf_count = 0
                for f in frame_list:
                    for c in f.boxes.conf:
                        confidanceI += c.item()
                        conf_count += 1
                if conf_count == 0:
                    confidanceI = "0.0"
                else:
                    confidanceI = str(confidanceI/conf_count)
                # Se tem algum animal
                if votes[votes_count.index(np.array(votes_count).max())] > 0:
                    temp = []
                    temp = frame.boxes.xyxyn.numpy().tolist()
                    if temp == []:
                        temp = backup_frame.boxes.xyxyn.numpy().tolist()
                        if temp == []:
                            temp = backup_frame1.boxes.xyxyn.numpy().tolist()
                            if temp == []:
                                temp = backup_frame2.boxes.xyxyn.numpy().tolist()
                    for idx,t in enumerate(temp):
                        j = list(map(lambda x : float('%.2f'%x),t))
                        temp.insert(idx,j)
                        temp.remove(t)
                    bboxes.append(temp)
                else:
                    bboxes.append([])
                if len(confidanceI) > 4:
                    confidanceI = confidanceI[0:5]
                confidance.append(float(confidanceI))
                votes = []
                votes_count = []
            backup_frame2 = backup_frame1
            backup_frame1 = backup_frame
            backup_frame = frame
            if frames_since_update > 9:
                self.signal_update.emit(frames_since_update+1, True)       #Crasshou aqui
                frames_since_update = -1
            frames_since_update += 1
        if self.cancela_check():
            return []
        if not multi_flag:
            self.signal_update.emit(len(to_graph),False)
            #progress.setValue(len(to_graph))
            self.signal_reset.emit()
        memory.save_entry(video,ponte,to_graph,confidance,bboxes,fps,frames)
        return [to_graph,confidance,bboxes,fps]
    
    
    def verification(self,cap:cv2.VideoCapture):
        desired_frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        frame_count = -1
        flag = True
        while flag:
            flag, frame = cap.read()
            frame_count += 1
        if desired_frame_count != frame_count:
            return False
        else:
            return True
        
    def converte_para_mp4(self,file):
        temp_file = moviepy.VideoFileClip(file)
        new_file = memory.temp_dir()+file.split('/')[-1]+'.mp4'
        temp_file.write_videofile(filename=new_file,codec='libx264',audio=False, logger=None, write_logfile=False)
        self.true_file = new_file