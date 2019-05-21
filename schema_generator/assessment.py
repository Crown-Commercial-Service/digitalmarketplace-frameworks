from itertools import chain

from dmcontent import ContentLoader


def _enum_for_question(question):
    return {"enum": question["assessment"]["passIfIn"]}


def generate_schema(framework_slug, question_set, manifest_name):
    loader = ContentLoader("./")
    loader.load_manifest(
        framework_slug,
        question_set,
        manifest_name,
    )
    manifest = loader.get_manifest(
        framework_slug,
        manifest_name,
    )

    assessed_questions = []
    for question in chain.from_iterable(section.questions for section in manifest.sections):
        if question.type == 'multiquestion':
            for nested_question in question.questions:
                if "passIfIn" in nested_question.get("assessment", {}):
                    assessed_questions.append(nested_question)
        elif "passIfIn" in question.get("assessment", {}):
            assessed_questions.append(question)

    discretionary_properties = {
        question.id: _enum_for_question(question)
        for question in assessed_questions if question["assessment"].get("discretionary")
    }
    baseline_properties = {
        question.id: _enum_for_question(question)
        for question in assessed_questions if not question["assessment"].get("discretionary")
    }

    return {
        "$schema": "http://json-schema.org/draft-07/schema#",  # hardcoded to draft 7 because jsonschema > 3 supports it
        "title": "{} Declaration Assessment Schema (Definite Pass Schema)".format(framework_slug),
        "type": "object",
        "allOf": [
            {"$ref": "#/definitions/baseline"},
            {"properties": discretionary_properties},
        ],
        "definitions": {
            "baseline": {
                "$schema": "http://json-schema.org/draft-04/schema#",
                "title": "{} Declaration Assessment Schema (Baseline Schema)".format(framework_slug),
                "type": "object",
                "properties": baseline_properties,
            },
        },
    }
