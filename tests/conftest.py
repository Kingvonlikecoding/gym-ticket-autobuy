import pytest
import json
import os

def pytest_addoption(parser):
    parser.addoption(
        "--config",
        action="store",
        default="config/settings.json",
        help="Path to the configuration file"
    )

@pytest.fixture(scope="session")
def config(request):
    config_path = request.config.getoption("--config")
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)
    return config_data