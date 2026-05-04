import os


save_dir = os.path.expanduser("~/Documents")

# Pensar em um nome
if not os.listdir(save_dir).__contains__("AppBugios"):
    os.mkdir(save_dir+"/AppBugios")

save_dir = save_dir+"/AppBugios/"

if not os.path.exists(save_dir+"log.txt"):
    with open(save_dir+'log.txt', 'w') as fp:
        fp.write("")
        pass
    
def log(text):
    with open(save_dir+'log.txt', 'a') as fp:
        fp.write(text+'\n')
        pass