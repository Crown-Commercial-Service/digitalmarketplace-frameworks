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
from docopt import docopt


def main(framework_family, iteration_number):
    new_fw = f"{framework_family}-{iteration_number}"
    previous_fw = f"{framework_family}-{iteration_number - 1}"
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
    main(framework_family, iteration_number)
