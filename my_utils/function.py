import yaml
import numpy as np
from radar_class.macro import CAMERA_CONFIG_DIR

def read_yaml(camera_type):
    '''
    读取相机标定参数,包含外参，内参，以及关于雷达的外参

    :param camera_type:相机编号
    :return: 读取成功失败标志位，相机内参，畸变系数，和雷达外参，相机图像大小
    '''
    yaml_path = "{0}/camera_{1}.yaml".format(CAMERA_CONFIG_DIR, camera_type)
    try:
        with open(yaml_path, 'rb') as f:
            res = yaml.load(f, Loader=yaml.FullLoader)
            K_0 = np.float32(res["K_0"]).reshape(3, 3)
            C_0 = np.float32(res["C_0"])
            E_0 = np.float32(res["E_0"]).reshape(4, 4)
            imgsz = tuple(res['ImageSize'])

        return True, K_0, C_0, E_0, imgsz
    except Exception as e:
        print("[ERROR] {0}".format(e))
        return False, None, None, None, None
    
def armor_filter(armors):
    '''
    装甲板去重

    :param armors:input np.ndarray (N,fp+conf+cls+img_no+bbox)

    :return: armors np.ndarray 每个id都最多有一个装甲板
    '''

    # 直接取最高置信度
    ids = [1, 2, 3, 4, 5, 8, 9, 10, 11, 12] # 1-5分别为b1-5 8-12分别为r1-5
    if isinstance(armors, np.ndarray):
        results = []
        for i in ids:
            mask = armors[:, 9] == i
            armors_mask = armors[mask]
            if armors_mask.shape[0]:
                armor = armors_mask[np.argmax(armors_mask[:, 8])]
                results.append(armor)
        if len(results):
            armors = np.stack(results, axis=0)
            return armors
        else:
            return None
    else:
        return None