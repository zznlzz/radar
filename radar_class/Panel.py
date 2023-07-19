import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
import cv2
from tkinter import filedialog
# from radar_class.mvsdk import CameraReadParameterFromFile
# from radar_class.camera import tune_exposure
from mvsdk import CameraReadParameterFromFile
from camera import tune_exposure

class Dashboard(tk.Tk):
    # hard code part
    zoom_in_ratio_cam = 0.32
    zoom_in_ratio_map = 0.60
    def __init__(self, cam_img_sz:list, map_img_sz:list, main_process=None):
        super().__init__()        
        self.title("Panel")
        self.init_image = ImageTk.PhotoImage(Image.fromarray(np.zeros(cam_img_sz[::-1])))
        # 这个地方用来预热，图片到底是什么无所谓
        self.cam_canvas = tk.Label(self, image=self.init_image)
        
        self.cam_canvas.grid(row=0, rowspan=3, column=1, padx=5, pady=5)
        
        # 放置文本框
        self.textbox = tk.Text(self, height=20, width=55)
        self.textbox.config(font=("Times", 13, "roman"))
        self.textbox.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N)
        self.textbox.tag_config("fore_red", foreground="red")

        # 放置地图, 这个地图在23赛季主要是用来给雷达手自己看的
        self.init_image = ImageTk.PhotoImage(Image.fromarray(np.zeros(map_img_sz[::-1])))
        self.map_canvas = tk.Label(self, image=self.init_image)
        self.map_canvas.grid(row=1, column=0, padx=5, pady=5)
        
        # 放置按钮组件
        self.Button_frame = tk.Frame(self)
        self.Button_frame.grid(row=2, column=0, padx=5, pady=5)

        self.set_camera = tk.Button(self.Button_frame, text='Set cam', width=12, height=2, command=self.set_cam)
        self.set_camera.pack(side=tk.LEFT, pady=5, padx=5)
        self.tune = tk.Button(self.Button_frame, text='Tune', width=12, height=2, command=self.tune_ligth)
        self.tune.pack(side=tk.LEFT, pady=5, padx=5)
        self.update_position = tk.Button(self.Button_frame, text='Update_p', width=12, height=2, command=self.update_postion)
        self.update_position.pack(side=tk.LEFT, pady=5, padx=5)
        self.record_video = tk.Button(self.Button_frame, text='rec_vi', width=12, height=2, command=self.switch_recording_mode, fg='blue')
        self.record_video.pack(side=tk.LEFT, padx=5, pady=5)
        self.stop_process = tk.Button(self.Button_frame, text='STOP', width=12, height=2, command=self.stop_processes, fg='red')
        self.stop_process.pack(side=tk.LEFT, pady=5, padx=5)

        if main_process != None:
            self.main_process = main_process
        
        self.update()
        
    def set_cam(self):
        file_path = filedialog.askopenfilename()
        CameraReadParameterFromFile(self.main_process.cap.cap.hCamera, file_path)
        
    def tune_ligth(self):
        tune_exposure(self.main_process.cap.cap, self.main_process.cap._date)
        
    def update_postion(self):
        self.main_process.update_postion()

    def switch_recording_mode(self):
        self.main_process.resume_flag ^= 1
        if self.main_process.resume_flag:
            self.update_text('Recording RESUMED')
        else:
            self.update_text('Recording PAUSED')
    
    def stop_processes(self):
        self.main_process.stop_flag = True
    
    def update_text(self, string, is_warning=False):
        string = self.convert_2_log_formate(string)
        if is_warning:
            self.textbox.insert(tk.END, string, "fore_red")
        else:
            self.textbox.insert(tk.END, string)
        self.textbox.see('end')
        self.update()        
        
    def update_cam_pic(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if self.zoom_in_ratio_cam:
            frame = cv2.resize(frame, (int(self.zoom_in_ratio_cam*frame.shape[1]), int(self.zoom_in_ratio_cam*frame.shape[0])))
        self.current_cam_pic = ImageTk.PhotoImage(Image.fromarray(frame))
        self.cam_canvas.config(image=self.current_cam_pic)
        self.update()
        
    def update_map_mood(self, map_frame):
        map_frame = cv2.cvtColor(map_frame, cv2.COLOR_BGR2RGB)
        if self.zoom_in_ratio_map:
            map_frame = cv2.resize(map_frame, (int(self.zoom_in_ratio_map*map_frame.shape[1]), int(self.zoom_in_ratio_map*map_frame.shape[0])))
        self.current_map_pic = ImageTk.PhotoImage(Image.fromarray(map_frame))
        self.map_canvas.config(image=self.current_map_pic)
        self.update()
        
    def convert_2_log_formate(self, string):
        if string[-1] != '\n':
            string = string + '\n'
        return string
    

    
import tkinter as tk
from PIL import ImageTk, Image
import cv2

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GUI Demo")
        # self.geometry("600x500")

        # 创建左侧文本框
        self.textbox = tk.Text(self, height=25, width=40)
        # self.textbox.pack(side=tk.LEFT, padx=10, pady=10)
        self.textbox.grid(row=0, column=0, padx=10, pady=10, sticky=tk.N)

        # 创建右侧图片
        self.img = Image.fromarray(np.zeros((200, 200))) # 加载图片
        self.img = self.img.resize((300, 200), Image.ANTIALIAS) # 缩放图片
        self.photo = ImageTk.PhotoImage(self.img)
        self.image_label = tk.Label(self, image=self.photo)
        # self.image_label.pack(side=tk.RIGHT, padx=10, pady=10)
        self.image_label.grid(row=0, rowspan=2, column=1, padx=10, pady=10)

        # 添加按钮，用于更改图片
        self.button = tk.Button(self, text="Change Image", command=self.change_image)
        # self.button.pack(side=tk.TOP)
        self.button.grid(row=1, column=0, sticky=tk.SE, padx=10, pady=10)

    def change_image(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # 更改图片
        self.img = Image.fromarray(frame) # 加载新图片
        self.img = self.img.resize((1280//4*3, 1024//4*3), Image.ANTIALIAS) # 缩放新图片
        self.photo = ImageTk.PhotoImage(self.img)
        self.image_label.config(image=self.photo)




if __name__ == "__main__":
    import sys
    sys.path.append('../single_version')
    from camera import Camera_Thread
    from macro import img_sz, map_size, MAP_PATH
    app = Dashboard(img_sz, map_size)
    cap = Camera_Thread(0)
    map = cv2.imread(MAP_PATH)
    while 1:
        cv2.imshow('test', np.zeros((2,2)))
        key = cv2.waitKey(1)
        if key == ord('r'):
            app.update_text('This is for testing!', is_warning=True)
        ret, frame = cap.read()
        app.update_cam_pic(frame)
        app.update_map_mood(map)
        
    
  
    