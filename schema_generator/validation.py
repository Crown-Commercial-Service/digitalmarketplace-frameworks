import os
import re
import json
from dmcontent import ContentLoader

MANIFESTS = {
    'services': {
        'question_set': 'services',
        'manifest': 'edit_submission'
    },
    'briefs': {
        'question_set': 'briefs',
        'manifest': 'edit_brief'
    },
    'brief-responses': {
        'question_set': 'brief-responses',
        'manifest': 'edit_brief_response'
    },
    'brief-awards': {
        'question_set': 'briefs',
        'manifest': 'award_brief'
    },
}

LEGACY_GCLOUD_LOTS = [
    ('scs', 'SCS'), ('iaas', 'IaaS'), ('paas', 'PaaS'), ('saas', 'SaaS')
]
G_CLOUD_LOTS = [
    ('cloud-hosting', 'Cloud Hosting'),
    ('cloud-software', 'Cloud Software'),
    ('cloud-support', 'Cloud Support')
]
DOS_LOTS = [
    ('digital-outcomes', 'Digital outcomes'),
    ('digital-specialists', 'Digital specialists'),
    ('user-research-participants', 'User research participants'),
    ('user-research-studios', 'User research studios')
]

FRAMEWORKS_AND_LOTS = {
    "g-cloud": [
        {'framework_slug': 'g-cloud-7', 'framework_name': "G-Cloud 7", 'lots': LEGACY_GCLOUD_LOTS},
        {'framework_slug': 'g-cloud-8', 'framework_name': "G-Cloud 8", 'lots': LEGACY_GCLOUD_LOTS},
        {'framework_slug': 'g-cloud-9', 'framework_name': "G-Cloud 9", 'lots': G_CLOUD_LOTS},
        {'framework_slug': 'g-cloud-10', 'framework_name': "G-Cloud 10", 'lots': G_CLOUD_LOTS},
        {'framework_slug': 'g-cloud-11', 'framework_name': "G-Cloud 11", 'lots': G_CLOUD_LOTS},
        {'framework_slug': 'g-cloud-12', 'framework_name': "G-Cloud 12", 'lots': G_CLOUD_LOTS},
    ],
    "digital-outcomes-and-specialists": [
        {
            'framework_slug': 'digital-outcomes-and-specialists',
            'framework_name': "Digital Outcomes and Specialists",
            'lots': DOS_LOTS
        },
        {
            'framework_slug': 'digital-outcomes-and-specialists-2',
            'framework_name': "Digital Outcomes and Specialists 2",
            'lots': DOS_LOTS
        },
        {
            'framework_slug': 'digital-outcomes-and-specialists-3',
            'framework_name': "Digital Outcomes and Specialists 3",
            'lots': DOS_LOTS
        },
        {
            'framework_slug': 'digital-outcomes-and-specialists-4',
            'framework_name': "Digital Outcomes and Specialists 4",
            'lots': DOS_LOTS
        },
        {
            'framework_slug': 'digital-outcomes-and-specialists-5',
            'framework_name': "Digital Outcomes and Specialists 5",
            'lots': DOS_LOTS
        },
    ]
}


def _get_schema_title_and_slugs(schema_type, framework_family=None, exclude_lot=None):
    titles_and_slugs = []
    for family, framework_list in FRAMEWORKS_AND_LOTS.items():
        if framework_family:
            # Some schemas are only required for DOS frameworks
            if framework_family != family:
                continue

        for framework in framework_list:
            for lot_slug, lot_name in framework['lots']:
                if exclude_lot:
                    # Some lots don't have briefs/brief response/brief award schemas
                    if exclude_lot == lot_slug:
                        continue

                titles_and_slugs.append(
                    (
                        "{} {} {}".format(framework['framework_name'], lot_name, schema_type),
                        framework['framework_slug'],
                        lot_slug
                    )
                )
    return titles_and_slugs


