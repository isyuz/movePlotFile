import ctypes
import os
import platform
import shutil
import time

import threading

def get_free_space_mb(folder):
    """
    获取磁盘剩余空间
    :param folder: 磁盘路径 例如 D:\\
    :return: 剩余空间 单位 G
    """
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value / 1024 / 1024 // 1024
    else:
        st = os.statvfs(folder)
        return st.f_bavail * st.f_frsize / 1024 / 1024 // 1024

# plot文件才处理
# 删除文件小于101G的损坏文件
# 目标盘剩余空间大于102则继续
def move_file(source, dst):
    print("源盘%s剩余空间：%s G,目标盘%s剩余空间: %s G" %(source,get_free_space_mb(source),dst, get_free_space_mb(dst)))
    list = os.listdir(source)  # 列出文件夹下所有的目录与文件
    if len(list) != 0:
        for i in range(0, len(list)):
            path = os.path.join(source, list[i])
            # 是plot文件才处理
            if os.path.isfile(path) and list[i].endswith('.plot'):    
                dst_path = os.path.join(dst, list[i])
                file_size = os.path.getsize(path)/float(1024*1024*1024)
                if file_size < 101:
                    os.remove(path)
                    print('已删除损坏的文件：',path,'文件大小：',file_size)
                else:
                    # 因plot文件一般是101.8G，所以设置目标盘剩余空间大于102，移动的文件大于101才处理
                    if get_free_space_mb(dst) > 102 and file_size > 101:
                        # 目标文件已存在，且小于101G，则删除；避免文件已复制且源文件为0的误删的情况
                        if os.path.exists(dst_path) and os.path.getsize(dst_path)/float(1024*1024*1024) < 101:
                            os.remove(dst_path)
                        print("%s 开始转移:%s 到 %s" %(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),path,dst))
                        shutil.move(path, dst)
                        print("%s 成功转移第 %s 个文件：%s " %(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),i + 1,path))
                    # else: print("%s 跳过……文件大小：%s;目标盘剩余：%s;文件路径：%s" %(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),file_size,get_free_space_mb(dst),path)
    else: print("没有plot文件")

if __name__ == '__main__':
    print('Version:','1.0.0')
    # sourcList = ['D:\ss\mnt\dst\d1']
    # dstList = ['D:\ss\mnt\dst\d4']
    sourcInput = input("请输入源盘编号(00-03)：")
    if( sourcInput == ""):
        sourcList = ['/mnt/dst/00', '/mnt/dst/01', '/mnt/dst/02', '/mnt/dst/03']
        dstList = ['/mnt/dst/04', '/mnt/dst/05', '/mnt/dst/06']
    else:
        sourcDisk = '/mnt/dst/' + sourcInput
        sourcList = [sourcDisk]
        dstInput = input("请输入目标盘编号(04-06)：")
        dstDisk = '/mnt/dst/' + dstInput
        dstList = [dstDisk]
    for i in range(0, len(sourcList)):
        t = threading.Thread(target=move_file, args=(sourcList[i], dstList[i]))
        t.start()
        print("Two things is end....")
