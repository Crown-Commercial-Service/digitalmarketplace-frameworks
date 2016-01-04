import re
from math import isnan
from glob import glob
import os
import shutil

import pytest
from dmutils.content_loader import ContentQuestion
from hypothesis.settings import Settings
from hypothesis import given, assume, strategies as st
from schema_generator import uri_property, parse_question_limits, \
    checkbox_property, percentage_property, multiquestion, \
    build_question_properties, empty_schema, load_questions, \
    drop_non_schema_questions, radios_property, list_property, price_string, \
    pricing_property, generate_schema, SCHEMAS
from . import support

Settings.default.database = None


def test_drop_non_schema_questions():
    questions = load_questions('g-cloud-7', 'scs')
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


@given(st.text(),
       st.lists(
           st.dictionaries(
               keys=st.just("label"),
               values=st.text(),
               min_size=1),
           min_size=1))
def test_checkbox_property(id, options):
    assume(len(id) > 0)
    assume(len(options) > 0)

    question = {
        "id": id,
        "options": options
    }
    result = checkbox_property(question)
    assert result[id]['minItems'] == 1

    question['optional'] = True
    result = checkbox_property(question)
    assert result[id]['minItems'] == 0
    assert len(result[id]['items']['enum']) == len(options)


@given(st.text(), st.lists(st.text()))
def test_radios_property(id, list_of_options):
    list_of_options = [{"label": x} for x in list_of_options]
    question = {"id": id, "options": list_of_options}
    result = radios_property(question)
    assert type(result) == dict
    assert id in result.keys()
    enum = result[id]['enum']
    assert len(enum) == len(list_of_options)


@given(st.text())
def test_list_property(id):
    question = {
        'id': id,
        'optional': True
    }
    result = list_property(question)
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
def test_percentage_property(id):
    actual = percentage_property({'id': id, 'type': 'percentage'})
    expected = {id: {
        "exclusiveMaximum": True,
        "maximum": 100,
        "minimum": 0,
        "type": "number"
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


def test_generate_schema_opens_files():
    """
    This test checks that when building a schema, all files are
    actually opened.

    The assumption is that if there are files which aren't opened,
    either they are unnecessary or something has gone profoundly wrong.
    """
    g_cloud_schemas = [x for x in SCHEMAS if x[1] == "g-cloud-7"]
    dos_schemas = [x for x in SCHEMAS
                   if x[1] == "digital-outcomes-and-specialists"]
    test_directory = os.path.join(os.getcwd(), "tests/build")

    # test G-Cloud 7 schemas
    support.clear_buffer()
    if not os.path.isdir(test_directory):
        os.mkdir(test_directory)
    for schema in g_cloud_schemas:
        generate_schema(test_directory, *schema)
    g_cloud_path = "./frameworks/g-cloud-7"
    g_cloud_opened_files = set([x for x in support.opened_files
                                if x.startswith(g_cloud_path) and
                                os.path.isfile(x)])
    g_cloud_expected_files = set([y for x in os.walk(g_cloud_path)
                                  for y in glob(g_cloud_path)
                                  if os.path.isfile(y)])
    g_cloud_diff = g_cloud_expected_files - g_cloud_opened_files
    assert len(g_cloud_diff) == 0
    shutil.rmtree(test_directory)

    # test DOS
    support.clear_buffer()
    if not os.path.isdir(test_directory):
        os.mkdir(test_directory)
    for schema in dos_schemas:
        generate_schema(test_directory, *schema)
    dos_path = "./frameworks/digital-outcomes-and-specialists"
    dos_opened_files = set([x for x in support.opened_files
                            if x.startswith(dos_path) and os.path.isfile(x)])
    dos_expected_files = set([y for x in os.walk(dos_path)
                              for y in glob(dos_path) if os.path.isfile(y)])
    dos_diff = dos_expected_files - dos_opened_files
    assert len(dos_diff) == 0
    shutil.rmtree(test_directory)
    support.clear_buffer()