SCHEMAS = {
    'services': _get_schema_title_and_slugs("Service"),
    'briefs': _get_schema_title_and_slugs(
        "Brief", "digital-outcomes-and-specialists", exclude_lot="user-research-studios"
    ),
    'brief-responses': _get_schema_title_and_slugs(
        "Brief Response", "digital-outcomes-and-specialists", exclude_lot="user-research-studios"
    ),
    'brief-awards': _get_schema_title_and_slugs(
        "Brief Award", "digital-outcomes-and-specialists", exclude_lot="user-research-studios"
    )
}


def load_questions(schema_type, framework_slug, lot_slug):
    loader = ContentLoader('./')
    loader.load_manifest(
        framework_slug,
        MANIFESTS[schema_type]['question_set'],
        MANIFESTS[schema_type]['manifest']
    )

    manifest = loader.get_manifest(framework_slug, MANIFESTS[schema_type]['manifest']).filter(
        {'lot': lot_slug},
        dynamic=False
    )
    return {q['id']: q for q in sum((s.questions for s in manifest.sections), [])}


def merge_schemas(a, b):
    if not (isinstance(a, dict) and isinstance(b, dict)):
        raise TypeError("Error merging unsupported types '{}' and '{}'".format(
            type(a).__name__, type(b).__name__
        ))

    result = a.copy()
    for key, val in b.items():
        if isinstance(result.get(key), dict):
            result[key] = merge_schemas(a[key], val)
        elif isinstance(result.get(key), list):
            result[key] = result[key] + val
        else:
            result[key] = val

    return result


def empty_schema(schema_name):
    return {
        "title": "{} Schema".format(schema_name),
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "additionalProperties": False,
        "properties": {},
        "required": [],
    }


def drop_non_schema_questions(questions):
    # These questions are used to generate questions in the UI but are
    # not used to validate the response, so we remove them....
    for key in ['id', 'lot', 'lotName']:
        questions.pop(key, None)


def text_property(question):
    data = {
        "type": "string",
        "minLength": 0 if question.get('optional') else 1,
    }

    format_limit = question.get('limits', {}).get('format')
    if format_limit:
        data['format'] = format_limit

    data.update(parse_question_limits(question))

    return {question['id']: data}


def date_property(question):
    return {question['id']: {"type": "string", "format": "date"}}


def uri_property(question):
    return {question['id']: {
        "type": "string",
        "format": "uri",
    }}


def checkbox_property(question):
    """
    Convert a checkbox question into JSON Schema.
    """
    return {question['id']: {
        "type": "array",
        "uniqueItems": True,
        "minItems": 0 if question.get('optional') else 1,
        "maxItems": question.get('number_of_items', len(question['options'])),
        "items": {
            "enum": [
                option.get('value', option['label'])
                for option in question['options']
            ]
        }
    }}


def checkbox_tree_property(question):
    """
    Convert a checkbox tree question into JSON Schema by flattening the tree structure. Only leaf
    nodes can be selected.
    """
    def flatten(options):
        for option in options:
            children = option.get('options', [])
            if not children:
                yield option
            else:
                for child in flatten(children):
                    yield child

    # items may not be unique, so using a set not a list
    all_items = {option.get('value', option['label']) for option in flatten(question['options'])}

    schema_fragment = {question['id']: {
        "type": "array",
        "uniqueItems": True,
        "minItems": 0 if question.get('optional') else 1,
        "items": {
            "enum": sorted(all_items)
        }
    }}

    # add maxitems conditionally: a restriction based on the number of items in the tree isn't very useful
    if question.get('number_of_items'):
        schema_fragment[question['id']]['maxItems'] = question.get('number_of_items')

    return schema_fragment


def radios_property(question):
    return {question['id']: {
        "enum": [
            option.get('value', option['label'])
            for option in question['options']
        ]
    }}


def boolean_property(question):
    data = {"type": "boolean"}
    if question.get("required_value") is not None:
        data = {"enum": [question["required_value"]]}
    return {question['id']: data}


def list_property(question):
    items = {
        "type": "string",
        "maxLength": 100,
        "pattern": "^(?:\\S+\\s+){0,9}\\S+$"
    }

    items.update(parse_question_limits(question, for_items=True))

    return {question['id']: {
        "type": "array",
        "minItems": 0 if question.get('optional') else 1,
        "maxItems": question.get('number_of_items', 10),
        "items": items
    }}


