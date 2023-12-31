import serial
import numpy as np
import offical_Judge_Handler
import binascii  #在BIN(二进制)和ASCII之间转换
import struct  #将数据作为完整的结构传输，用struct模块进行处理
from binascii import *
from crcmod import *
from offical_Judge_Handler import crc16Add
import time

buffercnt = 0
buffer = [0]
buffer *= 1000
cmdID = 0
indecode = 0

def read(ser):
    global buffercnt
    buffercnt = 0
    global buffer
    global cmdID
    global indecode
    # TODO:qt thread

    while True:
        s = ser.read(1)
        s = int().from_bytes(s, 'big')
        # doc.write('s: '+str(s)+'        ')

        if buffercnt > 50:
            buffercnt = 0

        print(buffercnt)
        buffer[buffercnt] = s
        # doc.write('buffercnt: '+str(buffercnt)+'        ')
        # doc.write('buffer: '+str(buffer[buffercnt])+'\n')
        print(hex(buffer[buffercnt]))

        if buffercnt == 0:
            if buffer[buffercnt] != 0xa5:
                buffercnt = 0
                continue

        if buffercnt == 5:
            if offical_Judge_Handler.myVerify_CRC8_Check_Sum(id(buffer), 5) == 0:
                buffercnt = 0
                if buffer[buffercnt] == 0xa5:
                    buffercnt = 1
                continue

        if buffercnt == 7:
            cmdID = (0x0000 | buffer[5]) | (buffer[6] << 8)
            print("cmdID")
            print(cmdID)

        if buffercnt == 10 and cmdID == 0x0002:
            if offical_Judge_Handler.myVerify_CRC16_Check_Sum(id(buffer), 10):
                Referee_Game_Result()
                buffercnt = 0
                if buffer[buffercnt] == 0xa5:
                    buffercnt = 1
                continue

        if buffercnt == 20 and cmdID == 0x0001:

            if offical_Judge_Handler.myVerify_CRC16_Check_Sum(id(buffer), 20):
                # 比赛阶段信息
                UART_passer.Referee_Update_GameData()
                buffercnt = 0
                if buffer[buffercnt] == 0xa5:
                    buffercnt = 1
                continue

        if buffercnt == 41 and cmdID == 0x0003:
            if offical_Judge_Handler.myVerify_CRC16_Check_Sum(id(buffer), 41):
                # 各车血量
                UART_passer.Referee_Robot_HP()
                buffercnt = 0
                if buffer[buffercnt] == 0xa5:
                    buffercnt = 1
                continue

        if buffercnt == 12 and cmdID == 0x0004:
            if offical_Judge_Handler.myVerify_CRC16_Check_Sum(id(buffer), 12):
                Referee_dart_status()
                buffercnt = 0
                if buffer[buffercnt] == 0xa5:
                    buffercnt = 1
                continue

        if buffercnt == 13 and cmdID == 0x0101:
            if offical_Judge_Handler.myVerify_CRC16_Check_Sum(id(buffer), 13):
                Referee_event_data()
                buffercnt = 0
                if buffer[buffercnt] == 0xa5:
                    buffercnt = 1
                continue

        if buffercnt == 13 and cmdID == 0x0102:
            if offical_Judge_Handler.myVerify_CRC16_Check_Sum(id(buffer), 13):
                Refree_supply_projectile_action()
                buffercnt = 0
                if buffer[buffercnt] == 0xa5:
                    buffercnt = 1
                continue

        if buffercnt == 11 and cmdID == 0x0104:
            if offical_Judge_Handler.myVerify_CRC16_Check_Sum(id(buffer), 11):
                Refree_Warning()
                buffercnt = 0
                if buffer[buffercnt] == 0xa5:
                    buffercnt = 1
                continue

        if buffercnt == 10 and cmdID == 0x0105:
            if offical_Judge_Handler.myVerify_CRC16_Check_Sum(id(buffer), 10):
                Refree_dart_remaining_time()
                buffercnt = 0
                if buffer[buffercnt] == 0xa5:
                    buffercnt = 1
                continue

        if buffercnt == 17 and cmdID == 0x301:  # 2bite数据
            if offical_Judge_Handler.myVerify_CRC16_Check_Sum(id(buffer), 17):
                # 比赛阶段信息
                UART_passer.Receive_Robot_Data()
                buffercnt = 0
                if buffer[buffercnt] == 0xa5:
                    buffercnt = 1
                continue

        if buffercnt == 25 and cmdID == 0x202:  # 雷达没有
            if offical_Judge_Handler.myVerify_CRC16_Check_Sum(id(buffer), 25):
                buffercnt = 0
                if buffer[buffercnt] == 0xa5:
                    buffercnt = 1
                continue

        if buffercnt == 25 and cmdID == 0x203:  # 雷达没有
            if offical_Judge_Handler.myVerify_CRC16_Check_Sum(id(buffer), 25):
                buffercnt = 0
                if buffer[buffercnt] == 0xa5:
                    buffercnt = 1
                continue

        if buffercnt == 27 and cmdID == 0x201:  # 雷达没有
            if offical_Judge_Handler.myVerify_CRC16_Check_Sum(id(buffer), 27):
                buffercnt = 0
                if buffer[buffercnt] == 0xa5:
                    buffercnt = 1
                continue

        if buffercnt == 10 and cmdID == 0x204:  # 雷达没有
            if offical_Judge_Handler.myVerify_CRC16_Check_Sum(id(buffer), 10):
                buffercnt = 0
                if buffer[buffercnt] == 0xa5:
                    buffercnt = 1
                continue

        if buffercnt == 10 and cmdID == 0x206:  # 雷达没有
            if offical_Judge_Handler.myVerify_CRC16_Check_Sum(id(buffer), 10):
                buffercnt = 0
                if buffer[buffercnt] == 0xa5:
                    buffercnt = 1
                continue

        if buffercnt == 13 and cmdID == 0x209:  # 雷达没有
            if offical_Judge_Handler.myVerify_CRC16_Check_Sum(id(buffer), 13):
                buffercnt = 0
                if buffer[buffercnt] == 0xa5:
                    buffercnt = 1
                continue

        if buffercnt == 16 and cmdID == 0x0301:
            if offical_Judge_Handler.myVerify_CRC16_Check_Sum(id(buffer), 16):
                # Refree_map_stop()
                buffercnt = 0
                if buffer[buffercnt] == 0xa5:
                    buffercnt = 1
                continue

        # if buffercnt == 24 and cmdID == 0x0303:
        #     if offical_Judge_Handler.myVerify_CRC16_Check_Sum(id(buffer), 24):
        #         # 云台手通信
        #         Refree_Arial_Message()
        #         buffercnt = 0
        #         if buffer[buffercnt] == 0xa5:
        #             buffercnt = 1
        #         continue

        buffercnt += 1


