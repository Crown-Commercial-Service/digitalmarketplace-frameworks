import os
import yaml
import pytest


@pytest.fixture
def all_files():
    all_paths = []
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    for filename in os.path.join(root_dir, 'g6'):
        if filename.endswith('.yml'):
            filepath = os.path.join(root_dir, 'g6', filename)
            all_paths.append(filepath)
    return all_paths

def test_all_files_are_yaml(all_files):
    for path in all_files:
        with open(path) as f:
            yaml.load(f)
