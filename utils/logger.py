import logging
import os

def setup_logger(name):
    """
    创建一个日志记录器
    
    Args:
        name: 记录器名称，通常使用 __name__（当前模块的名称）
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    
    # 如果logger已经有处理器，说明已经被配置过，直接返回
    # logger.handlers 是一个列表，保存了当前 logger 对象已经添加的所有日志处理器（Handler）。
    if logger.handlers:
        return logger
    
    # setLevel() 方法用于指定该记录器处理的最低日志级别。
    # logging.INFO 表示只记录 INFO 级别及以上（如 WARNING, ERROR, CRITICAL）的日志消息，
    # 低于 INFO 的级别（如 DEBUG）会被忽略
    logger.setLevel(logging.INFO)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 创建文件处理器
    os.makedirs('logs', exist_ok=True)
    file_handler = logging.FileHandler('logs/app.log', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 设置格式化器
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
