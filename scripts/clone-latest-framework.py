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
    # Hack for G-Cloud which helpfully contains a dash
    return fw_slug.replace('-', ' ').replace('g cloud', 'G-Cloud').title()


def get_nbsp_fw_name_from_slug(fw_slug):
    # Some places use G-Cloud&bsp;11 for non-breaking spaces
    return get_fw_name_from_slug(fw_slug).replace(" ", "&nbsp;")


def replace_framework_in_content(current_content, root, file):
    updated_content = None
    if previous_name in current_content:
        updated_content = current_content.replace(previous_name, new_name)
        print(f"Replacing framework name in {root}/{file}")
        # Keep the changes for the next replacement
        current_content = updated_content
    if previous_nbsp_name in current_content:
        updated_content = current_content.replace(previous_nbsp_name, new_nbsp_name)
        print(f"Replacing framework name (with nbsp) in {root}/{file}")
        # Keep the changes for the next replacement
        current_content = updated_content
    if previous_fw_slug in current_content:
        updated_content = current_content.replace(previous_fw_slug, new_fw_slug)
        print(f"Replacing framework slug in {root}/{file}")

    # If we return updated_content = None, we know that no changes have been made
    return updated_content


def replace_hardcoded_framework_name_and_slug():
    new_fw_root = os.path.join('frameworks', new_fw_slug)
    for root, dirs, files in os.walk(new_fw_root, topdown=True):
        if 'metadata' in root:
            # Metadata is updated separately
            continue
        for file in files:
            with open(os.path.join(root, file), 'r') as f:
                current_content = f.read()
                updated_content = replace_framework_in_content(current_content, root, file)
            # Only write if there's been a change
            if updated_content:
                with open(os.path.join(root, file), 'w') as f:
                    f.write(updated_content)


def update_metadata():
    print("Setting metadata")
    # Set copy_services.yml content
    copy_services_file = os.path.join("frameworks", new_fw_slug, 'metadata', METADATA_FILES['copy_services'])
    with open(copy_services_file) as f:
        content = yaml.safe_load(f)
        # TODO: preserve ordering
        new_content = {
            'source_framework': previous_fw_slug,
            'questions_to_copy': content['questions_to_copy']
        }

    with open(copy_services_file, 'w') as f:
        yaml.dump(new_content, f)

    # Set following_framework.yml content
    following_fw_file = os.path.join("frameworks", new_fw_slug, 'metadata', METADATA_FILES['following_framework'])
    with open(following_fw_file) as f:
        content = yaml.safe_load(f)
        new_content = {
            'framework': {
                'slug': following_fw_slug,
                'name': get_fw_name_from_slug(following_fw_slug),
                'coming': str(int(content['framework']['coming']) + 1)
            }
        }
    with open(following_fw_file, 'w') as f:
        yaml.dump(new_content, f)


def copy_fw_folder():
    previous_fw_folder = os.path.join("frameworks", previous_fw_slug)
    if not os.path.exists(previous_fw_folder):
        sys.exit(f"No previous framework for iteration {previous_fw_slug}")

    print(f"Copying all files from {previous_fw_slug} to {new_fw_slug}")
    try:
        shutil.copytree(previous_fw_folder, os.path.join("frameworks", new_fw_slug))
    except FileExistsError:
        print("Skipping - folder exists")


if __name__ == '__main__':
    current_dir = os.path.dirname(__file__)
    arguments = docopt(__doc__)
    framework_family = arguments['--family']
    if framework_family not in ('g-cloud', 'digital-outcomes-and-specialists'):
        sys.exit('Invalid framework family - must be g-cloud or digital-outcomes-and-specialists')

    iteration_number = int(arguments['--iteration'])

    # Set all the strings up front: framework slug, name and non-breaking-space name
    new_fw_slug = f"{framework_family}-{iteration_number}"
    previous_fw_slug = f"{framework_family}-{iteration_number - 1}"
    following_fw_slug = f"{framework_family}-{iteration_number + 1}"
    previous_name = get_fw_name_from_slug(previous_fw_slug)
    new_name = get_fw_name_from_slug(new_fw_slug)
    previous_nbsp_name = get_nbsp_fw_name_from_slug(previous_fw_slug)
    new_nbsp_name = get_nbsp_fw_name_from_slug(new_fw_slug)

    copy_fw_folder()
    replace_hardcoded_framework_name_and_slug()
    update_metadata()
