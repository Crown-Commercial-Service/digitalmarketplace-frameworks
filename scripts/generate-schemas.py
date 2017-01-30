#!/usr/bin/env python
"""Generate JSON schemas from the frameworks questions content.

Usage:
    generate-schemas.py --output-path=<output_path>

"""
import os
import sys
sys.path.insert(0, '.')

from docopt import docopt
from schema_generator import generate_schema, SCHEMAS


if __name__ == '__main__':
    arguments = docopt(__doc__)
    OUTPUT_DIR = arguments['--output-path']
    if not os.path.exists(OUTPUT_DIR):
        print("Creating {} directory".format(OUTPUT_DIR))
        os.makedirs(OUTPUT_DIR)
    for schema_type in SCHEMAS:
        for schema in SCHEMAS[schema_type]:
            generate_schema(OUTPUT_DIR, schema_type, *schema)
