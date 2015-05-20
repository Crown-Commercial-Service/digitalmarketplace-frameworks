import os
import yaml
import json
import pytest
from jsonschema.validators import validator_for
from jsonschema import ValidationError


def test_all_files_are_yaml(all_files):
    for path in all_files:
        with open(path) as f:
            yaml.load(f)


def test_questions_match_schema(all_files):
    question_schema = load_jsonschema('tests/schemas/question.json')
    for path in all_files:
        with open(path) as f:
            data = yaml.load(f)
            try:
                validator_for(question_schema)(question_schema).validate(data)
            except ValidationError as e:
                pytest.fail("{} failed validation with: {}".format(path, e))


@pytest.fixture
def all_files():
    all_paths = []
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    root_dir = os.path.join(root_dir, 'g6')
    for filename in os.listdir(root_dir):
        if filename.endswith('.yml') and filename != 'index.yml':
            filepath = os.path.join(root_dir, filename)
            all_paths.append(filepath)
    return all_paths


def load_jsonschema(path):
    with open(path) as f:
        schema = json.load(f)
        validator = validator_for(schema)
        validator.check_schema(schema)
        return schema
