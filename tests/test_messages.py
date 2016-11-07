import glob

import pytest

from dmcontent import ContentLoader
from dmcontent.utils import TemplateField

content = ContentLoader('./')


MESSAGE_CONTEXT = {
    'contract_variation_1': {'supplier_name': "Supplier 1"}
}


def get_messages():
    paths = glob.glob('frameworks/*/messages/*.yml')
    for path in paths:
        _, framework, _, message = path.split('/')
        message = message.replace('.yml', '')

        yield (framework, message)


def content_messages():
    for framework, message in get_messages():
        content.load_messages(framework, [message])

    for framework_messages in content._messages.values():
        for message, message_content in framework_messages.items():
            yield message, message_content


@pytest.mark.parametrize("message_name, message", content_messages())
def test_render_message(message_name, message):
    for field in message.values():
        assert render(field, MESSAGE_CONTEXT.get(message_name)) is not None


def render(field, context):
    if isinstance(field, TemplateField):
        return field.render(context)
    elif isinstance(field, dict):
        return {key: render(value, context) for key, value in field.items()}
    elif isinstance(field, list):
        return [render(i, context) for i in field]
    else:
        return field
