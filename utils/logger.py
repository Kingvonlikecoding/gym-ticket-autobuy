import logging
import os
import time

# 获取根logger
root_logger = logging.getLogger()

# 全局变量，标记根logger是否已经配置
_is_root_configured = False

# 全局变量，保存当前日志文件名
_current_log_file = None

def setup_logger(name):
    """设置日志记录器，确保所有模块共享同一个日志文件"""
    # 获取指定名称的logger，它会自动成为根logger的子logger
    logger = logging.getLogger(name)
    
    # 设置logger的级别（子logger会继承根logger的级别，但这里可以单独设置）
    logger.setLevel(logging.INFO)
    
    # 如果根logger已经配置过，直接返回
    global _is_root_configured
    if _is_root_configured:
        return logger
    
    # 根logger还没有配置，进行配置
    # 设置根logger的级别
    root_logger.setLevel(logging.INFO)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 创建文件处理器
    os.makedirs('logs', exist_ok=True)
    global _current_log_file
    if _current_log_file is None:
        _current_log_file = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime()) + '.log'
    file_name = _current_log_file
    file_handler = logging.FileHandler(f'logs/{file_name}', encoding='utf-8')
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
    
    # 标记根logger已经配置
    _is_root_configured = True
    
    return logger
