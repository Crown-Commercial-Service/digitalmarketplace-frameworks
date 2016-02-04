#!/usr/bin/env python
"""Generate JSON schemas from the frameworks questions content.

Usage:
    generate-schemas.py --output-path=<output_path>

"""
import sys
sys.path.insert(0, '.')

from docopt import docopt
from schema_generator import generate_schema, SCHEMAS


if __name__ == '__main__':
    arguments = docopt(__doc__)
    for schema_type in SCHEMAS:
        for schema in SCHEMAS[schema_type]:
            generate_schema(arguments['--output-path'], schema_type, *schema)
