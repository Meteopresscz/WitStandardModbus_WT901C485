# coding:UTF-8
"""
    测试文件
    Test file
"""
import time
import datetime
import platform
import threading
import lib.device_model as deviceModel
from lib.data_processor.roles.jy901s_dataProcessor import JY901SDataProcessor
from lib.protocol_resolver.roles.protocol_485_resolver import Protocol485Resolver

welcome = """
欢迎使用维特智能示例程序    Welcome to the Wit-Motoin sample program
"""
_writeF = None                    #写文件  Write file
_IsWriteF = False                 #写文件标识    Write file identification
def readConfig(device):
    """
    读取配置信息示例    Example of reading configuration information
    :param device: 设备模型 Device model
    :return:
    """
    tVals = device.readReg(0x02,3)  #读取数据内容、回传速率、通讯速率   Read data content, return rate, communication rate
    if (len(tVals)>0):
        print("Reg3返回结果：" + str(tVals))
    else:
        print("无返回")
    tVals = device.readReg(0x23,2)  #读取安装方向、算法  Read the installation direction and algorithm
    if (len(tVals)>0):
        print("Reg2返回结果：" + str(tVals))
    else:
        print("无返回")

def setConfig(device):
    """
    设置配置信息示例    Example setting configuration information
    :param device: 设备模型 Device model
    :return:
    """
    device.unlock()                # 解锁 unlock
    time.sleep(0.1)                # 休眠100毫秒    Sleep 100ms
    device.writeReg(0x03, 6)       # 设置回传速率为10HZ    Set the transmission back rate to 10HZ
    time.sleep(0.1)                # 休眠100毫秒    Sleep 100ms
    device.writeReg(0x23, 0)       # 设置安装方向:水平、垂直   Set the installation direction: horizontal and vertical
    time.sleep(0.1)                # 休眠100毫秒    Sleep 100ms
    device.writeReg(0x24, 0)       # 设置安装方向:九轴、六轴   Set the installation direction: nine axis, six axis
    time.sleep(0.1)                # 休眠100毫秒    Sleep 100ms
    device.save()                  # 保存 Save

def AccelerationCalibration(device):
    """
    加计校准    Acceleration calibration
    :param device: 设备模型 Device model
    :return:
    """
    device.AccelerationCalibration()                 # Acceleration calibration
    print("加计校准结束")

def FiledCalibration(device):
    """
    磁场校准    Magnetic field calibration
    :param device: 设备模型 Device model
    :return:
    """
    device.BeginFiledCalibration()                   # 开始磁场校准   Starting field calibration
    if input("请分别绕XYZ轴慢速转动一圈，三轴转圈完成后，结束校准（Y/N)？").lower()=="y":
        device.EndFiledCalibration()                 # 结束磁场校准   End field calibration
        print("结束磁场校准")

def startRecord():
    """
    开始记录数据  Start recording data
    :return:
    """
    global _writeF
    global _IsWriteF
    _writeF = open(str(datetime.datetime.now().strftime('%Y%m%d%H%M%S')) + ".txt", "w")    #新建一个文件
    _IsWriteF = True                                                                        #标记写入标识
    Tempstr = "Chiptime"
    Tempstr +=  "\tax(g)\tay(g)\taz(g)"
    Tempstr += "\twx(deg/s)\twy(deg/s)\twz(deg/s)"
    Tempstr += "\tAngleX(deg)\tAngleY(deg)\tAngleZ(deg)"
    Tempstr += "\tT(°)"
    Tempstr += "\tmagx\tmagy\tmagz"
    Tempstr += "\r\n"
    _writeF.write(Tempstr)
    print("开始记录数据")

def endRecord():
    """
    结束记录数据  End record data
    :return:
    """
    global _writeF
    global _IsWriteF
    _IsWriteF = False             # 标记不可写入标识    Tag cannot write the identity
    _writeF.close()               #关闭文件     Close file
    print("结束记录数据")

def onUpdate(deviceModel):
    """
    数据更新事件  Data update event
    :param deviceModel: 设备模型    Device model
    :return:
    """
    print("Chiptime:" + str(deviceModel.getDeviceData("Chiptime"))
         , " temperature:" + str(deviceModel.getDeviceData("temperature"))
         , " accel：" + str(deviceModel.getDeviceData("accX")) +","+  str(deviceModel.getDeviceData("accY")) +","+ str(deviceModel.getDeviceData("accZ"))
         ,  " gyro:" + str(deviceModel.getDeviceData("gyroX")) +","+ str(deviceModel.getDeviceData("gyroY")) +","+ str(deviceModel.getDeviceData("gyroZ"))
         , " angle:" + str(deviceModel.getDeviceData("angleX")) +","+ str(deviceModel.getDeviceData("angleY")) +","+ str(deviceModel.getDeviceData("angleZ"))
        , " magnetometer:" + str(deviceModel.getDeviceData("magX")) +","+ str(deviceModel.getDeviceData("magY"))+","+ str(deviceModel.getDeviceData("magZ"))
          )
    if (_IsWriteF):    #记录数据    Record data
        Tempstr = " " + str(deviceModel.getDeviceData("Chiptime"))
        Tempstr += "\t"+str(deviceModel.getDeviceData("accX")) + "\t"+str(deviceModel.getDeviceData("accY"))+"\t"+ str(deviceModel.getDeviceData("accZ"))
        Tempstr += "\t" + str(deviceModel.getDeviceData("gyroX")) +"\t"+ str(deviceModel.getDeviceData("gyroY")) +"\t"+ str(deviceModel.getDeviceData("gyroZ"))
        Tempstr += "\t" + str(deviceModel.getDeviceData("angleX")) +"\t" + str(deviceModel.getDeviceData("angleY")) +"\t"+ str(deviceModel.getDeviceData("angleZ"))
        Tempstr += "\t" + str(deviceModel.getDeviceData("temperature"))
        Tempstr += "\t" + str(deviceModel.getDeviceData("magX")) +"\t" + str(deviceModel.getDeviceData("magY")) +"\t"+ str(deviceModel.getDeviceData("magZ"))
        Tempstr += "\r\n"
        _writeF.write(Tempstr)

def LoopReadThead(device):
    """
    循环读取数据  Cyclic read data
    :param device:
    :return:
    """
    while(True):                            #循环读取数据 Cyclic read data
        device.readReg(0x30, 41)            #读取 数据  Read data

if __name__ == '__main__':

    print(welcome)
    device = deviceModel.DeviceModel(
        "我的JY901",
        Protocol485Resolver(),
        JY901SDataProcessor(),
        "51_0"
    )
    device.ADDR = 0x50                                       #设置传感器ID   Setting the Sensor ID
    if (platform.system().lower() == 'linux'):
        device.serialConfig.portName = "/dev/ttyUSB0"        #设置串口  Set serial port
    else:
        device.serialConfig.portName = "COM82"               #设置串口  Set serial port
    device.serialConfig.baud = 9600                          #设置波特率 Set baud rate
    device.openDevice()                                      #打开串口  Open serial port
    readConfig(device)                                       #读取配置信息    Read configuration information
    device.dataProcessor.onVarChanged.append(onUpdate)       #数据更新事件    Data update event

    startRecord()                                            # 开始记录数据   Start recording data
    t = threading.Thread(target=LoopReadThead, args=(device,))  #开启一个线程读取数据 Start a thread to read data
    t.start()

    input()
    device.closeDevice()
    endRecord()                             # 结束记录数据    End record data