def boolean_list_property(question):
    return {question['id']: {
        "type": "array",
        "minItems": 0 if question.get('optional') else 1,
        "maxItems": question.get('number_of_items', 10),
        "items": {
            "type": "boolean"
        }
    }}


def price_string(optional, decimal_place_restriction=False):
    pattern = r"^\d{1,15}(?:\.\d{1,5})?$"  # up to 5 decimal places allowed eg 0, 90, 90.1, 90.12345
    # restricted to positive numbers with 0dp or 2dp only eg 90 or 90.12
    restricted_pattern = r"^[1-9](?:\d{1,14})?(?:\.\d{2})?$|^0\.(?!00)\d{2}$"

    if decimal_place_restriction:
        pattern = restricted_pattern
    if optional:
        pattern = r"^$|" + pattern
    return {
        "type": "string",
        "pattern": pattern,
    }


def pricing_property(question):
    pricing = {}
    if 'price' in question.fields:
        pricing[question.fields['price']] = price_string(
            'price' in question.get('optional_fields', []),
            question.decimal_place_restriction
        )
    if 'minimum_price' in question.fields:
        pricing[question.fields['minimum_price']] = price_string(
            'minimum_price' in question.get('optional_fields', []),
            question.decimal_place_restriction
        )
    if 'maximum_price' in question.fields:
        pricing[question.fields['maximum_price']] = price_string(
            'maximum_price' in question.get('optional_fields', []),
            question.decimal_place_restriction
        )
    if 'price_unit' in question.fields:
        pricing[question.fields['price_unit']] = {
            "enum": [
                "Unit",
                "Person",
                "Licence",
                "User",
                "Device",
                "Instance",
                "Server",
                "Virtual machine",
                "Transaction",
                "Megabyte",
                "Gigabyte",
                "Terabyte"
            ]
        }
        if 'price_unit' in question.get('optional_fields', []):
            pricing[question.fields['price_unit']]['enum'].insert(0, "")
    if 'price_interval' in question.fields:
        pricing[question.fields['price_interval']] = {
            "enum": [
                "Second",
                "Minute",
                "Hour",
                "Day",
                "Week",
                "Month",
                "Quarter",
                "6 months",
                "Year"
            ]
        }
        if 'price_interval' in question.get('optional_fields', []):
            pricing[question.fields['price_interval']]['enum'].insert(0, "")

    if 'hours_for_price' in question.fields:
        pricing[question.fields['hours_for_price']] = {
            "enum": [
                "1 hour",
                "2 hours",
                "3 hours",
                "4 hours",
                "5 hours",
                "6 hours",
                "7 hours",
                "8 hours"
            ]
        }

    return pricing


def number_property(question):
    limits = question.get('limits', {})
    output = {question['id']: {
        "minimum": limits.get('min_value') or 0,
        "type": "integer" if limits.get('integer_only') else "number"
    }}
    inclusive_max = bool(limits.get('integer_only'))
    maximum = limits['max_value'] if limits.get('max_value') is not None else 100
    output[question['id']].update({"maximum": maximum} if inclusive_max else {"exclusiveMaximum": maximum})
    return output


def multiquestion(question):
    """
    Moves subquestions of multiquestions into fully fledged questions.
    """

    if question._data['type'] == 'dynamic_list':
        return _dynamic_list(question)
    else:
        property_schema, schema_addition = _flat_multiquestion(question)
        required_fields = _flat_multiquestion_required(question)
        if required_fields:
            required_schema = {"required": _flat_multiquestion_required(question)}
            schema_addition = merge_schemas(schema_addition, required_schema)

        return property_schema, schema_addition


def _dynamic_list(question):
    return {
        question['id']: {
            "type": "array",
            "minItems": 0 if question.get('optional') else 1,
            "items": _nested_multiquestion(question)[question['id']]
        }
    }


def _complement_values(question, values):
    if question['type'] == 'boolean':
        options = [True, False]
    elif question['type'] in ['radios', 'checkboxes']:
        options = [
            option.get('value', option['label'])
            for option in question['options']
        ]
    else:
        raise ValueError('Followup questions are only supported for questions with options')

    return sorted(set(options) - set(values))


