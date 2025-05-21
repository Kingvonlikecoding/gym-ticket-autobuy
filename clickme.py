import subprocess
import os
import json

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
            "flag": "new"
        }
        with open('config/settings.json', 'w', encoding='utf-8') as f:
            json.dump(default_settings, f, indent=4)

def check_dependencies():
    """检查并安装依赖项"""
    # 安装 uv
    try:
        subprocess.run(['pip', 'install', 'uv'], check=False)
    except Exception as e:
        print(f"Warning: Failed to install uv: {e}")

    # 初始化 uv
    try:
        subprocess.run(['uv', 'init'], check=False)
    except Exception as e:
        print(f"Warning: Failed to initialize uv: {e}")

    try:
        subprocess.run(['uv', 'venv'], check=False)
    except Exception as e:
        print(f"Warning: Failed to create venv: {e}")
    
    # 同步项目依赖
    try:
        subprocess.run(['uv', 'sync'], check=False)
    except Exception as e:
        print(f"Warning: Failed to sync dependencies: {e}")
    
    # 安装 playwright
    subprocess.run(['uv', 'run', 'python', '-m', 'playwright', 'install'], check=True)



def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)

    check_configuration()

    # 读取 flag
    with open('./config/settings.json', 'r', encoding='utf-8') as f:
        settings = json.load(f)

    flag = settings.get("flag")

    if flag=='new':
        check_dependencies()
        settings["flag"] = "used"
        with open('./config/settings.json', 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)

    # 运行主程序
    subprocess.run(['uv', 'run', 'python', 'main.py'], check=True)


if __name__ == "__main__":
    main()