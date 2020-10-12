import yaml
from functools import lru_cache
from pathlib import Path

import pytest


@lru_cache(maxsize=None)  # memoize this function as it is slow
def get_framework_names_ids_fields(framework):
    names_ids_fields = set()

    for p in Path("frameworks", framework, "questions", "services").iterdir():
        if p.name.startswith("multiq"):
            continue
        contents = yaml.safe_load(p.read_text())
        if "id" in contents:
            names_ids_fields.add(contents["id"])
        if "fields" in contents:
            names_ids_fields.update(contents["fields"].values())
        names_ids_fields.add(p.name[:-4])

    return names_ids_fields


class TestCopyServices:
    frameworks_with_copy_services = {
        copy_services_file.parts[1]: yaml.safe_load(copy_services_file.read_text())
        for copy_services_file in Path("frameworks").glob(
            "*/metadata/copy_services.yml"
        )
    }

    @pytest.fixture(params=frameworks_with_copy_services.keys())
    def framework(self, request):
        return request.param

    @pytest.fixture
    def copy_services(self, framework):
        return self.frameworks_with_copy_services[framework]

    def test_source_framework_exists(self, copy_services):
        assert Path("frameworks", copy_services["source_framework"]).is_dir()

    def test_keys_exist_in_source_framework(self, copy_services):
        names_ids_fields = get_framework_names_ids_fields(
            copy_services["source_framework"]
        )

        if "questions_to_exclude" in copy_services:
            assert set(copy_services["questions_to_exclude"]).issubset(names_ids_fields)

        if "questions_to_copy" in copy_services:
            assert set(copy_services["questions_to_copy"]).issubset(names_ids_fields)


class TestServiceQuestionsToScanForBadWords:

    frameworks_with_service_questions_to_scan_for_bad_words = {
        p.parts[1]: yaml.safe_load(p.read_text())
        for p in Path("frameworks").glob(
            "*/metadata/service_questions_to_scan_for_bad_words.yml"
        )
    }

    @pytest.fixture(
        params=frameworks_with_service_questions_to_scan_for_bad_words.keys()
    )
    def framework(self, request):
        return request.param

    @pytest.fixture
    def service_questions_to_scan_for_bad_words(self, framework):
        return self.frameworks_with_service_questions_to_scan_for_bad_words[framework]

    def test_keys_in_framework(
        self, framework, service_questions_to_scan_for_bad_words
    ):
        names_ids_fields = get_framework_names_ids_fields(framework)

        assert set(
            service_questions_to_scan_for_bad_words["service_questions"]
        ).issubset(names_ids_fields)
