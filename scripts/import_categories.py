#! /usr/bin/env python
"""
Import from a CSV file containing a two-level categorisation for G-Cloud, create
or overwrite a YAML structure as required for our framework question definition.

We expect to see three columns, labelled as follows:

 "Top level (lot)" - used to filter the rows - provide the lot as the second argument
 "Primary category" - more broad categorisation
 "Secondary category" - more specific categorisation (if any)

Example data file <<END
Top level (lot),Primary category,Secondary category
Cloud Hosting,"Archiving, backup and disaster recovery",
Cloud Software,Accounting and finance,Accounts payable
END

Usage:
    scripts/import-categories.py <input-csv-file> <lot> [<output-yaml-file>] [-h|--help]

"""

from docopt import docopt
import yaml
from collections import OrderedDict
import csv
import sys


if __name__ == '__main__':
    arguments = docopt(__doc__)
    primary_by_label = OrderedDict()
    lot_filter = arguments['<lot>']

    csv_path = arguments['<input-csv-file>']
    with open(csv_path, 'r') as h_csv:
        reader = csv.DictReader(h_csv)
        for row in reader:
            lot = row['Top level (lot)'].strip()
            if lot == lot_filter:
                primary_label = row['Primary category'].strip()
                secondary_label = row['Secondary category'].strip()
                primary = primary_by_label.get(primary_label, dict())
                if not primary:
                    primary_by_label[primary_label] = primary
                    primary['label'] = primary_label
                    if secondary_label:
                        primary['options'] = list()

                if secondary_label:
                    secondary = dict()
                    secondary['label'] = secondary_label
                    primary['options'].append(secondary)

    if not primary_by_label:
        print("No data found in that lot")
        sys.exit(1)

    output_file = arguments.get('<output-yaml-file>')
    if output_file:
        with open(output_file, 'r') as yaml_file:
            question_data = yaml.safe_load(yaml_file)
    else:
        question_data = {}

    # not sorting top level categories - order in source is not alphabetical, and this is on purpose
    question_data['options'] = primary_by_label.values()

    for option in question_data['options']:
        children = option.get('options')
        # sort with 'other' last
        if children:
            children.sort(key=lambda o: ('other' in o['label'].lower().split(), o['label'].lower()))

    if output_file:
        with open(output_file, 'w') as h_yaml:
            yaml.safe_dump(question_data, h_yaml, default_flow_style=False)
    else:
        yaml.safe_dump(question_data, sys.stdout, default_flow_style=False)
