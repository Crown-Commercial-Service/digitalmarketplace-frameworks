#!/usr/bin/env python

import yaml
import os

dir = os.getcwd()
if os.path.isfile('{}/output.yml'.format(dir)):
    os.remove('{}/output.yml'.format(dir))

def create_data_packet(file_path, doc):
    return dict(
        path=file_path.split('..')[-1],
        name=doc.get('name', '**DOES NOT EXIST**'),
        question=doc.get('question', '**DOES NOT EXIST**'),
        hint=doc.get('hint', '**DOES NOT EXIST**'),
        validations=doc.get('validations', '**DOES NOT EXIST**')
    )

def write_back_to_file(ouput_file, data):
    ouput_file.write( yaml.dump(data, default_flow_style=False, allow_unicode=True) )
    ouput_file.write('\n')

def directory_is_questions_(dirName):
    return dirName.split('/')[-1] == 'questions'

def get_file_list(directory):
    output = []
    for dirName, subdirList, fileList in os.walk(directory):
        with_paths = map(lambda file_name: '{}/{}'.format(dirName, file_name), fileList)
        output.append(with_paths)
    return [val for sublist in output for val in sublist]

def read_and_write_files(file_paths):
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            doc = yaml.load(f)
            if doc.get('validations'):
                data = create_data_packet(file_path, doc)
                with open ('output.yml', 'a') as output_file:
                    write_back_to_file(output_file, data)


if __name__ == '__main__':
    for dirName, subdirList, fileList in os.walk('{}/../frameworks'.format(dir)):
        if directory_is_questions_(dirName):
            file_paths = get_file_list(dirName)
            read_and_write_files(file_paths)
