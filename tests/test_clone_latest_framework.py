from script_helpers.clone_helpers import get_fw_name_from_slug, get_nbsp_fw_name_from_slug


def test_get_fw_name_from_slug():
    assert get_fw_name_from_slug('g-cloud-11') == 'G-Cloud 11'
    assert get_fw_name_from_slug('digital-outcomes-and-specialists-4') == 'Digital Outcomes and Specialists 4'


def test_get_nbsp_fw_name_from_slug():
    assert get_nbsp_fw_name_from_slug('g-cloud-11') == 'G-Cloud&nbsp;11'
    assert get_nbsp_fw_name_from_slug('digital-outcomes-and-specialists-4') == 'Digital Outcomes and Specialists&nbsp;4'

