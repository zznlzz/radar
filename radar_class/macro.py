enemy: int = 1  # 0:red, 1:blue
home_test = False
debug = True

##################################  路径相关  #################################################################
CAMERA_CONFIG_DIR = 'Camera_config'
VIDEO_SAVE_DIR = 'save_stuff/video'
CACHE_CONFIG_SAVE_DIR = 'save_stuff'
LIDAR_TOPIC_NAME = "/livox/lidar" # 雷达PointCloud节点名称
PC_STORE_DIR = "point_record" # 录制点云保存位置
MAP_PATH = 'save_stuff/map.png'
LOCATION_SAVE_DIR = 'save_stuff/position'
# NET_PATH = 'weights/detail_best.pt'
NET_PATH = 'weights/640x640_large.pt'
model_imgsz = (640, 640)



armor_list = ['R1','R2','R3','R4','R5','B1','B2','B3','B4','B5'] # 雷达站实际考虑的各个装甲板类
preview_location = [(100, 100)]
map_size = [716,384]
img_sz = [3088, 2064]
position_choice = 'y'

color2enemy = {"red":0,"blue":1}
enemy2color = ['red','blue']

location_targets = {
    # enemy:red
    # red_base -> blue_outpost -> b_rt -> b_lt
    # enemy:blue
    # blue_base -> red_outpost -> r_rt -> r_lt
    'home_test': # 家里测试，填自定义类似于赛场目标的空间位置
    {
        'red_base': [9.3, 0.85, 1.96],
        'blue_outpost': [3.2, -0.6, 0.06],
        'red_outpost': [9.3-3.2, 4.65+0.6, 0.06],
        'blue_base': [0, 4.65-0.85, 1.96],
        'r_rt': [9.3-4.7, 4.65-4.6, 1.15],  # r0 right_top
        'r_lt': [0, 4.65-3.45, 2.19],  # r0 left_top
        # 'b_rt': [9.3, 3.9, 1.5],  # b0 right_top
        'b_rt': [4.7, 4.6, 1.15],  # b0 right_top
        'b_lt': [9.3, 3.45, 2.19]  # b0 right_top
        # 'red_base': [4.2, 2.1, 1.76],
        # 'blue_outpost': [4.15, 3.9, 1.76],
        # 'b_rt': [6.1, 5.8, 0],  # b0 right_top
        # 'b_lt': [6.5, 8.1, 2.9] 
        
    },

    'game': # 按照官方手册填入
        {
            # 'red_base': [1.760, -15. + 7.539, 0.200 + 0.920],  # red base
            # 'blue_outpost': [16.776, -15. + 12.565, 1.760],  # blue outpost
            # 'red_outpost': [11.176, -15. + 2.435, 1.760],  # red outpost
            # 'blue_base': [26.162, -15. + 7.539, 0.200 + 0.920],  # blue base
            # 'r_rt': [8.805, -5.728 - 0.660, 0.120 + 0.495],  # r0 right_top
            # 'r_lt': [8.805, -5.728, 0.120 + 0.495],  # r0 left_top
            # 'b_rt': [19.200, -9.272 + 0.660, 0.120 + 0.495],  # b0 right_top
            # 'b_lt': [19.200, -9.272, 0.120 + 0.495]  # b0 left_top
            'red_base': [1.760, 7.539, 0.200 + 0.920],  # red base
            'blue_outpost': [16.776, 12.565, 1.760],  # blue outpost
            'red_outpost': [11.176, 2.435, 1.760],  # red outpost
            'blue_base': [26.162, 7.539, 0.200 + 0.920],  # blue base
            'r_rt': [8.805, -5.728 - 0.660 + 15. , 0.120 + 0.495],  # r0 right_top
            'r_lt': [8.805, -5.728 + 15. , 0.120 + 0.495],  # r0 left_top
            'b_rt': [19.200, -9.272 + 0.660 + 15. , 0.120 + 0.495],  # b0 right_top
            'b_lt': [19.200, -9.272 + 15. , 0.120 + 0.495]  # b0 left_top
        }
}

position_alarm = {
    'enemy_is_red':[
        ([1], [[4.73, 15.],[8.94, 15.],[6.636, 15-4.1],[4.73, 15-4.06]], 1),
        ([1, 3, 4, 5], [[12.12, 13.763],[12.893, 13.224], [10.072, 9.265], [9.132, 9.5]], 2),
        ([1,3,4,5], [[5.76, 0.797], [12.487, 0.797], [12.487, 0.05], [5.76, 0.05]], 3)

    ],
    'enemy_is_blue':[
        ([101], [[28-4.73,0],[28-8.94,0],[28-6.636,4.1],[28-4.73,4.06]], 1),
        ([101, 103, 104, 105], [[17.928, 5.735],[18.868, 5.5],[15.88, 1.237],[15.107, 1.776]], 2),
        ([101, 103, 104, 105], [[15.513, 14.817],[22.24, 14.95],[22.24, 14.203],[15.513, 14.07]], 3)
    ]
}

receiver_id = [[103,104,105],
[3,4,5]
]
