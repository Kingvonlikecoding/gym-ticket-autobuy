import subprocess
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
subprocess.run(["uv", "run", "python", "-m", "pytest","./tests/test_main.py", "--headed"])