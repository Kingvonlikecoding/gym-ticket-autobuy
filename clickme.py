import subprocess
import os
import sys
import json
from utils.logger import setup_logger

logger = setup_logger(__name__)

def check_configuration():
    # 检查并创建必要的目录
    os.makedirs('config', exist_ok=True)
    os.makedirs('report', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    # 创建默认配置文件
    if not os.path.exists('config/settings.json'):
        default_settings = {
            "username": "",
            "password": "",
            "pay_pass": "",
            "date": "tomorrow",
            "time_slot": "20:00-21:00",
            "venue": "C",
            "court": "out",
            "viewable": "yes",
            "wait_timeout_seconds": "2",
            "count": 0
        }
        with open('config/settings.json', 'w', encoding='utf-8') as f:
            json.dump(default_settings, f, indent=4)

def check_dependencies():
    """检查并安装依赖项"""
    with open('config/settings.json', 'r') as f:
        settings = json.load(f)
    count=int(settings['count'])
    if count<4:
        count=0
        # 安装 uv
        try:
            subprocess.run(['pip', 'install', 'uv'], check=True)
            count+=1
        except Exception as e:
            logger.info("uv  installation failed: {e}")

        try:
            subprocess.run(['uv', 'venv'], check=True)
            count+=1
        except Exception as e:
            logger.info("venv installation failed: {e}")
        
        # 同步项目依赖（使用镜像）
        try:
            subprocess.run(['uv', 'sync'], check=True)
            count+=1
        except Exception as e:
            logger.info("uv sync failed: {e}")

        # python_path = r'.venv\Scripts\python.exe'

        # 安装 playwright（使用镜像下载 pip 包）
        try:
            # 设置环境变量使用镜像
            # env = os.environ.copy()
            
            # 安装浏览器
            # subprocess.run([python_path, '-m', 'playwright', 'install', 'chromium', '--with-deps'], env=env, check=True)
            subprocess.run(['uv', 'run', 'playwright', 'install', 'chromium', '--with-deps'], check=True)
            print("Playwright installation completed")
            count+=1
            settings['count']=count
            with open('config/settings.json', 'w') as f:
                json.dump(settings, f, indent=4)

        except Exception as e:
            logger.info("playwright installation failed: {e}")
            sys.exit()    

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)

    check_configuration()
    check_dependencies()

    # 运行主程序
    subprocess.Popen(
    ['uv', 'run', 'python', 'main.py'],
    stdout=subprocess.DEVNULL,  # 将子进程的标准输出（stdout）重定向到“空设备”，即丢弃所有输出
    stderr=subprocess.DEVNULL, # 错误输出（stderr）
    stdin=subprocess.DEVNULL, # 输入（stdin）
    start_new_session=True  # 使子进程独立于父进程所在的进程组和会话（不完全独立）
    )


if __name__ == "__main__":
    main()