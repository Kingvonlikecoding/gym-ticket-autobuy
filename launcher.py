import subprocess
import os
import sys
import json
import argparse
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger(__name__)

PROJECT_ROOT = Path(__file__).parent
VENV_DIR = PROJECT_ROOT / ".venv"


def run_cmd(cmd, *, capture_output=False):
    """Run a command and raise with readable logs when it fails."""
    kwargs = {"check": True}
    if capture_output:
        kwargs.update({"stdout": subprocess.PIPE, "stderr": subprocess.PIPE, "text": True})
    return subprocess.run(cmd, **kwargs)


def get_venv_python_path():
    """Return virtualenv python executable path for current platform."""
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def check_configuration(config_path):
    # 检查并创建必要的目录
    config_dir = os.path.dirname(config_path)
    if config_dir:
        os.makedirs(config_dir, exist_ok=True)
    os.makedirs("report", exist_ok=True)

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
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(default_settings, f, indent=4)
        logger.info(f"Default config file created: {config_path}")

def check_dependencies(config_path):
    """检查并安装依赖项"""
    with open(config_path, "r", encoding="utf-8") as f:
        settings = json.load(f)
    
    venv_python = get_venv_python_path()

    # count=4 只有在虚拟环境可用时才跳过检查
    count = int(settings.get('count', 0))
    if count == 4 and venv_python.exists():
        logger.info("All dependencies already installed (count=4), skipping all checks.")
        return
    
    # 检查并安装 uv
    try:
        run_cmd(["uv", "--version"], capture_output=True)
        logger.info("uv is already installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            # 使用当前 Python 安装 uv，避免系统找不到 pip 命令
            run_cmd([sys.executable, "-m", "pip", "install", "uv"])
            logger.info("uv installed successfully")
        except Exception as e:
            logger.error(f"uv installation failed: {e}")
            sys.exit(1)

    # 检查并创建虚拟环境（uv 默认目录是 .venv）
    venv_just_created = False
    if not VENV_DIR.exists():
        try:
            run_cmd(["uv", "venv"])
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
            run_cmd(["uv", "sync"])
            logger.info("uv sync completed successfully")
        else:
            logger.info("Dependencies already synced, skipping uv sync")
    except Exception as e:
        logger.error(f"uv sync failed: {e}")
        sys.exit(1)

    # 检查 playwright CLI 是否可用（不强制下载浏览器）
    try:
        # 使用 python -m playwright，避免依赖可执行入口脚本
        run_cmd(["uv", "run", "python", "-m", "playwright", "--version"], capture_output=True)
        logger.info("playwright is already installed")
        logger.info("Skipping bundled browser installation; will use system browser channels first")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("playwright CLI is unavailable after dependency sync")
        sys.exit(1)
    
    # 更新配置文件中的count为4，表示所有依赖项都已安装
    settings['count'] = 4
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)
    
    logger.info("All dependencies installed successfully.")

def main():
    # Parse command-line arguments for configuration file path
    parser = argparse.ArgumentParser(description="Launch the application with a specified configuration file.")
    parser.add_argument('--config', type=str, default='config/settings.json', help="Path to the configuration file (default: config/settings.json)")
    args = parser.parse_args()
    config_path = args.config

    os.chdir(PROJECT_ROOT)

    check_configuration(config_path)
    check_dependencies(config_path)

    # 运行主程序
    try:
        # 使用虚拟环境中的Python解释器运行main.py
        python_exe = get_venv_python_path()
        if not python_exe.exists():
            logger.error(f"Virtual environment Python interpreter not found at {python_exe}")
            sys.exit(1)
        
        # 运行main.py，传递配置文件路径
        run_cmd([str(python_exe), "-m", "main", f"--config={config_path}"])
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running main.py: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error running main.py: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()