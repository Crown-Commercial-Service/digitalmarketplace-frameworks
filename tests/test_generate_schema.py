import re
from math import isnan
import os

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

import mock
import pytest
from dmcontent.content_loader import ContentQuestion
from hypothesis.settings import Settings
from hypothesis import given, assume, strategies as st
from schema_generator import text_property, uri_property, parse_question_limits, \
    checkbox_property, number_property, multiquestion, \
    build_question_properties, empty_schema, load_questions, \
    drop_non_schema_questions, radios_property, list_property, boolean_list_property, \
    price_string, pricing_property, generate_schema, SCHEMAS

Settings.default.database = None


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
        keys=st.sampled_from(['label', 'value']),
        values=st.text(),
    ).filter(lambda c: 'label' in c)


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


@given(st.integers())
def test_parse_question_limits_word_count(num):
    assume(num > 0)
    assume(not isnan(num))
    assume(num < 65535)

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


@given(st.integers())
def test_parse_question_limits_word_count_optional(num):
    assume(num > 0)
    assume(not isnan(num))
    assume(num < 65535)

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


@given(st.integers())
def test_parse_question_limits_char_count(num):
    assume(num > 0)
    assume(not isnan(num))

    question = {"validations": [
        {
            "name": "under_character_limit",
            "message": str(num)
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


@given(st.text())
def test_boolean_list_property(id):
    question = {
        'id': id,
        'optional': True
    }
    result = boolean_list_property(question)
    assert id in result.keys()
    assert result[id]['minItems'] == 0


def test_price_string():
    price_string_validator = re.compile(price_string(False)['pattern'])
    valid_prices = [
        '0',
        '0.0',
        '1',
        '1.0',
        '150',
        '150.0',
        '12345678901234',
        '12345678901234.12345'
    ]
    for price in valid_prices:
        m = re.search(price_string_validator, price)
        assert m is not None


def test_price_string_empty():
    price_string_validator = re.compile(price_string(True)['pattern'])
    m = re.search(price_string_validator, '')
    assert m is not None


def test_pricing_property_minmax_price():
    manifest = {
        "id": "Test",
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
        "exclusiveMaximum": True,
        "maximum": 100,
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
        "exclusiveMaximum": False if integer_only else True,
        "maximum": max_value,
        "minimum": min_value,
        "type": "integer" if integer_only else "number"
    }}
    assert actual == expected


def test_multiquestion():
    question = {}
    question['questions'] = []
    question['questions'].append({
        'id': 'subquestion1',
        'name': 'Subquestion 1',
        'question': 'This is subquestion 1',
        'type': 'boolean'
    })
    question['questions'].append({
        'id': 'subquestion2',
        'name': 'Subquestion 2',
        'question': 'This is subquestion 2',
        'type': 'text'
    })
    result = multiquestion(question)
    assert 'subquestion1' in result.keys()
    assert 'subquestion2' in result.keys()

    # check that the multiquestion function gets called by
    # build_question_properties based on the value of type,
    # and throws an error if it isn't.
    with pytest.raises(KeyError):
        build_question_properties(question)

    question['type'] = 'multiquestion'
    bqp_result = build_question_properties(question)
    assert result == bqp_result


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
        generate_schema(test_directory, 'services', *schema)
    g_cloud_path = "./frameworks/g-cloud-7"
    g_cloud_opened_files = set(x for x in opened_files
                               if x.startswith(g_cloud_path) and
                               os.path.isfile(x))
    g_cloud_expected_files = set([x for x in recursive_file_list(g_cloud_path)
                                  if ("questions/services" in x or
                                      x.endswith("manifests/edit_submission.yml")) and
                                  not x.endswith("lot.yml") and not x.endswith("id.yml")])
    assert g_cloud_expected_files == g_cloud_opened_files


def test_generate_dos_schema_opens_files(opened_files, tmpdir):
    dos_schemas = [x for x in SCHEMAS['services'] if x[1] == "digital-outcomes-and-specialists"]
    test_directory = str(tmpdir.mkdir("schemas"))

    for schema in dos_schemas:
        generate_schema(test_directory, 'services', *schema)
    dos_path = "./frameworks/digital-outcomes-and-specialists"
    dos_opened_files = set(x for x in opened_files
                           if x.startswith(dos_path) and os.path.isfile(x))
    dos_expected_files = set([x for x in recursive_file_list(dos_path)
                              if ("questions/services" in x or
                                  x.endswith("manifests/edit_submission.yml")) and
                              not x.endswith("lot.yml")])
    assert dos_expected_files == dos_opened_files


def test_generate_dos_brief_opens_files(opened_files, tmpdir):
    dos_schemas = [x for x in SCHEMAS['briefs'] if x[1] == "digital-outcomes-and-specialists"]
    test_directory = str(tmpdir.mkdir("briefs"))

    for schema in dos_schemas:
        generate_schema(test_directory, 'briefs', *schema)
    dos_path = "./frameworks/digital-outcomes-and-specialists"
    dos_opened_files = set(x for x in opened_files
                           if x.startswith(dos_path) and os.path.isfile(x))
    dos_expected_files = set([x for x in recursive_file_list(dos_path)
                              if ("questions/briefs" in x or
                                  x.endswith("manifests/edit_brief.yml")) and
                              not x.endswith("lot.yml")])
    assert dos_expected_files == dos_opened_files