def _followup(question, root):
    schemas = []
    for followup_id, values in question['followup'].items():
        followup_q = root.get_question(followup_id)
        if question.type == 'checkboxes':
            should_not_have_followup = {
                "items": {"enum": _complement_values(question, values)}
            }
            should_have_followup = {
                "not": {"items": {"enum": _complement_values(question, values)}}
            }
        else:
            should_not_have_followup = {"enum": _complement_values(question, values)}
            should_have_followup = {"enum": values}

        schemas.append({
            'oneOf': [
                {
                    "properties": {
                        question['id']: should_not_have_followup,
                        followup_id: {"type": "null"}
                    },
                },
                {
                    "properties": {
                        question['id']: should_have_followup,
                    },
                    "required": question.required_form_fields + followup_q.required_form_fields
                },
            ]
        })

    return {'allOf': schemas}


def _flat_multiquestion(question):
    properties = {}
    for nested_question in question.questions:
        properties.update(build_question_properties(nested_question))

    schema_addition = {}
    for nested_question in question.questions:
        if nested_question.get('followup'):
            schema_addition = merge_schemas(
                schema_addition,
                _followup(nested_question, question)
            )

    return properties, schema_addition


def _nested_multiquestion(question):
    properties, schema_addition = _flat_multiquestion(question)

    object_schema = merge_schemas({
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": _nested_multiquestion_required(question),
    }, schema_addition)

    if not object_schema["required"]:
        object_schema.pop("required")

    return {question['id']: object_schema}


def _flat_multiquestion_required(question):
    if question.get('optional'):
        return []

    return _nested_multiquestion_required(question)


def _nested_multiquestion_required(question):
    """Returns a list of required nested properties for the multiquestion.

    `.required_form_fields` returns the top-level schema property name for the
    nested multiquestion, since that's the part that's influenced by the question's
    `optional` flag and it returns the key we need to add to the top-level schema's
    'required' list.

    Nested properties are always required if the nested question is mandatory, even
    when multiquestion itself is optional, since they're part of the nested schema.

    """
    required = []
    followups = []

    # Followup questions don't need to be in the 'required' properties list since even
    # non-optional questions don't always have to be present if they're a followup.
    # Both the question itself and the followups are covered by the oneOf subschemas.

    for nested_question in question['questions']:
        required.extend(nested_question.required_form_fields)
        if nested_question.get('followup'):
            followups.extend(nested_question['followup'].keys())

    return sorted(set(required) - set(followups))


QUESTION_TYPES = {
    'text': text_property,
    'upload': uri_property,
    'textbox_large': text_property,
    'checkboxes': checkbox_property,
    'radios': radios_property,
    'boolean': boolean_property,
    'list': list_property,
    'boolean_list': boolean_list_property,
    'pricing': pricing_property,
    'number': number_property,
    'multiquestion': multiquestion,
    'checkbox_tree': checkbox_tree_property,
    'date': date_property
}


def parse_question_limits(question, for_items=False):
    """
    Converts word and character length validators into JSON Schema-compatible maxLength and regex validators.
    """
    limits = {}
    word_length_validator = next(
        iter(filter(None, (
            re.match(r'under_(\d+)_words', validator['name'])
            for validator in question.get('validations', [])
        ))),
        None
    )
    char_length_validator = next(
        iter(filter(None, (
            re.search(r'([\d,]+)', validator['message'])
            for validator in question.get('validations', [])
            if validator['name'] == 'under_character_limit'
        ))),
        None
    )

    char_length = question.get('max_length') or (
        char_length_validator and char_length_validator.group(1).replace(',', '')
    )
    word_length = question.get('max_length_in_words') or (word_length_validator and word_length_validator.group(1))

    if char_length:
        limits['maxLength'] = int(char_length)

    if word_length:
        if not for_items and question.get('optional'):
            limits['pattern'] = r"^$|(^(?:\S+\s+){0,%s}\S+$)" % (int(word_length) - 1)
        else:
            limits['pattern'] = r"^(?:\S+\s+){0,%s}\S+$" % (int(word_length) - 1)

    return limits


