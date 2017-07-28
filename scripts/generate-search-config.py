#!/usr/bin/env python
"""Generate an Elasticsearch mapping using the template stored with the framework.

At the time of writing, most of the search mapping is written by hand, in
the search_mapping.json template file. This script adds to that template
and writes it to a services.json file in the directory provided, which
should be reference the 'mappings' directory in a checkout of the Search API.

To preview the mapping that will be generated, do not specify the output path.

Note that the Search API only supports one mapping at a time, which will be
used for any index relating to any G-Cloud framework. Therefore, care should
be taken with the release process to ensure that indexing for the currently-
live framework continues as expected, especially if the new framework's
mapping is not backward-compatible with the old one.


Usage:
    generate-validation-schemas.py [--help] <framework_slug> [--output-path=<output_path>]

"""
import os
import sys
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)
from datetime import datetime
from collections import OrderedDict

from docopt import docopt
from schema_generator.search import generate_config


if __name__ == '__main__':
    arguments = docopt(__doc__)
    output_dir = arguments.get('--output-path')
    if output_dir and not os.path.exists(output_dir):
        sys.exit('Specified output directory does not exist.')

    framework_slug = arguments['<framework_slug>']

    with open(os.path.join(base_dir, 'VERSION.txt'), 'r') as version_handle:
        extra_meta = OrderedDict((
            ('_', 'DO NOT UPDATE BY HAND'),
            ('version', version_handle.read().strip()),
            ('generated_from_framework', framework_slug),
            ('generated_by', os.path.abspath(__file__)),
            ('generated_time', datetime.utcnow().isoformat()),
        ))

    generate_config(framework_slug, extra_meta, output_dir)
