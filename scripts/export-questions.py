#!/usr/bin/env python
"""
Export questions for a given framework.

Use the --declaration flag to export declaration questions.
Provide a --lot-slug argument to export service questions (filtering out questions that aren't required for the lot)

Usage: scripts/export-questions.py <framework_slug> --output-dir=<output_dir> [--declaration] [--lot-slug=<lot_slug>]

"""
import os
import csv
from docopt import docopt
from dmcontent import ContentLoader


def load_question_sections(framework_slug, service):
    loader = ContentLoader('./')
    if service:
        section = 'services'
        manifest = 'edit_submission'
    else:
        section = 'declaration'
        manifest = 'declaration'
    loader.load_manifest(framework_slug, section, manifest)
    return loader.get_manifest(framework_slug, manifest)


def get_answer_labels(question):
    # Get answer labels where provided
    if question.get('options'):
        # Covers both radio and checkbox type questions
        return [option.get('label') for option in question.get('options')]
    if question['type'] == 'boolean':
        return ["Yes", "No"]
    return []


def _strip_tags(row):
    # Remove layout markup - if anything more complex is needed use e.g. BeautifulSoup
    cleaned_row = [
        cell.replace('<p>', '').replace('</p>', '').
            replace('<li>', '-').replace('</li>', '').
            replace('<ul>', '').replace('</ul>', '')
        for cell in row
    ]
    return cleaned_row


def _create_row(section, question):
    row = [
        str(section['name']),
        str(section['description'] or ''),
        "{}\n{}".format(question['question'], question.get('question_advice', '')),
        str(question.get('hint', ''))
    ]
    if question.get('options'):
        row.extend(get_answer_labels(question))
    return _strip_tags(row)


def parse_questions(framework_slug, lot_slug=None):
    manifest = load_question_sections(framework_slug, service=lot_slug)
    rows = []
    for section in manifest.sections:
        for question in section.questions:
            # Check the question is from the declaration, or a lot-specific question
            if lot_slug is None or question.filter({"lot": lot_slug}):
                rows.append(_create_row(section, question))
                # Handle multiquestions
                if question.get('questions'):
                    for followup in question['questions']:
                        if lot_slug is None or followup.filter({"lot": lot_slug}):
                            rows.append(_create_row(section, followup))
    return rows


if __name__ == '__main__':
    current_dir = os.path.dirname(__file__)
    arguments = docopt(__doc__)
    output_dir = arguments['--output-dir']
    framework_slug = arguments['<framework_slug>']
    lot_slug = arguments['--lot-slug']
    export_declaration = arguments['--declaration']

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if export_declaration:
        file_name = '{}-declaration-questions.csv'.format(framework_slug)
        rows = parse_questions(framework_slug)
    elif lot_slug:
        file_name = '{}-{}-service-questions.csv'.format(framework_slug, lot_slug)
        rows = parse_questions(framework_slug, lot_slug)
    else:
        raise ValueError("Please supply either --declaration or a --lot-slug.")

    file_path = os.path.join(output_dir, file_name)

    headers = [
        "Section / page title",
        "Page description and hint",
        "Question",
        "Description & hint",
        "Answer1",
        "Answer2",
        "Answer3",
        "Answer4",
        "Answer5",
        "Answer6",
    ]

    with open(file_path, 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', quotechar='"')
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)
