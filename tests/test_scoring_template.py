
from pathlib import Path

import ezodf
import yaml

import pytest


def dos_framework_brief_max_number_of_requirements():
    briefs_questions_folders = Path(".").glob("frameworks/digital-outcomes-and-specialists*/questions/briefs")
    paths = (
        {
            "essentialRequirements": folder.glob("essentialRequirements*.yml"),
            "niceToHaveRequirements": folder.glob("niceToHaveRequirements*.yml"),
            "culturalFitCriteria": folder.glob("culturalFitCriteria*.yml"),
        }
        for folder in briefs_questions_folders
    )

    def get_number_of_items(path):
        with open(path) as file:
            question = yaml.load(file)
            return question["number_of_items"]

    number_of_items_per_framework = (
        {key: max(get_number_of_items(p) for p in paths) for key, paths in framework.items()}
        for framework in paths
    )
    return number_of_items_per_framework


@pytest.fixture(params=dos_framework_brief_max_number_of_requirements())
def number_of_items(request):
    return request.param


@pytest.fixture
def sheet():
    return ezodf.opendoc(Path("assets/digital-outcomes-specialists-scoring-template.ods")).sheets["Sheet1"]


def test_scoring_template_has_enough_rows_for_each_criterion(number_of_items, sheet):
    row, col = 8, 3
    assert sheet[row, col].value == "Essential skills and experience"
    assert sheet[row, col].span[0] >= number_of_items["essentialRequirements"]

    row += sheet[row, col].span[0]
    assert sheet[row, col].value == "Nice-to-have skills and experience"
    assert sheet[row, col].span[0] >= number_of_items["niceToHaveRequirements"]

    row += sheet[row, col].span[0]
    assert sheet[row, col].value == "Proposed solution"

    row += sheet[row, col].span[0]
    assert sheet[row, col].value == "Cultural fit criteria"
    assert sheet[row, col].span[0] >= number_of_items["culturalFitCriteria"]
