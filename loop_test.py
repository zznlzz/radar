# import sys
# sys.path.append('RM_4_points_yolov5/')
# sys.path.append('radar_class/')
# from radar_class.camera import Camera_Thread
# from network.Predictor import Predictor
# import cv2

# cap = cv2.VideoCapture('/home/pheonix/NewDisk/about_radar/Radar_structure/single_version/save_stuff/video/15.mp4')
# _, frame = cap.read()
# frame_height, frame_width = frame.shape[0], frame.shape[1]
# NET_PATH = 'weights/800x800_large.pt'
# width = 3088
# height = 2064
# model_imgsz = (800, 800)
# net = Predictor(NET_PATH, model_imgsz)

# while True:
#     # 读取一帧图片
#     ret, frame = cap.read()
#     _, _, show_im = net.cated_infer(frame)
#     cv2.imshow('show_im', show_im)

import cv2
import sys
sys.path.append('RM_4_points_yolov5/')
sys.path.append('radar_class/')
from radar_class.camera import Camera_Thread
from network.Predictor import Predictor
model_imgsz = (800, 800)
# 打开视频文件
cap = cv2.VideoCapture('/home/pheonix/NewDisk/about_radar/Radar_structure/single_version/save_stuff/video/15.mp4')
NET_PATH = 'weights/800x800_large.pt'
net = Predictor(NET_PATH, model_imgsz)
cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
# 检查是否成功打开
if not cap.isOpened():
    print("Failed to open video file")

# 循环读取视频帧
while True:
    # 读取一帧图片
    ret, frame = cap.read()

    # 判断是否读取成功
    if ret:
        # 显示图片
        _, _, frame = net.cated_infer(frame)
        cv2.imshow('frame', frame)
    else:
        # 如果读取失败，退出循环
        break

    # 按下q键退出
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

# 释放资源并关闭窗口
cap.release()
cv2.destroyAllWindows()
