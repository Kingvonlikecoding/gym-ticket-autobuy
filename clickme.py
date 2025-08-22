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
    logger.info("Created necessary directories.")

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
        try:
            subprocess.run(['pipx', 'install', 'uv'], check=True)
            count+=1
            logger.info("uv  installed successfully")
        except Exception as e:
            logger.info("uv  installation failed: {e}")

        try:
            subprocess.run(['uv', 'venv'], check=True)
            count+=1
            logger.info("uv venv installed successfully")
        except Exception as e:
            logger.info("venv installation failed: {e}")
        
        try:
            subprocess.run(['uv', 'sync'], check=True)
            count+=1
            logger.info("uv sync completed successfully")
        except Exception as e:
            logger.info("uv sync failed: {e}")

        try:
            subprocess.run(['uv', 'run', 'playwright', 'install', 'chromium', '--with-deps'], check=True)
            count+=1
            logger.info("playwright install completed successfully")
            settings['count']=count
            with open('config/settings.json', 'w') as f:
                json.dump(settings, f, indent=4)

        except Exception as e:
            logger.info("playwright installation failed: {e}")
            sys.exit()    

    logger.info("All dependencies installed successfully.")

def main():
    from pathlib import Path
    cur_path = Path(__file__).parent
    os.chdir(cur_path)

    check_configuration()
    check_dependencies()

    # 运行主程序
    try:
        process = subprocess.Popen(
            ['uv', 'run', 'python', 'main.py'],
            start_new_session=True
        )

    except Exception as e:
        logger.error(f"Error running main.py: {e}")
        sys.exit()

if __name__ == "__main__":
    main()