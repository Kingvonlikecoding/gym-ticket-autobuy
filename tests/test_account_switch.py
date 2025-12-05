import os
import json
import pytest
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到Python路径
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 测试用的默认配置
DEFAULT_CONFIG = {
    "username": "431688",
    "password": "123456",
    "pay_pass": "654321"
}

# 测试用的用户配置
USER1_CONFIG = {
    "username": "431688",
    "password": "user1_pass",
    "pay_pass": "user1_pay"
}

USER2_CONFIG = {
    "username": "431689",
    "password": "user2_pass",
    "pay_pass": "user2_pay"
}

@pytest.fixture
def temp_config_dir():
    """创建临时配置目录"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = os.path.join(temp_dir, "config")
        os.makedirs(config_dir, exist_ok=True)
        yield config_dir

@pytest.fixture
def mock_app():
    """创建App类的模拟实例"""
    from unittest.mock import MagicMock
    from main import App
    
    # 创建一个最小化的App实例模拟
    app = MagicMock(spec=App)
    
    # 设置基本属性
    app.current_config_file = None
    app.settings = {}
    
    # 模拟get_config_file_path方法
    app.get_config_file_path = lambda username: f"config/settings_{username}.json"
    
    return app

def test_get_config_file_path():
    """测试获取配置文件路径的逻辑"""
    from main import App
    import os
    
    # 创建一个模拟对象
    mock_app = type('obj', (object,), {})
    
    # 获取get_config_file_path方法并绑定到模拟对象
    get_path = App.get_config_file_path.__get__(mock_app)
    
    # 测试不同用户名
    username = "431688"
    expected_path = os.path.join("config", f"settings_{username}.json")
    actual_path = get_path(username)
    
    assert actual_path == expected_path
    assert username in actual_path
    assert "config" in actual_path
    assert actual_path.endswith(".json")

def test_config_file_naming():
    """测试配置文件命名规则"""
    usernames = ["431688", "431689", "20230001"]
    
    for username in usernames:
        expected_filename = f"settings_{username}.json"
        assert "settings_" in expected_filename
        assert username in expected_filename
        assert expected_filename.endswith(".json")

def test_multi_account_isolation(temp_config_dir):
    """测试多账号配置文件的隔离性"""
    # 创建两个不同用户的配置文件
    user1_file = os.path.join(temp_config_dir, "settings_431688.json")
    user2_file = os.path.join(temp_config_dir, "settings_431689.json")
    
    # 保存不同的配置
    with open(user1_file, "w", encoding="utf-8") as f:
        json.dump(USER1_CONFIG, f, indent=4)
    
    with open(user2_file, "w", encoding="utf-8") as f:
        json.dump(USER2_CONFIG, f, indent=4)
    
    # 验证两个文件都存在
    assert os.path.exists(user1_file)
    assert os.path.exists(user2_file)
    
    # 验证内容不同
    with open(user1_file, "r", encoding="utf-8") as f:
        user1_config = json.load(f)
    
    with open(user2_file, "r", encoding="utf-8") as f:
        user2_config = json.load(f)
    
    assert user1_config["username"] != user2_config["username"]
    assert user1_config["password"] != user2_config["password"]

def test_config_file_operations(temp_config_dir):
    """测试配置文件的创建、保存和加载"""
    # 测试配置文件路径
    username = "431690"
    config_file = os.path.join(temp_config_dir, f"settings_{username}.json")
    
    # 1. 测试创建和保存配置文件
    new_config = {
        "username": username,
        "password": "test_pass",
        "pay_pass": "test_pay"
    }
    
    # 保存配置
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(new_config, f, indent=4)
    
    # 验证文件已创建
    assert os.path.exists(config_file)
    
    # 2. 测试加载配置文件
    with open(config_file, "r", encoding="utf-8") as f:
        loaded_config = json.load(f)
    
    # 验证配置内容
    assert loaded_config["username"] == username
    assert loaded_config["password"] == "test_pass"
    assert loaded_config["pay_pass"] == "test_pay"

def test_config_file_path_generation():
    """测试动态配置文件路径的生成"""
    from main import App
    import os
    
    # 测试不同用户名
    test_cases = [
        "431688",
        "431689",
        "testuser"
    ]
    
    for username in test_cases:
        # 使用模拟对象测试
        mock_app = type('obj', (object,), {})
        get_path = App.get_config_file_path.__get__(mock_app)
        
        actual_path = get_path(username)
        expected_path = os.path.join("config", f"settings_{username}.json")
        
        assert actual_path == expected_path
        assert username in actual_path
        assert "config" in actual_path
        assert actual_path.endswith(".json")
