import subprocess
import os
import json

def check_configuration():
    # 检查并创建必要的目录
    os.makedirs('config', exist_ok=True)
    os.makedirs('report', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    current_dir = os.path.dirname(os.path.abspath(__file__))

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
            "viewable": "yes"
        }
        with open('config/settings.json', 'w', encoding='utf-8') as f:
            json.dump(default_settings, f, indent=4)

def check_dependencies():
    """检查并安装依赖项"""
    # 安装 uv
    try:
        subprocess.run(['pip', 'install', 'uv', '-i', 'https://pypi.tuna.tsinghua.edu.cn/simple'], check=False)
    except Exception as e:
        print(f"Warning: Failed to install uv: {e}")

    try:
        subprocess.run(['uv', 'init'], check=False)
    except:
        pass

    try:
        subprocess.run(['uv', 'venv'], check=False)
    except Exception as e:
        print(f"Warning: Failed to create venv: {e}")
    
    # 同步项目依赖（使用镜像）
    try:
        subprocess.run(['uv', 'sync', '--index-url', 'https://pypi.tuna.tsinghua.edu.cn/simple'], check=False)
    except Exception as e:
        print(f"Warning: Failed to sync dependencies: {e}")
    
    try:
        subprocess.run(['pip', 'install', 'pytest-playwright'], check=False)
    except Exception as e:
        pass

    try:
        subprocess.run(['pip', 'install', 'playwright'], check=False)
    except Exception as e:
        pass

    # 安装 playwright（使用镜像下载 pip 包）
    try:
        subprocess.run(['playwright', 'install'], check=False)
    except Exception as e:
        print(f"Warning: Failed to install playwright: {e}")
        
    print("Dependencies installation completed")



def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)

    check_configuration()
    check_dependencies()

    # 运行主程序
    subprocess.run(['uv', 'run', 'python', 'main.py'], check=True)


if __name__ == "__main__":
    main()