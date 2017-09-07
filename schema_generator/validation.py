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
    'brief-cancel': {
        'question_set': 'briefs',
        'manifest': 'cancel_brief'
    },
}


SCHEMAS = {
    'services': [
        ('G-Cloud 7 SCS Service', 'g-cloud-7', 'scs'),
        ('G-Cloud 7 IaaS Service', 'g-cloud-7', 'iaas'),
        ('G-Cloud 7 PaaS Service', 'g-cloud-7', 'paas'),
        ('G-Cloud 7 SaaS Service', 'g-cloud-7', 'saas'),
        ('Digital Outcomes and Specialists Digital outcomes Service',
         'digital-outcomes-and-specialists', 'digital-outcomes'),
        ('Digital Outcomes and Specialists Digital specialists Service',
         'digital-outcomes-and-specialists', 'digital-specialists'),
        ('Digital Outcomes and Specialists User research studios Service',
         'digital-outcomes-and-specialists', 'user-research-studios'),
        ('Digital Outcomes and Specialists User research participants Service',
         'digital-outcomes-and-specialists', 'user-research-participants'),
        ('G-Cloud 8 SCS Service', 'g-cloud-8', 'scs'),
        ('G-Cloud 8 IaaS Service', 'g-cloud-8', 'iaas'),
        ('G-Cloud 8 PaaS Service', 'g-cloud-8', 'paas'),
        ('G-Cloud 8 SaaS Service', 'g-cloud-8', 'saas'),
        ('Digital Outcomes and Specialists 2 Digital outcomes Service',
         'digital-outcomes-and-specialists-2', 'digital-outcomes'),
        ('Digital Outcomes and Specialists 2 Digital specialists Service',
         'digital-outcomes-and-specialists-2', 'digital-specialists'),
        ('Digital Outcomes and Specialists 2 User research studios Service',
         'digital-outcomes-and-specialists-2', 'user-research-studios'),
        ('Digital Outcomes and Specialists 2 User research participants Service',
         'digital-outcomes-and-specialists-2', 'user-research-participants'),
        ('G-Cloud 9 Cloud Hosting Product', 'g-cloud-9', 'cloud-hosting'),
        ('G-Cloud 9 Cloud Software Product', 'g-cloud-9', 'cloud-software'),
        ('G-Cloud 9 Cloud Support Product', 'g-cloud-9', 'cloud-support'),
    ],
    'briefs': [
        ('Digital Outcomes and Specialists Digital outcomes Brief',
         'digital-outcomes-and-specialists', 'digital-outcomes'),
        ('Digital Outcomes and Specialists Digital specialists Brief',
         'digital-outcomes-and-specialists', 'digital-specialists'),
        ('Digital Outcomes and Specialists User research participants Brief',
         'digital-outcomes-and-specialists', 'user-research-participants'),
        ('Digital Outcomes and Specialists 2 Digital outcomes Brief',
         'digital-outcomes-and-specialists-2', 'digital-outcomes'),
        ('Digital Outcomes and Specialists 2 Digital specialists Brief',
         'digital-outcomes-and-specialists-2', 'digital-specialists'),
        ('Digital Outcomes and Specialists 2 User research participants Brief',
         'digital-outcomes-and-specialists-2', 'user-research-participants')
    ],
    'brief-responses': [
        ('Digital Outcomes and Specialists Digital outcomes Brief Response',
         'digital-outcomes-and-specialists', 'digital-outcomes'),
        ('Digital Outcomes and Specialists Digital specialists Brief Response',
         'digital-outcomes-and-specialists', 'digital-specialists'),
        ('Digital Outcomes and Specialists User research participants Brief Response',
         'digital-outcomes-and-specialists', 'user-research-participants'),
        ('Digital Outcomes and Specialists 2 Digital outcomes Brief Response',
         'digital-outcomes-and-specialists-2', 'digital-outcomes'),
        ('Digital Outcomes and Specialists 2 Digital specialists Brief Response',
         'digital-outcomes-and-specialists-2', 'digital-specialists'),
        ('Digital Outcomes and Specialists 2 User research participants Brief Response',
         'digital-outcomes-and-specialists-2', 'user-research-participants')
    ],
    'brief-awards': [
        ('Digital Outcomes and Specialists Digital outcomes Brief Award',
         'digital-outcomes-and-specialists', 'digital-outcomes'),
        ('Digital Outcomes and Specialists Digital specialists Brief Award',
         'digital-outcomes-and-specialists', 'digital-specialists'),
        ('Digital Outcomes and Specialists User research participants Brief Award',
         'digital-outcomes-and-specialists', 'user-research-participants'),
        ('Digital Outcomes and Specialists 2 Digital outcomes Brief Award',
         'digital-outcomes-and-specialists-2', 'digital-outcomes'),
        ('Digital Outcomes and Specialists 2 Digital specialists Brief Award',
         'digital-outcomes-and-specialists-2', 'digital-specialists'),
        ('Digital Outcomes and Specialists 2 User research participants Brief Award',
         'digital-outcomes-and-specialists-2', 'user-research-participants'),
    ],
    'brief-cancel': [
        ('Digital Outcomes and Specialists Digital outcomes Brief Cancel',
         'digital-outcomes-and-specialists', 'digital-outcomes'),
        ('Digital Outcomes and Specialists Digital specialists Brief Cancel',
         'digital-outcomes-and-specialists', 'digital-specialists'),
        ('Digital Outcomes and Specialists User research participants Brief Cancel',
         'digital-outcomes-and-specialists', 'user-research-participants'),
        ('Digital Outcomes and Specialists 2 Digital outcomes Brief Cancel',
         'digital-outcomes-and-specialists-2', 'digital-outcomes'),
        ('Digital Outcomes and Specialists 2 Digital specialists Brief Cancel',
         'digital-outcomes-and-specialists-2', 'digital-specialists'),
        ('Digital Outcomes and Specialists 2 User research participants Brief Cancel',
         'digital-outcomes-and-specialists-2', 'user-research-participants'),
    ]
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
        "$schema": "http://json-schema.org/schema#",
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


def price_string(optional):
    pattern = r"^\d{1,15}(?:\.\d{1,5})?$"
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
            'price' in question.get('optional_fields', [])
        )
    if 'minimum_price' in question.fields:
        pricing[question.fields['minimum_price']] = price_string(
            'minimum_price' in question.get('optional_fields', [])
        )
    if 'maximum_price' in question.fields:
        pricing[question.fields['maximum_price']] = price_string(
            'maximum_price' in question.get('optional_fields', [])
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
    return {question['id']: {
        "exclusiveMaximum": not limits.get('integer_only'),
        "maximum": limits['max_value'] if limits.get('max_value') is not None else 100,
        "minimum": limits.get('min_value') or 0,
        "type": "integer" if limits.get('integer_only') else "number"
    }}


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
            re.match('under_(\d+)_words', validator['name'])
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

    char_length = question.get('max_length') or (char_length_validator and
                                                 char_length_validator.group(1).replace(',', ''))
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
