import re
from math import isnan
import os

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

import mock
import pytest
from dmcontent import ContentQuestion
from hypothesis import settings, given, assume, HealthCheck, strategies as st
from schema_generator.validation import (
    SCHEMAS,
    boolean_list_property,
    boolean_property,
    checkbox_property,
    checkbox_tree_property,
    drop_non_schema_questions,
    empty_schema,
    generate_schema_todir,
    list_property,
    load_questions,
    multiquestion,
    number_property,
    parse_question_limits,
    price_string,
    pricing_property,
    radios_property,
    text_property,
    uri_property,
)


@pytest.fixture()
def opened_files(request):
    opened_files = []
    original_open = builtins.open

    def patched_open(*args):
        fh = original_open(*args)
        opened_files.append(fh.name)
        return fh

    open_patch = mock.patch.object(builtins, 'open', patched_open)
    open_patch.start()
    request.addfinalizer(open_patch.stop)

    return opened_files


def recursive_file_list(dirname):
    output = []
    for filename in os.listdir(dirname):
        filename = dirname + "/" + filename
        if os.path.isfile(filename):
            output.append(filename)
        else:
            for result in recursive_file_list(filename):
                output.append(result)
    return output


def radios():
    return checkboxes()


def checkboxes():
    return st.dictionaries(
        keys=st.sampled_from(['label', 'value', 'description']),
        values=st.text(),
    ).filter(lambda c: 'label' in c)


@st.composite
def nested_checkboxes(draw, options_list_strategy=None,
                      optional_keys=st.lists(st.sampled_from(['value', 'description']))):
    option = {
        'label': st.text()
    }
    for k in draw(optional_keys):
        option[k] = st.text()

    if options_list_strategy is not None:
        option['options'] = options_list_strategy

    return draw(st.fixed_dictionaries(option))


def nested_checkboxes_list():
    def create_options_with_children(list_strategy):
        return st.lists(nested_checkboxes(options_list_strategy=list_strategy), max_size=25)

    return st.recursive(
        st.lists(nested_checkboxes()),
        create_options_with_children,
        max_leaves=10
    )


def test_drop_non_schema_questions():
    questions = load_questions('services', 'g-cloud-7', 'scs')
    # lotName is in G-Cloud 7
    assert 'lotName' in questions.keys()
    drop_non_schema_questions(questions)
    assert 'lotName' not in questions.keys()


def test_empty_schema():
    result = empty_schema("Test")
    assert type(result) == dict
    assert "Test" in result['title']
    for k in ["title", "$schema", "type", "properties", "required"]:
        assert k in result.keys()


@given(st.text())
def test_text_property(id_name):
    result = text_property({"id": id_name})
    assert result == {id_name: {"type": "string", "minLength": 1}}


@given(st.text(), st.booleans())
def test_optional_text_property(id_name, optional):
    result = text_property({"id": id_name, "optional": optional})
    assert result == {id_name: {"type": "string", "minLength": 0 if optional else 1}}


@given(st.text())
def test_text_property_format(id_name):
    result = text_property({"id": id_name, "limits": {"format": "email"}})
    assert result == {id_name: {"type": "string", "format": "email", "minLength": 1}}


@given(st.text())
def test_uri_property(id_name):
    result = uri_property({"id": id_name})
    assert result == {id_name: {
        "type": "string",
        "format": "uri"}}


@given(st.integers(min_value=1, max_value=65534))
def test_parse_question_limits_word_count(num):
    assume(not isnan(num))

    question = {"validations": [
        {
            "name": "under_{0}_words".format(num)
        }
    ]}
    result = parse_question_limits(question)
    assert 'pattern' in result.keys()
    expected = '^(?:\\S+\\s+){0,' + str(num - 1) + '}\\S+$'
    assert result['pattern'] == expected
    matcher = re.compile(result['pattern'])

    # Now test the regex works!
    range_list = range(num)
    generated_str = ' '.join(['a' for x in range_list])
    m = re.search(matcher, generated_str)
    assert m is not None

    # now with one that's too long
    generated_str += ' a a a a'
    m = re.search(matcher, generated_str)
    assert m is None


@given(st.integers(min_value=1, max_value=65534))
def test_parse_question_limits_word_count_optional(num):
    assume(not isnan(num))

    question = {
        "validations": [
            {
                "name": "under_{0}_words".format(num)
            }
        ],
        "optional": True
    }
    result = parse_question_limits(question)
    assert 'pattern' in result.keys()
    assert result['pattern'].startswith("^$")

    # test empty condition
    matcher = re.compile(result['pattern'])
    m = re.search(matcher, "")
    assert m is not None


