import builtins
import mock
import pytest

from script_helpers.clone_helpers import get_fw_name_from_slug, get_nbsp_fw_name_from_slug, FrameworkContentCloner


class TestFrameworkCloningHelpers:

    def test_get_fw_name_from_slug(self):
        assert get_fw_name_from_slug('g-cloud-11') == 'G-Cloud 11'
        assert get_fw_name_from_slug('digital-outcomes-and-specialists-4') == 'Digital Outcomes and Specialists 4'

    def test_get_nbsp_fw_name_from_slug(self):
        assert get_nbsp_fw_name_from_slug('g-cloud-11') == 'G-Cloud&nbsp;11'
        assert get_nbsp_fw_name_from_slug('digital-outcomes-and-specialists-4') == \
            'Digital Outcomes and Specialists&nbsp;4'


class TestFrameworkClonerInit:

    @pytest.mark.parametrize(
        'copy_method_kwarg, copy_method_expected',
        [
            ('copy', 'copy'),
            ('exclude', 'exclude'),
            (None, 'exclude')
        ]
    )
    def test_framework_content_cloner_init(self, copy_method_kwarg, copy_method_expected):
        cloner = FrameworkContentCloner('g-cloud', 12, 2020, question_copy_method=copy_method_kwarg)
        assert cloner._launch_year == 2020
        assert cloner._question_copy_method == copy_method_expected
        assert cloner._new_fw_slug == 'g-cloud-12'
        assert cloner._previous_fw_slug == 'g-cloud-11'
        assert cloner._following_fw_slug == 'g-cloud-13'

        assert cloner._previous_name == 'G-Cloud 11'
        assert cloner._new_name == 'G-Cloud 12'
        assert cloner._previous_nbsp_name == 'G-Cloud&nbsp;11'
        assert cloner._escaped_previous_nbsp_name == 'G&#x2011;Cloud&nbsp;11'
        assert cloner._new_nbsp_name == 'G-Cloud&nbsp;12'

    def test_framework_content_cloner_init_for_second_iteration(self):
        cloner = FrameworkContentCloner('digital-outcomes-and-specialists', 2, 2017)
        assert cloner._previous_fw_slug == 'digital-outcomes-and-specialists'

    def test_framework_content_cloner_init_fails_for_first_iteration(self):
        with pytest.raises(ValueError) as exc:
            FrameworkContentCloner('digital-outcomes-and-specialists', 1, 2016)
        assert str(exc.value) == "Can't clone a framework on its first iteration"


class TestReplaceUrls:

    def test_replace_urls_with_placeholders(self):
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


class TestUpdateCopyServicesMetadata:

    @pytest.mark.parametrize('copy_method', [None, 'exclude'])
    def test_update_copy_services_metadata_does_not_copy_if_mismatched_method(self, copy_method):
        cloner = FrameworkContentCloner('g-cloud', 13, 2020, question_copy_method=copy_method)
        mock_g12_copy_services_file = """
            questions_to_copy:
              - question1
              - question2
            source_framework: "g-cloud-11"
        """
        with mock.patch.object(builtins, 'open', mock.mock_open(read_data=mock_g12_copy_services_file)) as mock_open:
            cloner.update_copy_services_metadata()
            assert mock_open.call_args_list == [
                mock.call('frameworks/g-cloud-13/metadata/copy_services.yml'),
                mock.call('frameworks/g-cloud-13/metadata/copy_services.yml', 'w')
            ]
            # What yaml.dump() does under the hood...
            expected_yaml_dump_calls = [
                'questions_to_exclude', ':', ' [', ']', '\n',
                'source_framework', ':', ' ', 'g-cloud-12', '\n'
            ]
            assert mock_open().write.call_args_list == [mock.call(x) for x in expected_yaml_dump_calls]

    def test_update_copy_services_metadata_clones_questions_if_matching_method(self):
        cloner = FrameworkContentCloner('g-cloud', 13, 2020, question_copy_method='exclude')
        mock_g12_copy_services_file = """
            questions_to_exclude:
              - question1
              - question2
            source_framework: "g-cloud-11"
        """
        with mock.patch.object(builtins, 'open', mock.mock_open(read_data=mock_g12_copy_services_file)) as mock_open:
            cloner.update_copy_services_metadata()
            assert mock_open.call_args_list == [
                mock.call('frameworks/g-cloud-13/metadata/copy_services.yml'),
                mock.call('frameworks/g-cloud-13/metadata/copy_services.yml', 'w')
            ]
            # What yaml.dump() does under the hood...
            expected_yaml_dump_calls = [
                'questions_to_exclude', ':', '\n',
                '-', ' ', 'question1', '\n',
                '-', ' ', 'question2', '\n',
                'source_framework', ':', ' ', 'g-cloud-12', '\n'
            ]
            assert mock_open().write.call_args_list == [mock.call(x) for x in expected_yaml_dump_calls]

# TODO: add more test coverage for file copying/replacement :)
