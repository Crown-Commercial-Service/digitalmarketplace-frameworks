import builtins
import mock
import pytest

from script_helpers.clone_helpers import get_fw_name_from_slug, get_nbsp_fw_name_from_slug, FrameworkContentCloner


def test_get_fw_name_from_slug():
    assert get_fw_name_from_slug('g-cloud-11') == 'G-Cloud 11'
    assert get_fw_name_from_slug('digital-outcomes-and-specialists-4') == 'Digital Outcomes and Specialists 4'


def test_get_nbsp_fw_name_from_slug():
    assert get_nbsp_fw_name_from_slug('g-cloud-11') == 'G-Cloud&nbsp;11'
    assert get_nbsp_fw_name_from_slug('digital-outcomes-and-specialists-4') == 'Digital Outcomes and Specialists&nbsp;4'


def test_framework_content_cloner_init():
    cloner = FrameworkContentCloner('g-cloud', 12, 2020)
    assert cloner._launch_year == 2020
    assert cloner._new_fw_slug == 'g-cloud-12'
    assert cloner._previous_fw_slug == 'g-cloud-11'
    assert cloner._following_fw_slug == 'g-cloud-13'

    assert cloner._previous_name == 'G-Cloud 11'
    assert cloner._new_name == 'G-Cloud 12'
    assert cloner._previous_nbsp_name == 'G-Cloud&nbsp;11'
    assert cloner._escaped_previous_nbsp_name == 'G&#x2011;Cloud&nbsp;11'
    assert cloner._new_nbsp_name == 'G-Cloud&nbsp;12'


def test_framework_content_cloner_init_for_second_iteration():
    cloner = FrameworkContentCloner('digital-outcomes-and-specialists', 2, 2017)
    assert cloner._previous_fw_slug == 'digital-outcomes-and-specialists'


def test_framework_content_cloner_init_fails_for_first_iteration():
    with pytest.raises(ValueError) as exc:
        FrameworkContentCloner('digital-outcomes-and-specialists', 1, 2016)
    assert str(exc.value) == "Can't clone a framework on its first iteration"


def test_replace_urls_with_placeholders():
    cloner = FrameworkContentCloner('g-cloud', 12, 2020)
    mock_file_contents = """
        my_url: "https://gov.uk/path/to/g-cloud-11.pdf"
        my_url2: "https://gov.uk/path/to/another/g-cloud-11.pdf"
    """

    with mock.patch.object(builtins, 'open', mock.mock_open(read_data=mock_file_contents)) as mock_open:
        cloner.set_placeholders_for_file_urls()
        assert mock_open.call_args_list == [
            mock.call('frameworks/g-cloud-12/messages/urls.yml'),
            mock.call('frameworks/g-cloud-12/messages/urls.yml', 'w')
        ]
        # What yaml.dump() does under the hood...
        assert mock_open().write.call_args_list == [
            mock.call('my_url'),
            mock.call(':'),
            mock.call(' '),
            mock.call("https://gov.uk/path/to/g-cloud-11.pdf/__placeholder__"),
            mock.call('\n'),
            mock.call('my_url2'),
            mock.call(':'),
            mock.call(' '),
            mock.call("https://gov.uk/path/to/another/g-cloud-11.pdf/__placeholder__"),
            mock.call('\n')
        ]

# TODO: add more test coverage for file copying/replacement :)
