
def get_fw_name_from_slug(fw_slug):
    # Hack for G-Cloud which helpfully contains a dash
    # Hack for Digital Outcomes and Specialists which contains a lower-case 'and'
    return fw_slug.replace('-', ' ').replace('g cloud', 'G-Cloud').title().replace('And', 'and')


def get_nbsp_fw_name_from_slug(fw_slug):
    # Some places use G-Cloud&bsp;11 for non-breaking spaces
    # Get the last space and 'replace' it
    name = get_fw_name_from_slug(fw_slug)
    last_space_position = name.rindex(" ")
    return name[:last_space_position] + "&nbsp;" + name[(last_space_position + 1):]
