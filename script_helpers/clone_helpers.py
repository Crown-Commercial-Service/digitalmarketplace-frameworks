import os
import sys
import shutil
import yaml


METADATA_FILES = {
    'copy_services': 'copy_services.yml',
    'following_framework': 'following_framework.yml',
    'bad_words': 'service_questions_to_scan_for_bad_words.yml'
}

DATES_FILES = {
    'application_deadline': 'messages/homepage-sidebar.yml',
    'clarification_deadline': 'questions/declaration/readUnderstoodGuidance.yml',
    'go_live': 'questions/declaration/canProvideFromDayOne.yml'
}

FILE_PLACEHOLDER_FILES = {
    'urls': 'messages/urls.yml'
}


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


class FrameworkContentCloner:

    def __init__(self, framework_family, iteration_number, launch_year, *, question_copy_method=None):
        self._launch_year = launch_year
        self._question_copy_method = question_copy_method if question_copy_method else 'exclude'
        self._new_fw_slug = f"{framework_family}-{iteration_number}"
        if iteration_number == 2:
            # Handle first iterations without numeric suffix (e.g. DOS 2 -> DOS)
            self._previous_fw_slug = f"{framework_family}"
        elif iteration_number < 2:
            raise ValueError("Can't clone a framework on its first iteration")
        else:
            self._previous_fw_slug = f"{framework_family}-{iteration_number - 1}"
        self._following_fw_slug = f"{framework_family}-{iteration_number + 1}"

        self._previous_name = get_fw_name_from_slug(self._previous_fw_slug)
        self._new_name = get_fw_name_from_slug(self._new_fw_slug)
        self._previous_nbsp_name = get_nbsp_fw_name_from_slug(self._previous_fw_slug)
        # Hack for G-Cloud (or should we say, 'G&#x2011;Cloud')
        self._escaped_previous_nbsp_name = get_nbsp_fw_name_from_slug(self._previous_fw_slug).replace("-", "&#x2011;")
        self._new_nbsp_name = get_nbsp_fw_name_from_slug(self._new_fw_slug)

    def copy_fw_folder(self):
        previous_fw_folder = os.path.join("frameworks", self._previous_fw_slug)
        if not os.path.exists(previous_fw_folder):
            sys.exit(f"No previous framework for iteration {self._previous_fw_slug}")

        print(f"Copying all files from {self._previous_fw_slug} to {self._new_fw_slug}")
        try:
            shutil.copytree(previous_fw_folder, os.path.join("frameworks", self._new_fw_slug))
        except FileExistsError:
            print("Skipping - folder already exists")

    def _replace_framework_in_content(self, current_content, root, filename):
        updated_content = None
        if self._previous_name in current_content:
            updated_content = current_content.replace(self._previous_name, self._new_name)
            print(f"Replacing framework name in {root}/{filename}")
            # Keep the changes for the next replacement
            current_content = updated_content
        if self._previous_nbsp_name in current_content:
            updated_content = current_content.replace(self._previous_nbsp_name, self._new_nbsp_name)
            print(f"Replacing framework name (with nbsp) in {root}/{filename}")
            # Keep the changes for the next replacement
            current_content = updated_content
        if self._escaped_previous_nbsp_name in current_content:
            # Hack for G-Cloud which has additional (unnecessary) escaping in some files
            updated_content = current_content.replace(self._escaped_previous_nbsp_name, self._new_nbsp_name)
            print(f"Replacing escaped framework name (with nbsp) in {root}/{filename}")
            # Keep the changes for the next replacement
            current_content = updated_content
        if self._previous_fw_slug in current_content:
            updated_content = current_content.replace(self._previous_fw_slug, self._new_fw_slug)
            print(f"Replacing framework slug in {root}/{filename}")

        # If we return updated_content = None, we know that no changes have been made
        return updated_content

    def replace_hardcoded_framework_name_and_slug(self):
        new_fw_root = os.path.join('frameworks', self._new_fw_slug)
        for root, dirs, files in os.walk(new_fw_root, topdown=True):
            if 'metadata' in root:
                # Metadata is updated separately
                continue
            for filename in files:
                with open(os.path.join(root, filename), 'r') as f:
                    current_content = f.read()
                    updated_content = self._replace_framework_in_content(current_content, root, filename)
                # Only write if there's been a change
                if updated_content:
                    with open(os.path.join(root, filename), 'w') as f:
                        f.write(updated_content)

    def update_copy_services_metadata(self):
        print("Setting copy_services metadata")
        # Set copy_services.yml content
        copy_services_file = os.path.join(
            "frameworks", self._new_fw_slug, 'metadata', METADATA_FILES['copy_services']
        )
        question_copy_method = f'questions_to_{self._question_copy_method}'

        with open(copy_services_file) as f:
            content = yaml.safe_load(f)

            # G-Cloud 12 and earlier only have (deprecated) `questions_to_copy` available
            # Don't re-use existing 'questions_to_copy' if it doesn't match the new method
            if question_copy_method not in content:
                new_content = {
                    'source_framework': self._previous_fw_slug,
                    question_copy_method: []
                }
            else:
                new_content = {
                    'source_framework': self._previous_fw_slug,
                    question_copy_method: content[question_copy_method]
                }

        with open(copy_services_file, 'w') as f:
            print(f"Writing content to {copy_services_file}")
            yaml.dump(new_content, f)

    def update_following_framework_metadata(self):
        print("Setting following_framework metadata")
        # Set following_framework.yml content
        following_fw_file = os.path.join(
            "frameworks", self._new_fw_slug, 'metadata', METADATA_FILES['following_framework']
        )
        with open(following_fw_file) as f:
            content = yaml.safe_load(f)
            new_content = {
                'framework': {
                    'slug': self._following_fw_slug,
                    'name': get_fw_name_from_slug(self._following_fw_slug),
                    'coming': str(int(content['framework']['coming']) + 1)
                }
            }
        with open(following_fw_file, 'w') as f:
            print(f"Writing content to {following_fw_file}")
            yaml.dump(new_content, f)

    def update_dates(self):
        print("Setting important dates to 2525")
        for key, file_path in DATES_FILES.items():
            full_file_path = os.path.join("frameworks", self._new_fw_slug, file_path)

            with open(full_file_path, 'r') as f:
                current_content = f.read()
                updated_content = current_content.replace(str(self._launch_year - 1), '2525')

            with open(full_file_path, 'w') as f:
                print(f"Writing content to {file_path}")
                f.write(updated_content)

    def set_placeholders_for_file_urls(self):
        print("Setting placeholder urls for as-yet unpublished files")
        file_placeholder_file = os.path.join(
            "frameworks", self._new_fw_slug, FILE_PLACEHOLDER_FILES['urls']
        )
        with open(file_placeholder_file) as f:
            content = yaml.safe_load(f)
            new_content = {
                key: "{}/__placeholder__".format(value)
                for key, value in content.items()
            }

        with open(file_placeholder_file, 'w') as f:
            print(f"Writing content to {file_placeholder_file}")
            yaml.dump(new_content, f)

    def clone(self):
        self.copy_fw_folder()
        self.replace_hardcoded_framework_name_and_slug()
        self.update_copy_services_metadata()
        self.update_following_framework_metadata()
        self.update_dates()
        self.set_placeholders_for_file_urls()
