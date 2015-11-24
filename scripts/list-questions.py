#!/usr/bin/env python
"""List paths to question files

Usage:
    list-questions.py <framework_slug> <question_group> <manifest> [<section_number>]
"""
import os

from docopt import docopt
from dmutils.content_loader import ContentLoader


def get_question_paths(framework_slug, questions, section):
    print(section)
    print(dir(section))
    prefix = os.path.join('frameworks', framework_slug, 'questions', questions)
    return [
        os.path.join(prefix, '{}.yml'.format(question.id))
        for question
        in section.questions
    ]


def make_question_path(framework_slug, question_group, question_id):
    return os.path.join(
        'frameworks', framework_slug, 'questions', question_group,
        '{}.yml'.format(question_id))


def main(framework_slug, question_group, manifest, section_number):
    loader = ContentLoader('./')
    loader.load_manifest(framework_slug, question_group, manifest)
    builder = loader.get_builder(framework_slug, manifest)

    if section_number is not None:
        section_number = int(section_number)
        question_paths = [
            make_question_path(framework_slug, question_group, question_id)
            for question_id
            in builder.sections[section_number-1].get_question_ids()
        ]
    else:
        question_paths = []
        for section in builder.sections:
            question_paths += [
                make_question_path(framework_slug, question_group, question_id)
                for question_id
                in section.get_question_ids()
            ]

    for question_path in question_paths:
        print("="*20)
        with open(question_path) as f:
            print(f.read())


if __name__ == '__main__':
    arguments = docopt(__doc__)
    main(
        arguments['<framework_slug>'],
        arguments['<question_group>'],
        arguments['<manifest>'],
        arguments['<section_number>'])

