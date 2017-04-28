from collections import OrderedDict

from dmcontent.questions import Hierarchy
from schema_generator.search import _checkbox_tree_transformation_generator


def test_checkbox_tree_transformation_generator():
    question = {
        "id": 'someQuestion',
        "options": [
            {
                'label': 'cat 1',
                'options': [
                    {'label': 'sub cat 1.1'},
                    {'label': 'sub cat 1.2', 'value': 'sc1-2'},
                    ]
            },
            {
                'label': 'cat 2',
                'options': [
                    {'label': 'sub cat 2.1'},
                    {'label': 'sub cat 2.2'}
                ]
            }
        ]
    }
    result = _checkbox_tree_transformation_generator(Hierarchy(question))

    assert {
        'append_conditionally': OrderedDict((
            ('field', 'someQuestion'),
            ('any_of', [
                'sub cat 1.1', 'sc1-2'
            ]),
            ('append_value', ['cat 1'])
        ))
    } in result

    assert {
        'append_conditionally': OrderedDict((
            ('field', 'someQuestion'),
            ('any_of', [
                'sub cat 2.1', 'sub cat 2.2'
            ]),
            ('append_value', ['cat 2'])
        ))
    } in result
