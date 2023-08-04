import sys
sys.path.append('RM_4_points_yolov5/')
sys.path.append('radar_class/')
from radar_class.camera import Camera_Thread
from network.Predictor import Predictor
import cv2

cap = Camera_Thread(0)
_, frame = cap.read()
frame_height, frame_width = frame.shape[0], frame.shape[1]
NET_PATH = 'weights/800x800_large.pt'
width = 3088
height = 2064
model_imgsz = (800, 800)
# 左上角的点
x1, y1 = 0, 0
x2, y2 = width, height
cv2.namedWindow('shrink_frame', cv2.WINDOW_NORMAL)
net = Predictor(NET_PATH, model_imgsz)


def left_move(mv_sz):
    global width, height
    global x1, y1, x2, y2
    if x1-mv_sz<0:
        x1 = 0
        x2 = width
    else:
        x1 -= mv_sz
        x2 -= mv_sz

def right_move(mv_sz):
    global width, frame_width
    global x1, x2
    if x2+mv_sz>frame_width:
        x2 = frame_width
        x1 = frame_width - width
    else:
        x1 += mv_sz
        x2 += mv_sz

def up_move(mv_sz):
    global height
    global y1, y2
    if y1-mv_sz <0:
        y1 = 0
        y2 = height
    else:
        y1 -= mv_sz
        y2 -= mv_sz
        
def down_move(mv_sz):
    global height, frame_height
    global y1, y2
    if y2+mv_sz>frame_height:
        y2 = frame_height
        y1 = frame_height - height
    else:
        y1 += mv_sz
        y2 += mv_sz



while 1:
    from radar_class import mvsdk
    ret, frame = cap.read()
    new_frame = frame[y1:y2, x1:x2]
    # new_frame = cv2.resize(new_frame, model_imgsz)
    mvsdk.CameraReadParameterFromFile(cap.cap.hCamera, 'save_stuff/camera_0_of_2023-07-19 15-12-54.Config')
    _, _, show_im = net.cated_infer(new_frame)
    cv2.imshow('shrink_frame', show_im)
    key = cv2.waitKey(1)
    if key == ord('a') & 0xff:
        left_move(200)
        continue
    if key == ord('d') & 0xff:
        right_move(200)
        continue
    if key == ord('w') & 0xff:
        up_move(200)
        continue
    if key == ord('s') & 0xff:
        down_move(200)
        continue
    if key == ord('j') & 0xff:
        left_move(50)
        continue
    if key == ord('l') & 0xff:
        right_move(50)
        continue
    if key == ord('i') & 0xff:
        up_move(50)
        continue
    if key == ord('k') & 0xff:
        down_move(50)
        continue
    if key == ord('q') & 0xff:
        break
    
    


