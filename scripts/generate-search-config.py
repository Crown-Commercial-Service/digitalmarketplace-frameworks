#!/usr/bin/env python
"""Generate an Elasticsearch mapping using the template stored with the framework.

At the time of writing, most of the search mapping is written by hand, in
the search_mapping.json template file. This script adds to that template
and writes it to a <doc_type>.json file in the directory provided, which
should usually be the 'mappings' directory in a checkout of the Search API.

To preview the mapping that will be generated, do not specify the output path.

Note that most of the digital marketplace code only supports one index (and
therefore one mapping) per doc type at a time. Therefore, care should be taken
with the release process to ensure that indexing for the currently-live
framework continues as expected, especially if the new framework's mapping is
not backward-compatible with the old one.

See https://github.com/alphagov/digitalmarketplace-search-api/blob/master/README.md#updating-the-index-mapping
for more information about how to apply the updated mapping to an index.
Backward-incompatible changes to the mapping should be applied by creating a new
index, and swapping the index aliases over when ready (for example when deploying
a frontend that references the new search manifest).

Usage:
    generate-search-config.py [--help] <framework_slug> <doc_type> [--output-path=<output_path>]

"""
import os
import sys
import json
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
    doc_type = arguments['<doc_type>']

    with open(os.path.join(base_dir, 'package.json')) as version_handle:
        extra_meta = OrderedDict((
            ('_', 'DO NOT UPDATE BY HAND'),
            ('version', json.load(version_handle)['version']),
            ('generated_from_framework', framework_slug),
            ('doc_type', doc_type),
            ('generated_by', os.path.abspath(__file__)),
            ('generated_time', datetime.utcnow().isoformat()),
        ))

    generate_config(framework_slug, doc_type, extra_meta, output_dir)
