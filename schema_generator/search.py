from __future__ import print_function

import os.path
import sys
import json
from collections import defaultdict, OrderedDict

from dmcontent import ContentLoader, utils


_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _get_questions_by_type(framework_slug, question_types):
    loader = ContentLoader(_base_dir)
    loader.load_manifest(
        framework_slug,
        'services',
        'search_filters'
    )

    manifest = loader.get_manifest(framework_slug, 'search_filters')
    return (q for q in sum((s.questions for s in manifest.sections), []) if q.type in question_types)


def _checkbox_tree_transformation_generator(checkbox_tree_question):
    def update_ancestors_dict(options, leaf_values_dict, parents):
        for option in options:
            children = option.get('options', [])
            if not children:
                if parents:
                    if parents not in leaf_values_dict:
                        leaf_values_dict[parents] = list()
                        # list of child-values preserves order from the source yaml, for the benefit of
                        # git history in output file

                    leaf_values_dict[parents].append(utils.get_option_value(option))
            else:
                update_ancestors_dict(children, leaf_values_dict, parents.union([utils.get_option_value(option)]))

    leaf_values_by_ancestor_set = OrderedDict()  # again, preserve order from source yaml
    update_ancestors_dict(checkbox_tree_question.options, leaf_values_by_ancestor_set, parents=frozenset())

    return [
        {
            'append_conditionally': OrderedDict((
                ('field', checkbox_tree_question.id),
                ('any_of', child_values),
                ('append_value', sorted(ancestor_values)),
            ))
        } for ancestor_values, child_values in leaf_values_by_ancestor_set.items()
    ]


def _derived_options_transformation_generator(checkbox_question):
    retval = [
        {
            'append_conditionally': OrderedDict((
                ('field', option['derived_from']['question']),
                ('target_field', checkbox_question.id),
                ('any_of', option['derived_from']['any_of']),
                ('append_value', [option['label']]),
            ))
        }
        for option in checkbox_question.get('options')
        if option.get('derived_from', None) is not None
    ]

    return retval


TRANSFORMATION_GENERATORS = {
    'checkbox_tree': _checkbox_tree_transformation_generator,
    'checkboxes': _derived_options_transformation_generator
}


def get_transformations(framework_slug):
    for question in _get_questions_by_type(framework_slug, TRANSFORMATION_GENERATORS.keys()):
        for transformer in TRANSFORMATION_GENERATORS[question.type](question):
            yield transformer


def generate_search_mapping(framework_slug, file_handle, mapping_type, extra_meta={}):
    with open(os.path.join(_base_dir, 'frameworks', framework_slug, 'search_mapping.json'), 'r') as h_template:
        mapping_json = json.load(h_template, object_pairs_hook=OrderedDict)  # preserve template order for git history

    mapping_json['mappings'][mapping_type]['_meta'].update(extra_meta)
    mapping_json['mappings'][mapping_type]['_meta']['transformations'] = list(get_transformations(framework_slug))

    json.dump(mapping_json, file_handle, indent=2, separators=(',', ': '))
    print('', file=file_handle)


def generate_config(framework_slug, extra_meta, output_dir=None):
    mapping_type_name = 'services'
    if output_dir:
        with open(os.path.join(output_dir, 'services.json'), 'w') as h_services_mapping:
            generate_search_mapping(framework_slug, h_services_mapping, mapping_type_name, extra_meta)
    else:
        generate_search_mapping(framework_slug, sys.stdout, mapping_type_name, extra_meta)
