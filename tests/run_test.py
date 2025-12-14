#!/usr/bin/env python3
import os
import sys
import subprocess
from datetime import datetime

# 将父目录添加到Python路径中
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 直接使用utils.logger，它会自动检测测试环境
from utils.logger import setup_logger, get_current_log_file

logger = setup_logger(__name__)

def run_test_in_sequence():
    """按顺序运行所有测试用例"""
    test_cases = [
        "tests/test_smoke.py"
    ]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join("tests", "test_results", f"test_report_{timestamp}.html")
    
    logger.info("开始执行所有测试用例")
    print("开始执行所有测试用例")
    
    # 获取当前日志文件名
    current_log_file = get_current_log_file()
    
    # 设置环境变量，让pytest进程使用同一个日志文件
    env = os.environ.copy()
    env['TEST_LOG_FILE'] = current_log_file
    
    # 将所有测试用例作为一个整体执行
    cmd = [sys.executable, "-m", "pytest"] + test_cases + ["-v", "--headed", f"--html={report_file}", "--self-contained-html"]
    
    try:
        # 在调用pytest时传递环境变量
        subprocess.run(cmd, cwd=project_root, env=env, shell=False)
        logger.info("所有测试用例执行完成")
    except Exception as e:
        error_msg = f"执行测试用例时发生错误: {str(e)}"
        logger.error(error_msg)
        print(error_msg)
    
    completion_msg = f"所有测试用例执行完成，报告文件生成在: {report_file}"
    logger.info(completion_msg)
    print(completion_msg)

if __name__ == "__main__":
    run_test_in_sequence()
