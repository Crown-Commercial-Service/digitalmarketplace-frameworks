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

    assessed_questions = tuple(
        question
        for question in chain.from_iterable(section.questions for section in manifest.sections)
        if "passIfIn" in question.get("assessment", {})
    )

    discretionary_properties = {
        question.id: _enum_for_question(question)
        for question in assessed_questions if question["assessment"].get("discretionary")
    }
    baseline_properties = {
        question.id: _enum_for_question(question)
        for question in assessed_questions if not question["assessment"].get("discretionary")
    }

    return {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "allOf": [
            {"$ref": "#/definitions/baseline"},
            {"properties": discretionary_properties},
        ],
        "definitions": {
            "baseline": {
                "$schema": "http://json-schema.org/draft-04/schema#",
                "type": "object",
                "properties": baseline_properties,
            },
        },
    }
