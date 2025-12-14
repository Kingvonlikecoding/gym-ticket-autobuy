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
    
    # 创建测试相关目录
    os.makedirs('tests/test_results', exist_ok=True)
    os.makedirs('tests/test_logs', exist_ok=True)
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
            "count": 0,
            "user": "user"
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_settings, f, indent=4)
        logger.info(f"Default config file created: {config_path}")

def check_dependencies_4dev(config_path):
    """检查并安装依赖项"""
    with open(config_path, 'r') as f:
        settings = json.load(f)
    
    # 首先判断count是否为4，如果是则跳过所有依赖项检查和安装
    count = int(settings.get('count', 0))
    if count == 4:
        logger.info("All dependencies already installed (count=4), skipping all checks.")
        return
    
    # 检查并安装 uv
    try:
        # 尝试运行 uv --version 来检查是否已安装
        subprocess.run(['uv', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info("uv is already installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        # 如果未安装，则安装
        try:
            subprocess.run(['pip', 'install', 'uv'], check=True)
            logger.info("uv installed successfully")
        except Exception as e:
            logger.error(f"uv installation failed: {e}")
            sys.exit(1)

    # 检查并创建虚拟环境
    venv_just_created = False
    if not os.path.exists('venv'):
        try:
            subprocess.run(['uv', 'venv'], check=True)
            logger.info("uv venv created successfully")
            venv_just_created = True
        except Exception as e:
            logger.error(f"venv creation failed: {e}")
            sys.exit(1)
    else:
        logger.info("Virtual environment already exists")
    
    # 同步依赖项（仅在首次安装或虚拟环境刚创建时执行）
    try:
        # 只有在首次安装或虚拟环境刚创建时才执行uv sync
        if count < 3 or venv_just_created:
            subprocess.run(['uv', 'sync'], check=True)
            logger.info("uv sync completed successfully")
        else:
            logger.info("Dependencies already synced, skipping uv sync")
    except Exception as e:
        logger.error(f"uv sync failed: {e}")
        sys.exit(1)

    # 检查并安装 playwright chromium
    try:
        # 尝试运行 playwright --version 来检查是否已安装
        subprocess.run(['uv', 'run', 'playwright', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info("playwright is already installed")
        # 检查 chromium 是否已安装
        result = subprocess.run(['uv', 'run', 'playwright', 'install', 'chromium', '--dry-run'], 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if "already installed" in result.stdout or "already installed" in result.stderr:
            logger.info("chromium is already installed")
        else:
            # 如果 chromium 未安装，则安装
            subprocess.run(['uv', 'run', 'playwright', 'install', 'chromium', '--with-deps'], check=True)
            logger.info("chromium installed successfully")
    except (subprocess.CalledProcessError, FileNotFoundError):
        # 如果 playwright 未安装，则安装
        try:
            subprocess.run(['uv', 'run', 'playwright', 'install', 'chromium', '--with-deps'], check=True)
            logger.info("playwright and chromium installed successfully")
        except Exception as e:
            logger.error(f"playwright installation failed: {e}")
            sys.exit(1)
    
    # 更新配置文件中的count为4，表示所有依赖项都已安装
    settings['count'] = 4
    with open(config_path, 'w') as f:
        json.dump(settings, f, indent=4)
    
    logger.info("All dependencies installed successfully.")

def check_dependencies_4user(config_path):
    """用户模式下的依赖检查，使用pip管理依赖，并使用镜像站加速安装"""
    with open(config_path, 'r') as f:
        settings = json.load(f)
    
    # 首先判断count是否为4，如果是则跳过所有依赖项检查和安装
    count = int(settings.get('count', 0))
    if count == 4:
        logger.info("All dependencies already installed (count=4), skipping all checks.")
        return
    
    # 定义依赖项和镜像站URL
    dependencies = [
        "playwright>=1.52.0"
    ]
    # 使用清华大学PyPI镜像站加速安装
    mirror_url = "https://pypi.tuna.tsinghua.edu.cn/simple"
    mirror_option = ["-i", mirror_url, "--trusted-host", "pypi.tuna.tsinghua.edu.cn"]
    
    # 检查并安装依赖项
    for dependency in dependencies:
        try:
            # 提取包名（去除版本要求）
            package_name = dependency.split('>=')[0]
            
            # 检查包是否已安装且版本满足要求
            result = subprocess.run(
                [sys.executable, "-c", f"import {package_name}; print({package_name}.__version__)"]
            )
            
            if result.returncode != 0:
                # 包未安装，使用镜像站安装
                logger.info(f"Installing {dependency} using mirror...")
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", *mirror_option, dependency],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                logger.info(f"Successfully installed {dependency} using mirror")
            else:
                logger.info(f"{package_name} is already installed, skipping")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install {dependency} using mirror: {e.stdout}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error when installing {dependency}: {e}")
            sys.exit(1)
    
    logger.info("All dependencies installed successfully using pip and mirror")

    # 检查并安装 playwright chromium
    try:
        # 使用镜像站安装 playwright 浏览器
        logger.info("Installing/Checking playwright browsers...")
        
        # 安装 chromium 浏览器，使用镜像站加速
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium", "--with-deps", "--download-timeout=60000"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env={**os.environ, "PLAYWRIGHT_DOWNLOAD_HOST": "https://npm.taobao.org/mirrors/playwright"}
        )
        logger.info("Playwright chromium installed successfully using mirror")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install playwright chromium: {e.stdout}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error when installing playwright: {e}")
        sys.exit(1)
    
    # 更新配置文件中的count为4，表示所有依赖项都已安装
    settings['count'] = 4
    with open(config_path, 'w') as f:
        json.dump(settings, f, indent=4)
    
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
    
    # 读取配置文件，根据user字段决定执行哪个依赖检查函数
    with open(config_path, 'r') as f:
        settings = json.load(f)
    
    user_type = settings.get('user', 'user')
    if user_type == 'dev':
        check_dependencies_4dev(config_path)
    else:
        check_dependencies_4user(config_path)

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