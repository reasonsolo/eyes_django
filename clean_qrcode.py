import os
import datetime
import time
file_dir = '/data/resource/qrcode/'
f =  list(os.listdir(file_dir))
print("clean file in " + file_dir)
for i in range(len(f)):
    filedate = os.path.getmtime(file_dir + f[i])
    current_time = time.time()
    duration =(current_time - filedate)/60
    if duration >= 30:
        try:
            os.remove(file_dir + f[i])
        except Exception as e:                                             
            print(e)      
