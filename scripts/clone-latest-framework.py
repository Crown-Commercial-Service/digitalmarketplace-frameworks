#!/usr/bin/env python
"""Clone a new framework, based on the latest iteration, into the same level directory.

- Finds the last iteration of the given framework family type
- Copies all content to a new folder
- Update metadata
- Update hardcoded content of framework name in declaration questions 'G-Cloud 11', 'G-Cloud&nsbp;11'
- Update hardcoded content of framework slug in urls, declaration
- Set any dates to a point in the far-future e.g. 1 Jan 2525 (using <launch_year> to detect last year's dates)

Usage:
    clone-latest-framework.py --family=<framework_family> --iteration=<iteration_number> --launch-year=<launch_year>
    [--question-copy-method=exclude|copy]

Example:
    ./scripts/clone-latest-framework.py --family=g-cloud --iteration=12 --launch-year=2020
    --question-copy-method=exclude
"""
import sys
sys.path.insert(0, '.')
from docopt import docopt
from script_helpers.clone_helpers import FrameworkContentCloner


if __name__ == '__main__':
    arguments = docopt(__doc__)
    framework_family = arguments['--family']
    if framework_family not in ('g-cloud', 'digital-outcomes-and-specialists'):
        sys.exit('Invalid framework family - must be g-cloud or digital-outcomes-and-specialists')

    iteration_number = int(arguments['--iteration'])
    launch_year = int(arguments['--launch-year'])
    question_copy_method = arguments.get('--question-copy-method')

    cloner = FrameworkContentCloner(
        framework_family, iteration_number, launch_year, question_copy_method=question_copy_method
    )
    cloner.clone()
