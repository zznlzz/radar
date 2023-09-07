import glob
from radar_class.camera import Camera_Thread
from my_utils.function import read_yaml
from radar_class.Lidar import Radar
from radar_class.prediction_handler import Bbox_Handler
from radar_class.location_alarmor import Location_alarmer
from network.Predictor import Predictor
import time
import cv2 
from radar_class.macro import MAP_PATH, enemy, home_test, map_size, img_sz, position_choice, NET_PATH, model_imgsz, debug, VIDEO_SAVE_DIR
from radar_class.location import locate_record, locate_pick, armor_filter
from radar_class.Panel import Dashboard
from radar_class.Debugger import Debugger
import traceback
import sys
sys.path.append('RM_4_points_yolov5/')
sys.path.append('radar_class/')
import numpy as np
from radar_class.static_uart import Static_UART
import serial
import threading

class radar_process:
    def __init__(self):
        self.panel = Dashboard(img_sz, map_size, self) # 初始化前端面板
        self.map = cv2.imread(MAP_PATH) # 加载地图
        self.cap = Camera_Thread(0) # 初始化相机
        self.stop_flag = False # 停止标志位 
        self._cap1 = self.cap
        if self.cap.is_open():
            self.panel.update_text("[INFO] Camera {0} Starting.".format(0))
        else:
            self.panel.update_text("[INFO] Camera {0} Failed, try to open.".format(0), is_warning=True)

        # 初始化视频保存器
        _, K_0, C_0, E_0, imgsz = read_yaml(0)
        save_order = self.increment_path(VIDEO_SAVE_DIR)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.vi_saver = cv2.VideoWriter(f'{VIDEO_SAVE_DIR}/{save_order}.mp4', fourcc, 6, imgsz)
        self.resume_flag = 0

        # 初始化处理边界框和地图的类
        self.bbox_handler = Bbox_Handler()
        self._scene = [self.bbox_handler]
        self.location_alarmor = Location_alarmer(False, True)

        self.net = Predictor(NET_PATH, model_imgsz) # 初始化目标检测模型
        # weights/detail_best.pt

        self.position_flag = False
        self._position_flag = np.array([self.position_flag])

        self.radar = Radar(K_0, C_0, E_0, queue_size=20, imgsz=img_sz)
        Radar.start()
        self.radar_init = False
        
        # 初始化调试器：将面板对象传递给它，用于在面板上显示调试信息
        self.debugger = Debugger(self.panel)
        self.uart_ids = {1:101, 2:102, 3:103, 4:104, 5:105, 0:107, 10:1, 11:2, 12:3, 13:4, 14:5, 9:7}
        
        
        
        
    def get_position_using_last(self):
        '''
        使用保存的位姿
        '''
        if self._position_flag.all(): # 全部位姿已估计完成
            self.panel.update_text("feedback", "camera pose already init")
            return
        if not self._position_flag[0]:
            flag, rvec1, tvec1 = locate_record(0, enemy)
            if flag:
                self._position_flag[0] = True
                # myshow.set_text("feedback", "Camera 0 pose init")
                self.panel.update_text("[INFO] Camera 0 pose init")
                # 将位姿存入反投影预警类
                T, cp = self._scene[0].push_T_and_inver(rvec1, tvec1)
                # 将位姿存入位置预警类
                self.location_alarmor.push_T(T, cp, 0)
            else:
                # myshow.set_text("feedback", "Camera 0 pose init error")
                self.panel.update_text("[INFO] Camera 0 pose init meet error", is_warning=True)
        # if not self._position_flag[1]:
        #     flag, rvec2, tvec2 = locate_record(1, enemy)
        #     if flag:
        #         self._position_flag[1] = True
        #         self._myshow.set_text("feedback", "camera 1 pose init ")
        #         print("[INFO] Camera 1 pose init")
        #         T, cp = self._scene[1].push_T(rvec2, tvec2)
        #         self._alarm_map.push_T( T, cp, 1)
        #     else:
        #         self._myshow.set_text("feedback", "camera 1 pose init meet error ")
        #         print("[INFO] Camera 1 pose init meet error")
        # 重叠区域去重
        # if split and self._position_flag.all():
        #     inside1, whole_location = self._scene[0].get_inside()
        #     inside1 = np.stack(inside1, axis=0)
        #     inside2, _ = self._scene[1].get_inside()
        #     inside2 = np.stack(inside2, axis=0)
        #     both_inside = np.logical_and(inside1.any(axis=1), inside2.any(axis=1)) # 大家都有的区域
        #     larger = inside1.sum(axis=1) >= inside2.sum(axis=1) # 比较在图像内的点数
        #     lesser = np.logical_not(larger)
        #     # larger为c0比c1多，lesser为c1比c0多
        #     whole_location = np.array(whole_location)
        #     self._scene[0].remove(whole_location[np.logical_and(lesser,both_inside)])
        #     self._scene[1].remove(whole_location[np.logical_and(both_inside,larger)])
        
    def get_position_new(self):
        '''
        using huge range object to get position, which is simple but perfect
        '''
        if self._position_flag.all():
            print("feedback", "camera pose already init")
            return
        
        if not self._position_flag[0]:
            flag = False
            if self._cap1.is_open():
                flag, rvec1, tvec1 = locate_pick(self._cap1, enemy, 0,  home_size = home_test, panel=self.panel)
            if flag:
                self._position_flag[0] = True
                self.panel.update_text("[INFO] Camera 0 pose init")
                locate_record(0, enemy, True, rvec1, tvec1) # 保存
                T, cp = self._scene[0].push_T_and_inver(rvec1, tvec1)
                self.location_alarmor.push_T(T, cp, 0)
            else:
                self.panel.update_text("Camera 0 pose init meet error", is_warning=True)
                self.panel.update_text("[INFO] Camera 0 pose init error", is_warning=True)

    def increment_path(self, up_dir): 
        '''
        增加视频保存路径中的数字序号，以确保不会覆盖已有的视频文件
        '''
        if up_dir[-1] != '/':
            up_dir = up_dir+'/'
        file_name_list = glob.glob(f'{up_dir}*.mp4')
        start_num = 1
        if len(file_name_list) != 0:
            for i in file_name_list:
                current_num = int(i.split('/')[-1].split('.')[0])
                if current_num > start_num:
                    start_num = current_num
        else:
            return start_num
        return start_num+1

    def update_postion(self):
        flag = False
        if self._cap1.is_open():
            flag, rvec1, tvec1 = locate_pick(self._cap1, enemy, 0,  home_size= home_test, panel=self.panel)
        if flag:
            print("[INFO] Camera 0 pose UPDATED")
            locate_record(0, enemy, True, rvec1, tvec1) # 保存
            T, cp = self._scene[0].push_T_and_inver(rvec1, tvec1)
            self.location_alarmor.push_T(T, cp, 0)
        else:
            print("[WARNING] Camera 0 pose updated error")

    def change_id_2_uart(self, pred_loc):
        '''
        将目标的ID更改为对应的UART ID
        '''
        # 这里必须要确保pred_loc不是None或者之类的异常变量
        for row in pred_loc:
            row[0] = self.uart_ids[row[0]] if row[0] in self.uart_ids.keys() else row[0]

    def spin_once(self):
        # 检查雷达初始化状态
        if self.radar.check_radar_init():
            self.radar_init = True

        # 2.6226043701171875e-05
        # 对打开失败的相机，尝试再次打开
        if not self.cap.is_open():
            self.cap.open()
        flag, frame = self.cap.read()
        # self.panel.update_cam_pic(frame)
        if not flag:
            self.panel.update_text('The camera could NOT be opened')
            time.sleep(0.05)
            return
        
        # 目标检测和筛选
        ret, locations, show_im = self.net.cated_infer(frame)
        locations = armor_filter(locations)

        # 更新前段面板显示的摄像头图片
        self.panel.update_cam_pic(show_im)
        
        pred_loc = None
        
        if ret:
            # 位置信息的微调
            pred_loc = self.location_alarmor.refine_cood(locations, self.radar)
            
            if len(pred_loc): 
                pred_loc = np.array(pred_loc, dtype=np.float32)
                if len(pred_loc.shape) == 1: pred_loc = pred_loc[None]
            
            # 如果微调后的目标位置信息可用（有一个包含目标信息的数组）
            if isinstance(pred_loc, np.ndarray):
                self.debugger.pred_loc_debugger(pred_loc)
                self.change_id_2_uart(pred_loc)
                Static_UART.push_loc(pred_loc)
                Static_UART.push_alarm(pred_loc)

        # 调试模式下的地图显示
        if debug:
            self.panel.update_map_mood(self.bbox_handler.draw_on_map(pred_loc, self.map.copy()))
        
        if self.resume_flag:
            self.vi_saver.write(frame)
        
    def stop_and_release(self):
        self.cap.release()
        # self.uart_proce.terminate()
        Static_UART.stop_flag = True
        self.vi_saver.release()
        self.radar.__del__()
    
    
if __name__ == '__main__':
    try:
        ser = serial.Serial('/dev/ttyUSB0', 115200, 8, 'N', 1, timeout=0.01) 
        main_process = radar_process()
        choice = position_choice if isinstance(position_choice, str) else input('Get new position? Y/y for yes, N/n for no\n')
        uart_thread = threading.Thread(target=Static_UART.advanced_loop, args=(ser, ), name='uart')
        # alarm_thread = threading.Thread(target=Static_UART.alarm_loop, args=(ser, ), name='alarm')
        uart_thread.start()
        # alarm_thread.start()

        if choice in ['Y', 'y']:
            main_process.panel.set_cam()
            main_process.get_position_new()
        elif choice in ['N', 'n']:
            main_process.get_position_using_last()
        while 1:
            t1 = time.time()
            main_process.spin_once()
            fps = 1 / (time.time() - t1)
            main_process.panel.update_text(f'The fps is:{fps}', True)
            
            if main_process.stop_flag:
                main_process.stop_and_release()
                break
            
    except:
        traceback.print_exc()
        
    
    
        
        
        
        
        
        
        
        