def add_assurance(value_schema, assurance_approach):
    assurance_options = {
        '2answers-type1': [
            'Service provider assertion', 'Independent validation of assertion'
        ],
        '3answers-type1': [
            'Service provider assertion', 'Contractual commitment', 'Independent validation of assertion'
        ],
        '3answers-type2': [
            'Service provider assertion', 'Independent validation of assertion',
            'Independent testing of implementation'
        ],
        '3answers-type3': [
            'Service provider assertion', 'Independent testing of implementation', 'CESG-assured components'
        ],
        '3answers-type4': [
            'Service provider assertion', 'Independent validation of assertion',
            'Independent testing of implementation'
        ],
        '4answers-type1': [
            'Service provider assertion', 'Independent validation of assertion',
            'Independent testing of implementation', 'CESG-assured components'
        ],
        '4answers-type2': [
            'Service provider assertion', 'Contractual commitment',
            'Independent validation of assertion', 'CESG-assured components'
        ],
        '4answers-type3': [
            'Service provider assertion', 'Independent testing of implementation',
            'Assurance of service design', 'CESG-assured components'
        ],
        '5answers-type1': [
            'Service provider assertion', 'Contractual commitment', 'Independent validation of assertion',
            'Independent testing of implementation', 'CESG-assured components'
        ]
    }

    return {
        "type": "object",
        "properties": {
            "assurance": {
                "enum": assurance_options[assurance_approach]
            },
            "value": value_schema,
        },
        "required": [
            "value",
            "assurance"
        ]
    }


def build_question_properties(question):
    question_data = QUESTION_TYPES[question['type']](question)
    if question.get('assuranceApproach'):
        for key, value_schema in question_data.items():
            question_data[key] = add_assurance(value_schema, question['assuranceApproach'])
    return question_data


def build_any_of(any_of, fields):
    return {
        'required': [field for field in sorted(fields)],
        'title': any_of
    }


def build_schema_properties(schema, questions):
    for key, question in questions.items():
        property_schema = build_question_properties(question)
        if isinstance(property_schema, tuple):
            property_schema, schema_addition = property_schema
            schema['properties'].update(property_schema)
            schema = merge_schemas(schema, schema_addition)
        else:
            schema['properties'].update(property_schema)
            schema['required'].extend(question.required_form_fields)

    schema['required'].sort()

    return schema


def _multiquestion_anyof(questions):
    any_ofs = {}

    for key, question in questions.items():
        if question.get('any_of'):
            question_fields = []
            for q in question.questions:
                if q.get('fields'):
                    question_fields.extend(val for val in q.get('fields').values())
                else:
                    question_fields.append(q.id)
            any_ofs[question.id] = build_any_of(question.get('any_of'), question_fields)

    return {"anyOf": [any_ofs[key] for key in sorted(any_ofs.keys())]} if any_ofs else {}


def _multiquestion_dependencies(questions):
    dependencies = {}
    for key, question in questions.items():
        if question.type == 'multiquestion' and question.get('any_of'):
            dependencies.update({
                field: sorted(set(question.form_fields) - set([field]))
                for field in question.form_fields
                if len(question.form_fields) > 1
            })

    return {'dependencies': dependencies} if dependencies else {}


def generate_schema(schema_type, schema_name, framework_slug, lot_slug):
    questions = load_questions(schema_type, framework_slug, lot_slug)
    drop_non_schema_questions(questions)
    schema = empty_schema(schema_name)

    schema = build_schema_properties(schema, questions)
    schema = merge_schemas(schema, _multiquestion_anyof(questions))
    schema = merge_schemas(schema, _multiquestion_dependencies(questions))

    return schema


def generate_schema_todir(dir_path, schema_type, schema_name, framework_slug, lot_slug):
    schema = generate_schema(schema_type, schema_name, framework_slug, lot_slug)

    with open(os.path.join(dir_path, '{}-{}-{}.json'.format(schema_type, framework_slug, lot_slug)), 'w') as f:
        json.dump(schema, f, sort_keys=True, indent=2, separators=(',', ': '))
        f.write(os.linesep)
