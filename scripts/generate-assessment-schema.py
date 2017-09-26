#!/usr/bin/env python
"""Generate assessment JSON schema for a framework's declaration to stdout.

Usage:
    generate-assessment-schema.py <framework_slug>

"""
import sys
sys.path.insert(0, '.')

import json

from docopt import docopt
from schema_generator.assessment import generate_schema


if __name__ == '__main__':
    arguments = docopt(__doc__)
    schema = generate_schema(arguments["<framework_slug>"], "declaration", "declaration")
    json.dump(schema, sys.stdout, sort_keys=True, indent=2, separators=(',', ': '))
