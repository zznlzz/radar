from network.RM_4_points_yolov5 import detect
import torch
import numpy as np
import cv2
import sys
sys.path.append('../single_version/')
from radar_class.macro import debug
class Predictor:
    # hard code part
    view_img = True # 是否显示图像的标志位
    fp16 = True # 是否使用半精度浮点数进行推理的标志位
    conf_thres = 0.5
    iou_thres = 0.5
    def __init__(self, weight, model_imgsz = (640, 640)):
        self.select_device()
        model = detect.load_model(weight, device=self.device)
        self.model = model.half() if self.fp16 else model # 将加载的模型转换为半精度浮点数（half())或保持原始精度
        self.img_sz = model_imgsz # 将模型输入图像的大小存储在self.img_sz
        
    def infer(self, frame): # 推理函数
        im0 = frame.copy()
        pred, img_tensor = self.run(frame) # 运行推理
        location, show_im = self.post_processing(pred, img_tensor, im0) # 后处理
        if location is None:
            return False, location, frame
        else:
            return True, np.float32(location), show_im
        
    def infer_bias(self, src_location, bias:tuple): # 对目标位置坐标进行偏移
        bias_x, bias_y = bias[0], bias[1]
        src_location[:, 0] += bias_x # 关键点坐标
        src_location[:, 1] += bias_y
        src_location[:, 2] += bias_x
        src_location[:, 3] += bias_y
        src_location[:, 4] += bias_x
        src_location[:, 5] += bias_y
        src_location[:, 6] += bias_x
        src_location[:, 7] += bias_y

        src_location[:, 10] += bias_x # 边界框坐标
        src_location[:, 11] += bias_y
        src_location[:, 12] += bias_x
        src_location[:, 13] += bias_y

    def cated_infer(self, frame):
        frame_height, frame_width = frame.shape[0], frame.shape[1]
        first_frame = frame[0:frame_height//2, 0:frame_width//2]
        second_frame = frame[0:frame_height//2, frame_width//2:frame_width]
        third_frame = frame[frame_height//2:frame_height, 0:frame_width//2]
        forth_frame = frame[frame_height//2:frame_height, frame_width//2:frame_width]
        cated_frame = [first_frame, second_frame, third_frame, forth_frame] # 将图像分割成四个部分

        pred, img_tensor = self.com_run(first_frame, second_frame, third_frame, forth_frame)
        return self.com_post_process(pred, img_tensor, cated_frame, 
    
                                                             frame_height, frame_width)
    

    
            
    def com_run(self, first_frame, second_frame, third_frame, forth_frame):
        first_frame = detect.letterbox(first_frame, self.img_sz, auto=False)[0]
        second_frame = detect.letterbox(second_frame, self.img_sz, auto=False)[0]
        third_frame = detect.letterbox(third_frame, self.img_sz, auto=False)[0]
        forth_frame = detect.letterbox(forth_frame, self.img_sz, auto=False)[0]
        
        img_tensor = self.com_shift(first_frame, second_frame, third_frame, forth_frame)
        pred = self.model(img_tensor)[0] # 这个函数返回的结果有多个，但是我只想要第一个结果， 可能同时返回了一些其他的信息，例如说有没有成功运行。
        pred = detect.non_max_suppression_face(pred, self.conf_thres, self.iou_thres)
        return pred, img_tensor
            
    def com_post_process(self, pred, img_tensor, im0, frame_height, frame_width):
        total_locations = [] # 存储合并后的目标位置信息
        # 我们要首先保证pred是有长度的
        location_1, show_im_1 = self.post_processing([pred[0]], img_tensor[0][None], im0[0]) # [4, 3, H, W]
        if not location_1 is None:
            total_locations.append(location_1)

        location_2, show_im_2 = self.post_processing([pred[1]], img_tensor[1][None], im0[1])
        if not location_2 is None:
            self.infer_bias(location_2, (frame_width//2, 0))
            total_locations.append(location_2)

        location_3, show_im_3 = self.post_processing([pred[2]], img_tensor[2][None], im0[2])
        if not location_3 is None:
            self.infer_bias(location_3, (0, frame_height//2))
            total_locations.append(location_3)

        location_4, show_im_4 = self.post_processing([pred[3]], img_tensor[3][None], im0[3])
        if not location_4 is None:
            self.infer_bias(location_4, (frame_width//2, frame_height//2))
            total_locations.append(location_4)

        one_two = np.concatenate([show_im_1, show_im_2], axis=1) # 水平拼接 == torch.cat [H, W, C]
        three_four = np.concatenate([show_im_3, show_im_4], axis=1)
        total_im = np.concatenate([one_two, three_four], axis=0) # 垂直拼接
        
        if len(total_locations):
            total_locations = torch.cat(total_locations, dim=0)
            return True, np.float32(total_locations), total_im
        else:
            return False, None, total_im


        
    def composition_infer(self, frame): # 不用这个函数了
        total_locations = []
        frame_height, frame_width = frame.shape[0], frame.shape[1]

        # 第一个裁剪的图案
        first_frame = frame[0:frame_height//2, 0:frame_width//2] # [4，3，H, W] 原来只运行了一次     现在[1, 3, H, W] 运行了4次 O(4)
        pred, img_tensor = self.run(first_frame)
        show_im_1 = first_frame
        if len(pred[0]):
            location_1, show_im_1 = self.post_processing(pred, img_tensor, first_frame)
            total_locations.append(location_1) 

        # 第二个裁剪的图案
        second_frame = frame[0:frame_height//2, frame_width//2:frame_width]
        pred, img_tensor = self.run(second_frame)
        show_im_2 = second_frame
        if len(pred[0]):
            location_2, show_im_2 = self.post_processing(pred, img_tensor, second_frame)
            self.infer_bias(location_2, (frame_width//2, 0))
            total_locations.append(location_2)

        # 第三个裁剪的图案
        third_frame = frame[frame_height//2:frame_height, 0:frame_width//2]
        pred, img_tensor = self.run(third_frame)
        show_im_3 = third_frame
        if len(pred[0]):
            location_3, show_im_3 = self.post_processing(pred, img_tensor, third_frame)
            self.infer_bias(location_3, (0, frame_height//2))
            total_locations.append(location_3)

        # 第四个裁剪的图案
        forth_frame = frame[frame_height//2:frame_height, frame_width//2:frame_width]
        pred, img_tensor = self.run(forth_frame)
        show_im_4 = forth_frame
        if len(pred[0]):
            location_4, show_im_4 = self.post_processing(pred, img_tensor, forth_frame)
            self.infer_bias(location_4, (frame_width//2, frame_height//2))
            total_locations.append(location_4)

        if len(total_locations):
            total_locations = torch.cat(total_locations, dim=0)
            one_two = np.concatenate([show_im_1, show_im_2], axis=1)
            three_four = np.concatenate([show_im_3, show_im_4], axis=1)
            total_im = np.concatenate([one_two, three_four], axis=0)
            # print('the x:', total_locations[0][10], 'the y:', total_locations[0][11])
            return True, np.float32(total_locations), total_im
        else:
            return False, None, frame



    
    def run(self, frame): # 这里的frame是一个numpy的数组——待推理的图像帧
        img = detect.letterbox(frame,  new_shape=self.img_sz, auto=False)[0] # 调整图像尺寸以适应模型的输入尺寸
        img_tensor = self.shift_2_torch_tensor(img) # 将图像转换为PyTorch张量
        pred = self.model(img_tensor)[0]
        pred = detect.non_max_suppression_face(pred, self.conf_thres, self.iou_thres) # 非极大值抑制
        return pred, img_tensor
        
    def post_processing(self, pred, img_tensor, im0):# 参数为：模型的预测结果，输入到模型的图像张量，原始图像
        
        det = pred[0] # 因为这里，在同一时刻，我们只会有一张图片被输入到模型当中， len(pred)==1
        if len(det): # 判断预测结果是否为空
            det[:, :4] = detect.scale_coords(img_tensor.shape[2:], det[:, :4], im0.shape).round() # 将边界框坐标转换为原始图像的绝对坐标
            det[:, 5:13] = detect.scale_coords_landmarks(img_tensor.shape[2:], det[:, 5:13], im0.shape).round() # 将关键点坐标转换为原始图像的绝对坐标
            
            cat_landmark = det[:, 5:13] # 调整后的关键点坐标
            cat_conf = det[:, 4].reshape(-1, 1) # 调整后的置信度, 这里reshape(-1, 1)是为了后面的torch.cat()拼接
            cat_class = det[:, 13].reshape(-1, 1) # 调整后的类别
            cat_xyxy = det[:, :4] # 调整后的边界框坐标
            new_det = torch.cat([cat_landmark, cat_conf, cat_class, cat_xyxy],dim=1) # 将关键点坐标、置信度、类别信息和边界框坐标按列进行拼接，形成新的预测结果
            # 0-7:关键点坐标，8:置信度，9:类别，10-13:边界框坐标
            if debug: # 绘制，可视化
                for j in range(det.size()[0]):
                    xyxy = det[j, :4].view(-1).tolist()
                    conf = det[j, 4].cpu().numpy()
                    landmarks = det[j, 5:13].view(-1).tolist()
                    class_num = det[j, 13].cpu().numpy()
                    im0 = detect.show_results(im0, xyxy, conf, landmarks, class_num)

            # for j in range(det.size()[0]):
            #     xyxy = cat_xyxy[j].view(-1).tolist()
            #     conf = cat_conf[j].cpu().view(-1).numpy()
            #     landmarks = cat_landmark[j].view(-1).tolist()
            #     class_num = cat_class[j].cpu().numpy()
                
            #     im0 = detect.show_results(im0, xyxy, conf, landmarks, class_num)
            
        else:
            new_det = None
        # 如果检测到目标，就输出检测的结果，如果没有，就输出原图像。
        return new_det.cpu() if new_det!=None else None, im0
            
            
    def com_shift(self, first_frame, second_frame, third_frame, forth_frame):
        first_frame = self.shift_2_torch_tensor(first_frame) 
        second_frame = self.shift_2_torch_tensor(second_frame) 
        third_frame = self.shift_2_torch_tensor(third_frame)
        forth_frame = self.shift_2_torch_tensor(forth_frame)

        return torch.cat([first_frame, second_frame, third_frame, forth_frame])  # [B, C, H, W] dim=0 --> B dim=1 --> C 
        # 堆叠之后的size应该是：[4, 3, H, W]
        
    def shift_2_torch_tensor(self, im):# 将图像转换为PyTorch张量，im是一个numpy的数组
        im = im.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
        # 将原始数组的轴重新排列，使得通道轴（原始索引为2）成为第一个轴，高度轴（原始索引为0）成为第二个轴，宽度轴（原始索引为1）成为第三个轴
        im_input = np.ascontiguousarray(im)  # contiguous
        
        im_input = torch.from_numpy(im_input).to(self.device)
        im_input = im_input.half() if self.fp16 else im_input.float()  # uint8 to fp16/32
        im_input /= 255  # 0 - 255 to 0.0 - 1.0
        if len(im_input.shape) == 3:
            im_input = im_input[None]  # expand for batch dim
        return im_input
        
    
    def select_device(self):
        if torch.cuda.is_available():
            self.device = f'cuda:0'
            return 
        self.device = f'cpu'
        