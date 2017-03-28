#!/usr/bin/env python
"""Generate validation JSON schemas from the frameworks questions content.

Usage:
    generate-validation-schemas.py --output-path=<output_path>

"""
import os
import sys
sys.path.insert(0, '.')

from docopt import docopt
from schema_generator.validation import generate_schema_todir, SCHEMAS


if __name__ == '__main__':
    arguments = docopt(__doc__)
    OUTPUT_DIR = arguments['--output-path']
    if not os.path.exists(OUTPUT_DIR):
        print("Creating {} directory".format(OUTPUT_DIR))
        os.makedirs(OUTPUT_DIR)
    for schema_type in SCHEMAS:
        for schema in SCHEMAS[schema_type]:
            generate_schema_todir(OUTPUT_DIR, schema_type, *schema)
