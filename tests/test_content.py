import glob

import mock
import pytest

from dmcontent import ContentLoader
from dmcontent.utils import TemplateField

content = ContentLoader('./')

MANIFEST_QUESTION_SET = {
    "display_brief": "briefs",
    "edit_brief": "briefs",

    "display_brief_response": "brief-responses",
    "edit_brief_response": "brief-responses",
    "output_brief_response": "brief-responses",

    "clarification_question": "clarification_question",

    "declaration": "declaration",

    "display_service": "services",
    "edit_service": "services",
    "edit_service_as_admin": "services",
    "edit_submission": "services",
    "search_filters": "services",
}

QUESTION_SET_CONTEXT = {
    'briefs': {'lot': 'context-lot'},
    'brief-responses': {'lot': 'context-lot', 'brief': mock.Mock()},
    'services': {'lot': 'context-lot'},
}


def get_manifests():
    paths = glob.glob('frameworks/*/manifests/*.yml')
    for path in paths:
        _, framework, _, manifest = path.split('/')
        manifest = manifest.replace('.yml', '')

        yield (framework, MANIFEST_QUESTION_SET[manifest], manifest)


def content_questions():
    for manifest in get_manifests():
        content.load_manifest(*manifest)

    for framework_questions in content._questions.values():
        for question_set, questions in framework_questions.items():
            for question in questions.values():
                yield question_set, question['id'], question


def content_sections():
    for manifest in get_manifests():
        content.load_manifest(*manifest)

    for framework_manifests in content._content.values():
        for manifest, sections in framework_manifests.items():
            for section in sections:
                yield manifest, section['slug'], section


@pytest.mark.parametrize("manifest, section_slug, section", content_sections())
def test_render_section(manifest, section_slug, section):
    for field in section.values():
        if isinstance(field, TemplateField):
            assert field.render(QUESTION_SET_CONTEXT.get(MANIFEST_QUESTION_SET[manifest])) is not None


@pytest.mark.parametrize("question_set, question_id, question", content_questions())
def test_render_question(question_id, question_set, question):
    question_set_context = {
        'briefs': {'lot': 'context-lot'},
        'brief-responses': {'lot': 'context-lot', 'brief': mock.Mock()},
        'services': {'lot': 'context-lot'},
    }
    for field in question.values():
        if isinstance(field, TemplateField):
            assert field.render(question_set_context.get(question_set)) is not None
