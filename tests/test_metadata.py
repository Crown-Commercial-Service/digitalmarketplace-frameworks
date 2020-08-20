import glob
import os
import re
import yaml


def test_copying_services_metadata():
    """Make sure that every key listed under copy_services.questions_to_copy or copy_services.questions_to_exclude
    points to a valid question file, id, or field and that the referenced historical framework exists. """
    copying_services_filenames = glob.glob('frameworks/*/metadata/copy_services.yml')
    assert len(copying_services_filenames) > 0
    for copying_services_filename in copying_services_filenames:
        framework = re.match(r'^frameworks/([^/]+)/.+$', copying_services_filename).group(1)

        with open(copying_services_filename) as copying_services_file:
            copying_services_data = yaml.safe_load(copying_services_file.read())

            old_framework_path = f'frameworks/{copying_services_data["source_framework"]}'
            assert os.path.isdir(old_framework_path), f'`{old_framework_path}` is not a valid directory'

            names_ids_fields = set()
            for filename in os.listdir(f'frameworks/{framework}/questions/services'):
                if filename.startswith('multiq'):
                    continue
                with open(f'frameworks/{framework}/questions/services/{filename}') as f:
                    contents = yaml.safe_load(f)
                    if contents.get('id'):
                        names_ids_fields.add(contents['id'])
                    if contents.get('fields'):
                        names_ids_fields.update([v for v in contents.get('fields').values()])
                    names_ids_fields.add(filename[:-4])

            if 'questions_to_exclude' in copying_services_data:
                for question in copying_services_data['questions_to_exclude']:
                    assert question in names_ids_fields
            else:
                for question in copying_services_data['questions_to_copy']:
                    assert question in names_ids_fields


def test_g11_service_questions_to_scan_for_bad_words_metadata():
    """
    Ensure every key listed under service_questions_to_scan_for_bad_words.service_questions points
    to a valid question file, id or field.
    """
    service_question_filenames = glob.glob(
        'frameworks/*/metadata/service_questions_to_scan_for_bad_words.yml'
    )
    assert len(service_question_filenames) > 0

    for service_question_filename in service_question_filenames:
        framework = re.match(r'^frameworks/([^/]+)/.+$', service_question_filename).group(1)
        # Build the list of service question fields to check against for this framework
        names_ids_fields = set()
        for filename in os.listdir(f'frameworks/{framework}/questions/services'):
            # Ignore multiquestion files
            if filename.startswith('multiq'):
                continue
            with open(f'frameworks/{framework}/questions/services/{filename}') as f:
                contents = yaml.safe_load(f)
                if contents.get('id'):
                    names_ids_fields.add(contents['id'])
                if contents.get('fields'):
                    names_ids_fields.update([v for v in contents.get('fields').values()])
                names_ids_fields.add(filename[:-4])

        # Check all the fields in the 'bad words' list exist as service questions
        with open(service_question_filename) as service_question_file:
            service_question_data = yaml.safe_load(service_question_file.read())
            for question in service_question_data['service_questions']:
                assert question in names_ids_fields
