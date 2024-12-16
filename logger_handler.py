import logging
from logging.handlers import RotatingFileHandler
import os
import datetime
import sys
from pathlib import Path

project_path = Path(__file__).parent
log_path = project_path /'out_files' / 'logs'

# 自定义日志过滤器类
class LogFilter(logging.Filter):
    """自定义日志过滤器"""

    def filter(self, record):
        # 过滤掉info级别的日志
        # if record.levelno == logging.INFO:
        #     return False
        return True

class Logger:
    """
    Logger类用于封装日志功能，提供信息、调试、警告、错误和严重错误等不同级别的日志记录方法。
    """
    def __init__(self, name="自救针购买日志", level=logging.INFO, log_dir= log_path):
        """
        初始化Logger类实例。

        Parameters:
            name: 日志记录器的名称，默认为"AppAutomation"。
            level: 日志级别，默认为logging.INFO。
            log_dir: 日志文件存放路径
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)  # 设置日志级别
        self.logger.addFilter(LogFilter())  # 添加自定义日志过滤器

        # 确保日志目录存在
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 创建包含日期的日志文件名
        log_filename = f"{log_dir}/{datetime.datetime.now().strftime('%Y-%m-%d')}.log"

        # 创建文件日志处理器，设置最大文件大小和备份文件数量，并指定编码为utf-8
        self.file_handler = RotatingFileHandler(log_filename, maxBytes=10485760, backupCount=5, encoding='utf-8')
        self.file_handler.setLevel(level)  # 设置文件处理器的日志级别

        # 创建控制台日志处理器
        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setLevel(level)  # 设置控制台处理器的日志级别

        # 设置日志格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(threadName)s - %(message)s')
        self.file_handler.setFormatter(formatter)  # 为文件处理器设置格式
        self.console_handler.setFormatter(formatter)  # 为控制台处理器设置格式

        # 将处理器添加到日志记录器
        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.console_handler)

    def get_logger(self):
        return self.logger

    def critical(self, msg):
        self.logger.critical(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def error(self, msg):
        self.logger.error(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

# 配置日志
logger = Logger().get_logger()

if __name__ == '__main__':
    logger.info("Hello, world!")
    logger.warning("This is a warning message.")
    logger.error("An error has occurred.")
    logger.debug("This is a debug message.")
    logger.critical("A critical error has occurred.")