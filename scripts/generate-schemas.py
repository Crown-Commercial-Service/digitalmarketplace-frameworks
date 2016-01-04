#!/usr/bin/env python
"""Generate JSON schemas from the frameworks questions content.

Usage:
    generate-schemas.py --output-path=<output_path>

"""


from docopt import docopt
from schema_generator import generate_schema, SCHEMAS


if __name__ == '__main__':
    arguments = docopt(__doc__)
    for schema in SCHEMAS:
        generate_schema(arguments['--output-path'], *schema)