@given(st.integers(min_value=1))
def test_parse_question_limits_char_count(num):
    assume(not isnan(num))

    question = {"validations": [
        {
            "name": "under_character_limit",
            "message": "The answer must be no more than {:,} characters.".format(num)
        }
    ]}
    result = parse_question_limits(question)
    assert 'maxLength' in result.keys()
    assert result['maxLength'] == num


@given(st.text(), st.lists(checkboxes()))
def test_checkbox_property(id, options):
    assume(len(id) > 0)

    question = {
        "id": id,
        "options": options
    }
    result = checkbox_property(question)
    assert result[id]['minItems'] == 1

    question['optional'] = True
    result = checkbox_property(question)
    assert result[id]['minItems'] == 0

    enum = result[id]['items']['enum']
    assert len(enum) == len(options)
    assert all(option['value'] in enum
               for option in options if 'value' in option)
    assert all(option['label'] in enum
               for option in options if 'value' not in option)


@settings(suppress_health_check=[HealthCheck.too_slow])
@given(st.text(), nested_checkboxes_list(), st.integers(min_value=1))
def test_checkbox_tree_property(id, options, number_of_items):
    assume(len(id) > 0)

    question = {
        "id": id,
        "options": options,
        "number_of_items": number_of_items
    }
    result = checkbox_tree_property(question)
    assert result[id]['minItems'] == 1

    question['optional'] = True
    result = checkbox_tree_property(question)
    assert result[id]['minItems'] == 0
    assert result[id]['maxItems'] == number_of_items

    enum = result[id]['items']['enum']

    def recursive_check(opts):
        for option in opts:
            if 'options' in option:
                recursive_check(option['options'])
            else:
                if 'value' in option:
                    assert option['value'] in enum
                else:
                    assert option['label'] in enum

    recursive_check(options)


@given(st.text(), st.lists(radios()))
def test_radios_property(id, options):
    question = {"id": id, "options": options}
    result = radios_property(question)
    assert type(result) == dict
    assert id in result.keys()
    enum = result[id]['enum']
    assert len(enum) == len(options)
    assert all(option['value'] in enum
               for option in options if 'value' in option)
    assert all(option['label'] in enum
               for option in options if 'value' not in option)


@given(st.text())
def test_list_property(id):
    question = {
        'id': id,
        'optional': True
    }
    result = list_property(question)
    assert id in result.keys()
    assert result[id]['minItems'] == 0
    assert result[id]['items'] == {
        'type': 'string',
        'maxLength': 100,
        "pattern": "^(?:\\S+\\s+){0,9}\\S+$"
    }


def test_boolean_property():
    question = {
        'id': "Test",
    }
    result = boolean_property(question)
    assert result["Test"]["type"] == "boolean"
    assert "enum" not in result["Test"]


@given(st.booleans())
def test_boolean_property_with_required_value(boolean):
    question = {
        'id': "Test",
        'required_value': boolean
    }
    result = boolean_property(question)
    assert result["Test"]["enum"] == [boolean]
    assert "type" not in result["Test"]


@given(st.text())
def test_boolean_list_property(id):
    question = {
        'id': id,
        'optional': True
    }
    result = boolean_list_property(question)
    assert id in result.keys()
    assert result[id]['minItems'] == 0


@pytest.mark.parametrize("price", [
    '0',
    '0.0',
    '1',
    '1.0',
    '150',
    '150.0',
    '12345678901234',
    '12345678901234.12345'
])
def test_price_string_finds_valid_prices(price):
    price_string_validator = re.compile(price_string(False)['pattern'])
    assert re.search(price_string_validator, price) is not None


@pytest.mark.parametrize("price", [
    '0.79',
    '1',
    '150',
    '150.00',
    '219.28',
    '12345678901234',
])
def test_price_string_with_decimal_restriction_finds_valid_prices(price):
    price_string_validator = re.compile(price_string(False, True)['pattern'])
    assert re.search(price_string_validator, price) is not None


@pytest.mark.parametrize("price", [
    '0',
    '0.00',
    '150.1',
    '150.000',
    '150.00875',
])
def test_price_string_with_decimal_restriction_does_not_find_invalid_prices(price):
    price_string_validator = re.compile(price_string(False, True)['pattern'])
    assert re.search(price_string_validator, price) is None


