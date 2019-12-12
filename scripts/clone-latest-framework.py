#!/usr/bin/env python
"""Clone a new framework, based on the latest iteration, into the same level directory.

- Finds the last iteration of the given framework family type
- Copies all content to a new folder
- Update metadata
- Update hardcoded content of framework name in declaration questions 'G-Cloud 11', 'G-Cloud&nsbp;11'
- Update hardcoded content of framework slug in urls, declaration
- Set any dates to a point in the far-future e.g. 1 Jan 2525

Usage:
    clone-latest-framework.py --family=<framework_family> --iteration=<iteration_number>

"""
import os
import sys
import shutil
import yaml
from docopt import docopt


METADATA_FILES = {
    'copy_services': 'copy_services.yml',
    'following_framework': 'following_framework.yml',
    'bad_words': 'service_questions_to_scan_for_bad_words.yml'
}


def get_fw_name_from_slug(fw_slug):
    return fw_slug.replace('-', ' ').title()


def update_metadata(previous_fw, new_fw, following_fw):
    print("Setting metadata")
    # Set copy_services.yml content
    copy_services_file = os.path.join("frameworks", new_fw, 'metadata', METADATA_FILES['copy_services'])
    with open(copy_services_file) as f:
        content = yaml.safe_load(f)
        # TODO: preserve ordering
        new_content = {
            'source_framework': previous_fw,
            'questions_to_copy': content['questions_to_copy']
        }

    with open(copy_services_file, 'w') as f:
        yaml.dump(new_content, f)

    # Set following_framework.yml content
    following_fw_file = os.path.join("frameworks", new_fw, 'metadata', METADATA_FILES['following_framework'])
    with open(following_fw_file) as f:
        content = yaml.safe_load(f)
        new_content = {
            'framework': {
                'slug': following_fw,
                'name': get_fw_name_from_slug(following_fw),
                'coming': str(int(content['framework']['coming']) + 1)
            }
        }
    with open(following_fw_file, 'w') as f:
        yaml.dump(new_content, f)


def copy_fw_folder(previous_fw, new_fw):
    previous_fw_folder = os.path.join("frameworks", previous_fw)
    if not os.path.exists(previous_fw_folder):
        sys.exit(f"No previous framework for iteration {previous_fw}")

    print(f"Copying all files from {previous_fw} to {new_fw}")
    try:
        shutil.copytree(previous_fw_folder, os.path.join("frameworks", new_fw))
    except FileExistsError:
        print("Skipping - folder exists")


if __name__ == '__main__':
    current_dir = os.path.dirname(__file__)
    arguments = docopt(__doc__)
    framework_family = arguments['--family']
    if framework_family not in ('g-cloud', 'digital-outcomes-and-specialists'):
        sys.exit('Invalid framework family - must be g-cloud or digital-outcomes-and-specialists')

    iteration_number = int(arguments['--iteration'])

    new_fw = f"{framework_family}-{iteration_number}"
    previous_fw = f"{framework_family}-{iteration_number - 1}"
    following_fw = f"{framework_family}-{iteration_number + 1}"

    copy_fw_folder(previous_fw, new_fw)
    update_metadata(previous_fw, new_fw, following_fw)
