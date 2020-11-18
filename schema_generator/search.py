from __future__ import print_function

import os.path
import sys
import json
from collections import OrderedDict
from itertools import chain

from dmcontent import ContentLoader, utils


_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _get_questions_by_type(framework_slug, doc_type, question_types):
    manifest_name = '{}_search_filters'.format(doc_type)
    loader = ContentLoader(_base_dir)
    loader.load_manifest(
        framework_slug,
        doc_type,
        manifest_name,
    )

    manifest = loader.get_manifest(framework_slug, manifest_name)
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
                ('append_value', [utils.get_option_value(option)]),
            ))
        }
        for option in checkbox_question.get('options')
        if option.get('derived_from', None) is not None
    ]

    return retval


TRANSFORMATION_GENERATORS = {
    'checkbox_tree': _checkbox_tree_transformation_generator,
    'checkboxes': _derived_options_transformation_generator,
    'radios': _derived_options_transformation_generator
}


def get_transformations(framework_slug, doc_type):
    for question in _get_questions_by_type(framework_slug, doc_type, TRANSFORMATION_GENERATORS.keys()):
        for transformer in TRANSFORMATION_GENERATORS[question.type](question):
            yield transformer


def generate_search_mapping(framework_slug, doc_type, file_handle, mapping_type, extra_meta={}):
    with open(os.path.join(
        _base_dir,
        "frameworks",
        framework_slug,
        "search_mappings",
        "{}.json".format(doc_type),
    ), 'r') as h_template:
        mapping_json = json.load(h_template, object_pairs_hook=OrderedDict)  # preserve template order for git history

    mappings = mapping_json["mappings"]

    # Elasticsearch 7 removes mapping types by default
    # https://www.elastic.co/guide/en/elasticsearch/reference/7.10/removal-of-types.html
    include_type_name = False
    if mapping_type in mappings:
        include_type_name = True

    original_meta = mappings[mapping_type].get("_meta", {}) if include_type_name else mappings.get("_meta", {})

    # starting our final _meta dict from scratch so we can ensure extra_meta gets the top spot, in ordered output
    meta = OrderedDict((
        *((k, v) for k, v in extra_meta.items()),
        # we want entries from original_meta to come *after* entries from extra_meta, but want to extra_meta entries
        # to override original_meta, so ignore original_meta entries which are already in extra_meta
        *((k, v) for k, v in original_meta.items() if k not in extra_meta),
        ("transformations", list(chain(
            extra_meta.get("transformations", ()),
            original_meta.get("transformations", ()),
            get_transformations(framework_slug, doc_type),
        ))),
    ))

    if include_type_name:
        mappings[mapping_type]["_meta"] = meta
    else:
        mappings["_meta"] = meta

    json.dump(mapping_json, file_handle, indent=2, separators=(',', ': '))
    print('', file=file_handle)


def generate_config(framework_slug, doc_type, extra_meta, output_dir=None):
    if output_dir:
        with open(os.path.join(output_dir, '{}-{}.json'.format(doc_type, framework_slug)), 'w') as base_mapping:
            generate_search_mapping(framework_slug, doc_type, base_mapping, doc_type, extra_meta)
    else:
        generate_search_mapping(framework_slug, doc_type, sys.stdout, doc_type, extra_meta)
