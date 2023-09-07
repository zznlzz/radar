# -*- coding: UTF-8 -*-
import argparse
import time
from pathlib import Path
import sys
import os

import numpy as np
import cv2
import torch
import torch.backends.cudnn as cudnn
from numpy import random
import copy

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

from models.experimental import attempt_load
from utils.datasets import letterbox, img_formats, vid_formats, LoadImages, LoadStreams
from utils.general import check_img_size, non_max_suppression_face, apply_classifier, scale_coords, xyxy2xywh, \
    strip_optimizer, set_logging, increment_path
from utils.plots import plot_one_box
from utils.torch_utils import select_device, load_classifier, time_synchronized
sys.path.append('/home/pheonix/NewDisk/about_radar/Radar_structure/Our_project')
from radar_class.camera import Camera_Thread
cap = Camera_Thread(0, strict_mode=False)

def scale_coords_landmarks(img1_shape, coords, img0_shape, ratio_pad=None):
    # Rescale coords (xyxy) from img1_shape to img0_shape
    if ratio_pad is None:  # calculate from img0_shape
        gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])  # gain  = old / new
        pad = (img1_shape[1] - img0_shape[1] * gain) / 2, (img1_shape[0] - img0_shape[0] * gain) / 2  # wh padding
    else:
        gain = ratio_pad[0][0]
        pad = ratio_pad[1]

    coords[:, [0, 2, 4, 6]] -= pad[0]  # x padding
    coords[:, [1, 3, 5, 7]] -= pad[1]  # y padding
    coords[:, :10] /= gain
    #clip_coords(coords, img0_shape)
    coords[:, 0].clamp_(0, img0_shape[1])  # x1
    coords[:, 1].clamp_(0, img0_shape[0])  # y1
    coords[:, 2].clamp_(0, img0_shape[1])  # x2
    coords[:, 3].clamp_(0, img0_shape[0])  # y2
    coords[:, 4].clamp_(0, img0_shape[1])  # x3
    coords[:, 5].clamp_(0, img0_shape[0])  # y3
    coords[:, 6].clamp_(0, img0_shape[1])  # x4
    coords[:, 7].clamp_(0, img0_shape[0])  # y4
    #coords[:, 8].clamp_(0, img0_shape[1])  # x5
    #coords[:, 9].clamp_(0, img0_shape[0])  # y5
    return coords

def show_results(img, xyxy, conf, landmarks, class_num):
    h,w,c = img.shape
    tl = 1 or round(0.002 * (h + w) / 2) + 1  # line/font thickness
    x1 = int(xyxy[0])
    y1 = int(xyxy[1])
    x2 = int(xyxy[2])
    y2 = int(xyxy[3])
    img = img.copy()
    
    #cv2.rectangle(img, (x1,y1), (x2, y2), (0,255,0), thickness=tl, lineType=cv2.LINE_AA)

    clors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0)]

    point = []
    for i in range(4): 
        point.append(int(landmarks[2 * i]))
        point.append(int(landmarks[2 * i + 1]))
        point_x = int(landmarks[2 * i])
        point_y = int(landmarks[2 * i + 1])
        cv2.circle(img, (point_x, point_y), tl+1, clors[i], -1)
    cv2.line(img,(point[0],point[1]),(point[4],point[5]),(0,0,255),5)
    cv2.line(img,(point[2],point[3]),(point[6],point[7]),(0,0,255),5)
    cv2.line(img,(point[0],point[1]),(point[2],point[3]),(0,0,255),5)
    cv2.line(img,(point[4],point[5]),(point[6],point[7]),(0,0,255),5)
    #print(point)
    

    tf = max(tl - 1, 1)  # font thickness
    label = str(conf)[:5]
    cv2.putText(img, "class:"+str(class_num), (x1+50, y1 - 2), 0, tl / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)
    cv2.putText(img, label, (x1, y1 - 2), 0, tl / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)
    return img

def shift_2_torch_tensor(im):
    im = im.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
    im_input = np.ascontiguousarray(im)  # contiguous
    
    im_input = torch.from_numpy(im_input).to('cuda:0')
    im_input = im_input.half()  # uint8 to fp16/32
    im_input /= 255  # 0 - 255 to 0.0 - 1.0
    if len(im_input.shape) == 3:
        im_input = im_input[None]  # expand for batch dim
    return im_input

def diy_detect(model, device, view_img):
    img_size = 640
    conf_thres = 0.6
    iou_thres = 0.5
    imgsz=(640, 640)

    k = cv2.waitKey(1)

    while True:
        if not cap.is_open():
            cap.open()

        # receive one frame
        flag, frame = cap.read()

        if not flag:
            time.sleep(0.1)
            continue

        original_img = frame
        im0 = frame
        img = letterbox(original_img,  new_shape=[640, 640], auto=False)[0]
        img = shift_2_torch_tensor(img)
        # Inference
        model.half()
        pred = model(img)[0]

        pred = non_max_suppression_face(pred, conf_thres, iou_thres)
        print(len(pred[0]), 'face' if len(pred[0]) == 1 else 'faces')

        # Process detections
        for i, det in enumerate(pred):  # detections per image
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                
                
                det[:, 5:13] = scale_coords_landmarks(img.shape[2:], det[:, 5:13], im0.shape).round()
                
                for j in range(det.size()[0]):
                    xyxy = det[j, :4].view(-1).tolist()
                    conf = det[j, 4].cpu().numpy()
                    landmarks = det[j, 5:13].view(-1).tolist()
                    class_num = det[j, 13].cpu().numpy()
                    
                    im0 = show_results(im0, xyxy, conf, landmarks, class_num)
            
            if view_img:
                cv2.imshow('result', im0)
                k = cv2.waitKey(1)

        if k & 0xff == ord('q'):
            break

def load_model(weights, device):
    model = attempt_load(weights, map_location=device)  # load FP32 model
    return model

diy_detect(load_model('/home/pheonix/NewDisk/about_radar/Radar_structure/Our_project/weights/detail_best.pt', 
                      device='cuda:0'), 
           'cuda:0', True)

