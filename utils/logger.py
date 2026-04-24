import logging
import os
import time

# 全局变量，保存当前日志文件名
_current_log_file = None

def setup_logger(name):
    """设置日志记录器，确保所有模块共享同一个日志文件"""
    # 获取根logger
    root_logger = logging.getLogger()
    
    # 检查根logger是否已经有处理器被添加
    if root_logger.handlers:
        return logging.getLogger(name)
    
    # 设置根logger的级别
    root_logger.setLevel(logging.INFO)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 统一将日志保存到 logs 目录
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    global _current_log_file
    if _current_log_file is None:
        _current_log_file = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime()) + '.log'
    
    file_name = _current_log_file
    file_handler = logging.FileHandler(os.path.join(log_dir, file_name), encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s  [%(levelname)s]  %(module)s  [%(filename)s:%(lineno)d]  %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 设置格式化器
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # 只在根logger上添加处理器，所有子logger会自动继承
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    return logging.getLogger(name)

def get_current_log_file():
    """获取当前日志文件的文件名"""
    global _current_log_file
    return _current_log_file