def test_price_string_empty():
    price_string_validator = re.compile(price_string(True)['pattern'])
    m = re.search(price_string_validator, '')
    assert m is not None


def test_pricing_property_minmax_price():
    manifest = {
        "id": "Test",
        "type": "pricing",
        "fields": {
            "minimum_price": "priceMin",
            "maximum_price": "priceMax"
        }
    }
    cq = ContentQuestion(manifest)
    result = pricing_property(cq)
    assert not result['priceMin']['pattern'].startswith("^$|")
    assert not result['priceMax']['pattern'].startswith("^$|")


def test_pricing_property_minmax_price_optional():
    manifest = {
        "id": "Test",
        "type": "pricing",
        "fields": {
            "minimum_price": "priceMin",
            "maximum_price": "priceMax"
        },
        "optional_fields": [
            "minimum_price",
            "maximum_price"
        ]
    }
    cq = ContentQuestion(manifest)
    result = pricing_property(cq)
    assert result['priceMin']['pattern'].startswith("^$|")
    assert result['priceMax']['pattern'].startswith("^$|")


def test_pricing_property_price_unit_and_interval():
    manifest = {
        "id": "Test",
        "type": "pricing",
        "fields": {
            "price_unit": "priceUnit",
            "price_interval": "priceInterval"
        }
    }
    cq = ContentQuestion(manifest)
    result = pricing_property(cq)
    assert type(result['priceInterval']['enum']) == list
    assert type(result['priceUnit']['enum']) == list


def test_pricing_property_price_unit_and_interval_optional():
    manifest = {
        "id": "Test",
        "type": "pricing",
        "fields": {
            "price_unit": "priceUnit",
            "price_interval": "priceInterval"
        },
        "optional_fields": [
            "price_unit",
            "price_interval"
        ]
    }
    cq = ContentQuestion(manifest)
    result = pricing_property(cq)
    assert "" in result['priceUnit']['enum']
    assert "" in result['priceInterval']['enum']


def test_hours_for_price():
    manifest = {
        "id": "Test",
        "type": "pricing",
        "fields": {
            "hours_for_price": "pfh"
        }
    }
    cq = ContentQuestion(manifest)
    result = pricing_property(cq)
    assert "enum" in result['pfh'].keys()


@given(st.text())
def test_number_property(id):
    actual = number_property({'id': id, 'type': 'number'})
    expected = {id: {
        "exclusiveMaximum": 100,
        "minimum": 0,
        "type": "number"
    }}
    assert actual == expected


@given(st.integers(), st.integers(), st.booleans())
def test_number_property_limits(max_value, min_value, integer_only):
    actual = number_property({'id': 'number-question', 'type': 'number', 'limits': {
        'max_value': max_value, 'min_value': min_value, 'integer_only': integer_only
    }})
    expected = {"number-question": {
        "minimum": min_value,
        "type": "integer" if integer_only else "number"
    }}
    expected['number-question'].update({"maximum": max_value} if integer_only else {"exclusiveMaximum": max_value})
    assert actual == expected


def test_multiquestion():
    question = ContentQuestion({
        "type": "multiquestion",
        "questions": [
            {
                'id': 'subquestion1',
                'name': 'Subquestion 1',
                'question': 'This is subquestion 1',
                'type': 'boolean'
            },
            {
                'id': 'subquestion2',
                'name': 'Subquestion 2',
                'question': 'This is subquestion 2',
                'type': 'text'
            }
        ]
    })

    result, schema_addition = multiquestion(question)
    assert 'subquestion1' in result.keys()
    assert 'subquestion2' in result.keys()

    assert schema_addition == {'required': ['subquestion1', 'subquestion2']}


def test_followup():
    question = ContentQuestion({
        "id": "multiq",
        "type": "multiquestion",
        "questions": [
            {
                'id': 'subquestion1',
                'name': 'Subquestion 1',
                'question': 'This is subquestion 1',
                'type': 'boolean',
                'followup': {
                    'subquestion2': [True]
                }
            },
            {
                'id': 'subquestion2',
                'name': 'Subquestion 2',
                'question': 'This is subquestion 2',
                'type': 'text'
            }
        ]
    })

    result, schema_addition = multiquestion(question)
    assert 'subquestion1' in result.keys()
    assert 'subquestion2' in result.keys()

    assert schema_addition == {
        'allOf': [
            {'oneOf': [
                {'properties': {
                    'subquestion1': {'enum': [False]},
                    'subquestion2': {'type': 'null'}
                }},
                {
                    'properties': {'subquestion1': {'enum': [True]}},
                    'required': ['subquestion1', 'subquestion2']
                }
            ]}
        ],
        'required': ['subquestion1']
    }


