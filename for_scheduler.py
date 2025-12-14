import subprocess
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
subprocess.run(["uv", "run", "python", "./scripts/main_script.py", "--config=config/settings.json", "--headed"])