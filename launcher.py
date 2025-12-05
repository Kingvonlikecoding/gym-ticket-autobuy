import subprocess
import os
import sys
import json
import argparse
from utils.logger import setup_logger

logger = setup_logger(__name__)

def check_configuration(config_path):
    # 检查并创建必要的目录
    config_dir = os.path.dirname(config_path)
    if config_dir:
        os.makedirs(config_dir, exist_ok=True)
    os.makedirs('report', exist_ok=True)
    logger.info(f"Created necessary directories for config: {config_path}")

    # 创建默认配置文件
    if not os.path.exists(config_path):
        logger.info(f"Creating default config file: {config_path}")
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
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_settings, f, indent=4)
        logger.info(f"Default config file created: {config_path}")

def check_dependencies(config_path):
    """检查并安装依赖项"""
    with open(config_path, 'r') as f:
        settings = json.load(f)
    count=int(settings['count'])
    if count<4:
        count=0
        try:
            subprocess.run(['pip', 'install', 'uv'], check=True)
            count+=1
            logger.info("uv  installed successfully")
        except Exception as e:
            logger.error("uv  installation failed: {e}")
            sys.exit(1)

        try:
            subprocess.run(['uv', 'venv'], check=True)
            count+=1
            logger.info("uv venv installed successfully")
        except Exception as e:
            logger.error("venv installation failed: {e}")
            sys.exit(1)
        
        try:
            subprocess.run(['uv', 'sync'], check=True)
            count+=1
            logger.info("uv sync completed successfully")
        except Exception as e:
            logger.error("uv sync failed: {e}")
            sys.exit(1)

        try:
            subprocess.run(['uv', 'run', 'playwright', 'install', 'chromium', '--with-deps'], check=True)
            count+=1
            logger.info("playwright install completed successfully")
            settings['count']=count
            with open(config_path, 'w') as f:
                json.dump(settings, f, indent=4)

        except Exception as e:
            logger.error("playwright installation failed: {e}")
            sys.exit(1)    

    logger.info("All dependencies installed successfully.")

def main():
    # Parse command-line arguments for configuration file path
    parser = argparse.ArgumentParser(description="Launch the application with a specified configuration file.")
    parser.add_argument('--config', type=str, default='config/settings.json', help="Path to the configuration file (default: config/settings.json)")
    args = parser.parse_args()
    config_path = args.config

    from pathlib import Path
    cur_path = Path(__file__).parent
    os.chdir(cur_path)

    check_configuration(config_path)
    check_dependencies(config_path)

    # 运行主程序
    try:
        from main import launch_app
        launch_app(config_path=config_path)
    except ImportError as e:
        logger.error(f"Error importing launch_app: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error running launch_app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()