import glob
import os
import re
import yaml


def test_copying_services_metadata():
    """Make sure that every file/question listed under copying-services.questions_whitelist points to a valid
    question file, and that the referenced historical framework exists."""
    copying_services_filenames = glob.glob('frameworks/*/metadata/copying-services.yml')
    for copying_services_filename in copying_services_filenames:
        framework = re.match(r'^frameworks/([^/]+)/.+$', copying_services_filename).group(1)

        with open(copying_services_filename) as copying_services_file:
            copying_services_data = yaml.safe_load(copying_services_file.read())

            old_framework_path = f'frameworks/{copying_services_data["framework"]}'
            assert os.path.isdir(old_framework_path), f'`{old_framework_path}` is not a valid directory'

            for question in copying_services_data['questions_whitelist']:
                question_filename = f'frameworks/{framework}/questions/services/{question}.yml'
                assert os.path.isfile(question_filename), f'`{question_filename}` is not a file'
