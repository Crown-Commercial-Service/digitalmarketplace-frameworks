from itertools import chain
import os.path
import json

# if we need more powerful merging strategies, we can switch to the jsonmerge package, but this is fine for now
# and more straightforward
from deepmerge import always_merger

from dmcontent import ContentLoader


_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _enum_for_question(question):
    return {"enum": question["assessment"]["passIfIn"]}


def generate_schema(framework_slug, question_set, manifest_name):
    loader = ContentLoader(_base_dir)
    loader.load_manifest(
        framework_slug,
        question_set,
        manifest_name,
    )
    manifest = loader.get_manifest(
        framework_slug,
        manifest_name,
    )

    try:
        with open(os.path.join(
            _base_dir,
            "frameworks",
            framework_slug,
            "assessment",
            manifest_name,
            "extra.schema.json",
        ), "r") as f:
            extra_schema = json.load(f)
    except FileNotFoundError:
        extra_schema = {}

    assessed_questions = []
    for question in chain.from_iterable(section.questions for section in manifest.sections):
        if question.type == 'multiquestion':
            for nested_question in question.questions:
                if "passIfIn" in nested_question.get("assessment", {}):
                    assessed_questions.append(nested_question)
        elif "passIfIn" in question.get("assessment", {}):
            assessed_questions.append(question)

    discretionary_questions = tuple(q for q in assessed_questions if q["assessment"].get("discretionary"))
    baseline_questions = tuple(q for q in assessed_questions if not q["assessment"].get("discretionary"))

    # we add all assessed_questions as "required" by default, not because it's the assessment schema's job to
    # enforce that requirement, but it's a stronger guarantee we keep the content, the tests for this function
    # and the custom validation in the supplier frontend in agreement with each other.

    generated_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",  # hardcoded to draft 7 because jsonschema > 3 supports it
        "title": "{} Declaration Assessment Schema (Definite Pass Schema)".format(framework_slug),
        "type": "object",
        "allOf": [
            {"$ref": "#/definitions/baseline"},
            {"properties": {q.id: _enum_for_question(q) for q in discretionary_questions}},
        ],
        "required": sorted(q.id for q in discretionary_questions if q["assessment"].get("required", True)),
        "definitions": {
            "baseline": {
                "$schema": "http://json-schema.org/draft-04/schema#",
                "title": "{} Declaration Assessment Schema (Baseline Schema)".format(framework_slug),
                "type": "object",
                "allOf": [
                    {"properties": {q.id: _enum_for_question(q) for q in baseline_questions}},
                ],
                "required": sorted(q.id for q in baseline_questions if q["assessment"].get("required", True)),
            },
        },
    }

    return always_merger.merge(generated_schema, extra_schema)