enemy = 0



class Robomst_UART:
    debug = True
    home_width = 9.3
    home_height = 4.65
    real_width = 28
    real_height = 15
    def __init__(self):
        self.robot_location = None
        self.Id_red = 1
        self.Id_blue = 101
        self.specific_color = {0:[1, 2 ,3 ,4 ,5, 7], 1: [101, 102, 103, 104, 105, 107]}
        self.between_car_len = b'\x0a'
        self.send_id = 9 if enemy else 109
        
    def create_SOF(self, datalen):
        buffer = [0]
        buffer = buffer * 5
        buffer[0] = 0xa5
        buffer[1] = datalen
        buffer[2] = 0
        buffer[3] = 0
        buffer[4] = offical_Judge_Handler.myGet_CRC8_Check_Sum(id(buffer), 4, 0xff)
        
        return bytes(bytearray(buffer))

    def push_loc(self, location):
        self.robot_location = np.float32(location)
        
    def get_position(self):
        return self.robot_location
    
    def xy_check(self, x:float, y:float, ):
        new_x = x*self.real_width/self.home_width
        new_y = y*self.real_height/self.home_height

        return new_x, new_y
    
    def radar_map(self, ID, X, Y, ser, whether_new=False):
        Z = 1
        try:
            SOF = (b'\xa5' b'\x0a' b'\x00' b'\x00' b'\x37') if whether_new else (b'\xa5' b'\x0e' b'\x00' b'\x00' b'\x37')
            CMDID = (b'\x05' b'\x03')
            data = struct.pack("<1H2f",ID,X,Y) if whether_new else struct.pack("<1H3f",ID,X,Y,Z)
            data1 = SOF + CMDID + data
            decodeData = binascii.b2a_hex(data1).decode('utf-8')
            data_last,hexer = crc16Add(decodeData)
            ser.write(hexer)

        except Exception as e:
            print("serial write data has ERROR: \033[0m", e)

    def radar_map_test(self, ID, X, Y, ser):
        try:
            Z = 1
            SOF = self.create_SOF(14)
            CMDID = (b'\x05' b'\x03')
            data = struct.pack("<1H3f",ID,X,Y,Z)
            data1 = SOF + CMDID + data
            decodeData = binascii.b2a_hex(data1).decode('utf-8')
            data_last,hexer = crc16Add(decodeData)
            ser.write(hexer)
        except:
            print(f'The ID:{ID}, and the X:{X} and the Y:{Y}')
            
    def radar_between_car(self, data:list, data_id:int, datalenth:int, receiver_id, ser):
        SOF = self.create_SOF(datalenth+6) # datalength 指的是我要发的数据长度，前面还有6位的字节漂移
        CMDID = (b'\x01' b'\x03')
        # data = struct.pack("<4f", data[0], data[1], data[2], data[3])
        data = bytes(bytearray(data))
        dataid_sender_receiver = struct.pack('<3H',data_id, self.send_id, receiver_id)
        data_sum = SOF + CMDID + dataid_sender_receiver + data
        decodeData = binascii.b2a_hex(data_sum).decode('utf-8')
        data_last,hexer = crc16Add(decodeData)
        ser.write(hexer)
        
 
    
    def Referee_Transmit_BetweenCar(self, dataID, ReceiverId, data, ser):
        '''
        雷达站发送车间通信包函数
        '''
        buffer = [0]
        buffer = buffer * 200

        buffer[0] = 0xA5  # 数据帧起始字节，固定值为 0xA5
        buffer[1] = 10  # 数据帧中 data 的长度,占两个字节
        buffer[2] = 0
        buffer[3] = 0  # 包序号
        buffer[4] = offical_Judge_Handler.myGet_CRC8_Check_Sum(id(buffer), 5 - 1, 0xff)  # 帧头 CRC8 校验
        buffer[5] = 0x01
        buffer[6] = 0x03
        # 自定义内容ID
        buffer[7] = dataID & 0x00ff
        buffer[8] = (dataID & 0xff00) >> 8
        # 发自雷达站
        if enemy:
            buffer[9] = 9
        else:
            buffer[9] = 109
        buffer[10] = 0
        buffer[11] = ReceiverId
        buffer[12] = 0
        # 自定义内容数据段
        buffer[13] = data[0]
        buffer[14] = data[1]
        buffer[15] = data[2]
        buffer[16] = data[3]

        offical_Judge_Handler.Append_CRC16_Check_Sum(id(buffer), 10 + 9)  # 等价的

        buffer_tmp_array = [0]
        buffer_tmp_array *= 9 + 10

        for i in range(9 + 10):
            buffer_tmp_array[i] = buffer[i]
        ser.write(bytearray(buffer_tmp_array))

    
    def Referee_Transmit_Map(self, cmdID, datalength, targetId, x, y, ser):
        '''
        小地图包 

        x，y采用np.float32转换为float32格式
        '''
        buffer = [0]
        buffer = buffer * 200

        buffer[0] = 0xA5  # 数据帧起始字节，固定值为 0xA5
        buffer[1] = (datalength) & 0x00ff  # 数据帧中 data 的长度,占两个字节
        buffer[2] = ((datalength) & 0xff00) >> 8
        buffer[3] = 0  # 包序号
        buffer[4] = offical_Judge_Handler.myGet_CRC8_Check_Sum(id(buffer), 5 - 1, 0xff)  # 帧头 CRC8 校验
        buffer[5] = cmdID & 0x00ff
        buffer[6] = (cmdID & 0xff00) >> 8

        buffer[7] = targetId
        buffer[8] = 0
        buffer[9] = bytes(x)[0]
        buffer[10] = bytes(x)[1]
        buffer[11] = bytes(x)[2]
        buffer[12] = bytes(x)[3]
        buffer[13] = bytes(y)[0]
        buffer[14] = bytes(y)[1]
        buffer[15] = bytes(y)[2]
        buffer[16] = bytes(y)[3]
        buffer[17:20] = [0] * 4 ## 朝向，直接赋0，协议bug，不加这一项无效

        offical_Judge_Handler.Append_CRC16_Check_Sum(id(buffer), datalength + 9)  # 等价的

        buffer_tmp_array = [0]
        buffer_tmp_array *= 9 + datalength

        for i in range(9 + datalength):
            buffer_tmp_array[i] = buffer[i]
        ser.write(bytearray(buffer_tmp_array))
    

            
    def Robot_Data_Transmit_Map(self, ser, pred_loc):
        for row in pred_loc:
            target_id = int(row[0])
            if target_id in self.specific_color[enemy]:
                x, y = float(row[1]), float(row[2])
                x, y = self.xy_check(x, y)
                self.radar_map_test(target_id, x, y, ser)
                time.sleep(0.1)
            
            
if __name__ == "__main__":
    ser = serial.Serial('/dev/ttyUSB0', 115200, 8, 'N', 1, timeout=0.01)
    
    pred_loc = np.array([[7, 4, 3],
                         [1, 7, 1]])
    uart = Robomst_UART()
    # uart.Robot_Data_Transmit_Map(ser, pred_loc)
    
    dataID = 0x020F
    receive_id = 103

    while 1:
        # read(ser=ser)
        # uart.Referee_Transmit_BetweenCar(dataID=dataID, ReceiverId=receive_id, data=[0, 1, 2, 3], ser=ser)
        # time.sleep(0.1)
        # uart.Robot_Data_Transmit_Map(ser, pred_loc)
        uart.radar_between_car(data=[0, 8, 9, 3], data_id=dataID, datalenth=4, receiver_id=receive_id, ser=ser)
        time.sleep(0.1)
    
        
    
            