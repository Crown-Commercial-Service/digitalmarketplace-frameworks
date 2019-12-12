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

# TODO: add test coverage for file copying/replacement :)
