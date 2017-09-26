#!/usr/bin/env python
"""Extract validation messages from the frameworks questions content.

This script retrieves all the validation messages within the frameworks repo for
all the apps. There are small number of validation messages in the frontend apps
which will need extracting manually for completeness.

Specify the output path for the files as below, and a directory will be created
with a separate yaml file for each framework, containing that frameworks
validation messages.

Usage:
    extract_validation_messages.py --output-path=<output_path>

"""
import yaml
import os
import sys
from docopt import docopt


def check_and_create_output_directory(path):
    if os.path.exists('{}/validation_messages'.format(path)):
        print('{}/validation_messages already exists. Please specify a different output path.'.format(path))
        sys.exit(1)

    os.makedirs('{}/validation_messages'.format(path))


def create_data_packet(file_path, doc):
    return dict(
        path=file_path.split('..')[-1],
        name=doc.get('name', '**DOES NOT EXIST**'),
        question=doc.get('question', '**DOES NOT EXIST**'),
        hint=doc.get('hint', '**DOES NOT EXIST**'),
        validations=doc.get('validations', '**DOES NOT EXIST**')
    )


def write_back_to_file(ouput_file, data):
    ouput_file.write(yaml.dump(data, default_style='>', default_flow_style=False, allow_unicode=True))
    ouput_file.write('\n')


def directory_is_questions_(dirName):
    return dirName.split('/')[-1] == 'questions'


def get_file_list(directory):
    output = []
    for dirName, subdirList, fileList in os.walk(directory):
        with_paths = map(lambda file_name: '{}/{}'.format(dirName, file_name), fileList)
        output.append(with_paths)
    return [val for sublist in output for val in sublist]


def read_and_write_files(file_paths, output_file_name):
    with open(output_file_name, 'a') as output_file:
        for file_path in file_paths:
            with open(file_path, 'r') as f:
                doc = yaml.safe_load(f)
                if doc.get('validations'):
                    data = create_data_packet(file_path, doc)
                    write_back_to_file(output_file, data)


if __name__ == '__main__':
    current_dir = os.path.dirname(__file__)
    arguments = docopt(__doc__)
    check_and_create_output_directory(arguments['--output-path'])
    for dirName, subdirList, fileList in os.walk('{}/../frameworks'.format(current_dir)):
        if directory_is_questions_(dirName):
            output_file_name = '{}/validation_messages/{}.yml'.format(arguments['--output-path'],
                                                                      dirName.split('/')[-2])
            file_paths = get_file_list(dirName)
            read_and_write_files(file_paths, output_file_name)
