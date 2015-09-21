import os
import yaml
import json
import pytest
from jsonschema.validators import validator_for
from jsonschema import ValidationError


def test_all_files_are_yaml(get_all_files):
    for path in get_all_files:
        with open(path) as f:
            yaml.load(f)


def test_questions_match_schema(get_all_files):
    question_schema = load_jsonschema('tests/schemas/question.json')
    for path in get_all_files:
        with open(path) as f:
            data = yaml.load(f)
            try:
                validator_for(question_schema)(question_schema).validate(data)
            except ValidationError as e:
                pytest.fail("{} failed validation with: {}".format(path, e))


@pytest.fixture
def get_all_files():

    def all_files():
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frameworks'))
        for root, subdirs, files in os.walk(root_dir):
            for filename in files:
                if filename.endswith('.yml'):
                    yield os.path.join(root, filename)

    return all_files()


def load_jsonschema(path):
    with open(path) as f:
        schema = json.load(f)
        validator = validator_for(schema)
        validator.check_schema(schema)
        return schema
