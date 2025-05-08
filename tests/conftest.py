import pytest
import json
@pytest.fixture(scope="session")
def config():
    with open("config/settings.json", "r", encoding="utf-8") as f:
        config_data = json.load(f)
    return config_data