import schedule
import time
from units7 import ScreenAutomation
import os
import shutil
from logger_handler import logger

# 定义一个函数来封装主逻辑，以便我们可以捕获异常并重新运行
def run_main():
    attempts = 1
    max_attempts = 2  # 最多重试两次
    while attempts <= max_attempts:
        try:
            start_app()
            logger.info(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}启动app')
            time.sleep(10)
            ScreenAutomation().run_main()
            logger.info(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}app主代码执行完毕')
            stop_app()
            logger.info(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}app关闭')
            clean_screenshots()
            logger.info('删除截图')
            break  # 如果没有错误，跳出循环
        except Exception as e:
            logger.error(f"运行过程中出现错误：{e}")
            clean_screenshots()
            attempts += 1
            if attempts > max_attempts:
                logger.error("达到最大重试次数，停止运行")

# 定义一个函数来封装华为app的主逻辑
def run_main_huawei():
    attempts = 0
    max_attempts = 2  # 最多重试两次
    while attempts <= max_attempts:
        try:
            start_app_huawei()
            logger.info(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}启动华为app')
            time.sleep(10)
            ScreenAutomation().run_main()
            logger.info(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}华为app主代码执行完毕')
            stop_app_huawei()
            logger.info(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}华为app关闭')
            clean_screenshots()
            logger.info('删除截图')
            break  # 如果没有错误，跳出循环
        except Exception as e:
            logger.info(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}华为app运行过程中出现错误：{e}')
            clean_screenshots()
            attempts += 1
            if attempts > max_attempts:
                logger.error(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}达到最大重试次数，停止运行')

# 启动华为app
def start_app_huawei():
    cmd = 'adb shell am start -n com.netease.yhtj.huawei/com.netease.game.MessiahNativeActivity'
    ScreenAutomation()._run_cmd(cmd)
    time.sleep(3)

# 关闭华为app
def stop_app_huawei():
    cmd = 'adb shell am force-stop com.netease.yhtj.huawei'
    ScreenAutomation()._run_cmd(cmd)
    time.sleep(3)

# 启动app
def start_app():
    cmd = 'adb shell am start -n com.netease.yhtj/com.netease.game.MessiahNativeActivity'
    ScreenAutomation()._run_cmd(cmd)
    time.sleep(3)

# 关闭app
def stop_app():
    cmd = 'adb shell am force-stop com.netease.yhtj'
    ScreenAutomation()._run_cmd(cmd)
    time.sleep(3)

# 删除截图
def clean_screenshots(folder_path="D:\\CODE\\YHTJ\\out_files\\screenshots"):
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
            except Exception as e:
                logger.error(f'无法删除 {file_path}。原因: {e}')
    else:
        logger.error(f'提供的路径 {folder_path} 不存在或不是一个文件夹。')

# 主函数，用于调度任务
def main():
    run_main()
    time.sleep(5)
    run_main_huawei()

# 安排任务
for hour in range(20):  # 0到20点
    schedule.every().day.at(f"{hour:02d}:58").do(main)

while True:
    schedule.run_pending()
    time.sleep(1)