def test_checkboxes_followup():
    question = ContentQuestion({
        "id": "multiq",
        "type": "multiquestion",
        "questions": [
            {
                'id': 'subquestion1',
                'name': 'Subquestion 1',
                'question': 'This is subquestion 1',
                'type': 'checkboxes',
                'options': [{'label': 'AA', 'value': 'a'}, {'label': 'BB', 'value': 'b'}],
                'followup': {
                    'subquestion2': ['a']
                }
            },
            {
                'id': 'subquestion2',
                'name': 'Subquestion 2',
                'optional': True,
                'question': 'This is subquestion 2',
                'type': 'text'
            }
        ]
    })

    result, schema_addition = multiquestion(question)
    assert 'subquestion1' in result.keys()
    assert 'subquestion2' in result.keys()

    assert schema_addition == {
        'allOf': [
            {'oneOf': [
                {'properties': {
                    'subquestion1': {'items': {'enum': ['b']}},
                    'subquestion2': {'type': 'null'}
                }},
                {
                    'properties': {'subquestion1': {'not': {'items': {'enum': ['b']}}}},
                    'required': ['subquestion1']
                }
            ]}
        ],
        'required': ['subquestion1']
    }


def test_generate_g_cloud_schema_opens_files(opened_files, tmpdir):
    """
    This test checks that when building a schema, all files are
    actually opened.

    The assumption is that if there are files which aren't opened,
    either they are unnecessary or something has gone profoundly wrong.
    """
    g_cloud_schemas = [x for x in SCHEMAS['services'] if x[1] == "g-cloud-7"]
    test_directory = str(tmpdir.mkdir("schemas"))

    for schema in g_cloud_schemas:
        generate_schema_todir(test_directory, 'services', *schema)
    g_cloud_path = "./frameworks/g-cloud-7"
    g_cloud_opened_files = set(
        x for x in opened_files if x.startswith(g_cloud_path) and os.path.isfile(x)
    )
    g_cloud_expected_files = set(
        [
            x for x in recursive_file_list(g_cloud_path)
            if ("questions/services" in x or x.endswith("manifests/edit_submission.yml"))
            and not x.endswith("lot.yml")
            and not x.endswith("id.yml")
        ]
    )
    assert g_cloud_expected_files == g_cloud_opened_files


def test_generate_dos_schema_opens_files(opened_files, tmpdir):
    dos_schemas = [x for x in SCHEMAS['services'] if x[1] == "digital-outcomes-and-specialists"]
    test_directory = str(tmpdir.mkdir("schemas"))

    for schema in dos_schemas:
        generate_schema_todir(test_directory, 'services', *schema)
    dos_path = "./frameworks/digital-outcomes-and-specialists"
    dos_opened_files = set(x for x in opened_files
                           if x.startswith(dos_path) and os.path.isfile(x))
    dos_expected_files = set(
        [
            x for x in recursive_file_list(dos_path)
            if ("questions/services" in x or x.endswith("manifests/edit_submission.yml"))
            and not x.endswith("lot.yml")
        ]
    )
    assert dos_expected_files == dos_opened_files


def test_generate_dos_brief_opens_files(opened_files, tmpdir):
    dos_schemas = [x for x in SCHEMAS['briefs'] if x[1] == "digital-outcomes-and-specialists"]
    test_directory = str(tmpdir.mkdir("briefs"))

    for schema in dos_schemas:
        generate_schema_todir(test_directory, 'briefs', *schema)
        generate_schema_todir(test_directory, 'brief-awards', *schema)
    dos_path = "./frameworks/digital-outcomes-and-specialists"
    dos_opened_files = set(x for x in opened_files if x.startswith(dos_path) and os.path.isfile(x))
    dos_expected_files = set([
        x for x in recursive_file_list(dos_path)
        if (
            "questions/briefs" in x
            or x.endswith("manifests/edit_brief.yml")
            or x.endswith("manifests/award_brief.yml")
        )
        and not x.endswith("lot.yml")
    ])

    assert dos_expected_files == dos_opened_files
