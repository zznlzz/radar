```
    def __init__(self, camera_type, load_path:str=None, strict_mode=False):
        self._camera_type = camera_type
        self._date = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        self._open = False
        self._cap = None
        self._load_path = load_path
        self.strict_mode = strict_mode
        self.open()
```
+ **初始化**
1. `self._camera_type`：存储相机类型
2. `self._date`：存储当前时间
3. `self._open`：初始化为`False`，表示相机打开状态
4. `self._cap`: 初始化为`None`，存储相机对象
5. `self._load_path`: 表示加载参数的路径,默认为`None`
6. `strict_mode`: 表示是否启动严格模式，默认为`False`
7. `self._open()`: 打开相机
---
```
    def open(self):
        if not self._open:
            self._open, self.cap = self.open_cam(self._camera_type, self._date)
```
+ **打开相机**
1. 检查`self._open`的值来确定相机是否已经打开
2. 如果相机尚未打开，则调用`open_cam`方法，并传递`self._camera_type`（相机类型）和`self._date`（日期时间）
    - 第一个返回值赋值给`self._open`，表示相机是否成功打开
    - 第二个返回值赋值给`self.cap`，用于存储相机对象
---
```
    def is_open(self):
        '''
        check the camera opening state
        '''
        return self._open
```
+ **检查相机是否打开**
+ 对外的接口函数
---
```
    def open_cam(self, camera_type, date):
        cap = None
        init_flag = False
        try:
            cap = HT_Camera(camera_type, date, self.strict_mode)
            r, frame = cap.read()  # read once to examine whether the cap is working
            assert r, "[INFO] Camera not init"  # 读取失败则报错
            r, frame = cap.read()
            init_flag = True
        except Exception as e:
            print("[ERROR] {0}".format(e))
        return init_flag, cap
```
+ **打开相机并返回对象**
1. `cap`： 初始化为None，存储相机对象
2. `init_flag`: 初始化为False，表示相机是否成功打开
3. + *try*:
    1. 使用`HT_Camera`类创建一个相机对象cap，传递`camera_type`(相机类型)、`date`(日期时间)和`self.strict_mode`(严格模式)作为参数
    2. 调用`cap.read()`方法读取一帧图像，检查相机是否正常工作。
    3. 如果读取成功（r为True），则继续下一步；否则，报错"[INFO] Camera not init"，表示相机未能成功初始化
    4. 再次调用`cap.read()`方法读取一帧图像（?）
    5. `init_flag`: 设置为True，表示相机初始化成功
   + *except*:
    1. 如果在执行过程中出现异常，将异常信息打印输出
4. 返回两个值：`init_flag`（相机是否成功打开），`cap`（相机对象）
---
```
    def read(self):
        if self._open:
            r, frame = self.cap.read()
            if not r:
                self.cap.release()  # release the failed camera
                self._open = False
            return r, frame
        else:
            return False, None
```
+ **读取相机图像**
1. 判断相机是否打开
    + 若打开
    1. 调用`self.cap.read()`方法读取一帧图像，并将返回值保存在变量r和frame中
        + r = False, 表示无法读取图像, 调用`self.cap.release()`方法释放相机资源,将相机打开状态标记`self._open`设置为`False`，表示相机已关闭
        + r = True, 返回两个值：r(读取结果), frame(图像帧)
    + 若未打开
    1. 直接返回False和None，表示无法读取图像
---
```
    def release(self):
        if self._open:
            self.cap.release()
            self._open = False
```
+ **释放相机** 
1. 判断相机是否打开 
   + 若打开
   1. 调用`self.cap.release()`方法释放相机资源
   2. `self._open`设置为`False`，表示相机已关闭
---
```
    def __del__(self):
        if self._open:
            self.cap.release()
            self._open = False
```
+ **析构函数**
+ 确保在Camera_Thread对象被销毁时，即使忘记手动关闭相机，也能自动释放相机资源
