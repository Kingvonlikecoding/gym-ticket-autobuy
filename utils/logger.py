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
    
    # 检测是否在运行测试用例
    is_testing = False
    import sys
    if 'pytest' in sys.modules or 'test' in sys.argv[0]:
        is_testing = True
    
    # 从环境变量中获取日志文件名，如果有的话
    log_file_from_env = os.environ.get('TEST_LOG_FILE')
    
    # 创建文件处理器
    if is_testing:
        # 测试环境：将日志保存到 tests/test_logs 文件夹
        log_dir = 'tests/test_logs'
    else:
        # 非测试环境：将日志保存到 logs 文件夹
        log_dir = 'logs'
    
    os.makedirs(log_dir, exist_ok=True)
    
    global _current_log_file
    if _current_log_file is None:
        # 优先使用环境变量中的日志文件名
        if is_testing and log_file_from_env:
            _current_log_file = log_file_from_env
        elif is_testing:
            # 测试环境：使用分钟级的时间戳
            _current_log_file = time.strftime('%Y-%m-%d-%H-%M', time.localtime()) + '.log'
        else:
            # 非测试环境：使用秒级的时间戳
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
