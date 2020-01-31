from contextlib import contextmanager

import jsonschema
import pytest

from schema_generator.assessment import generate_schema


# we define a basic, assessment-passing, g11 declaration here (though interestingly it doesn't include informational
# fields so it wouldn't actually pass the *validation* schema). this could be fleshed out to enable it to be used as a
# common "example" valid declaration from other apps: having it live here in this repository and regularly checked
# in these tests ensures that it is always up to date with what is defined in the framework's yaml files... future work
# to look at.


def _definite_pass_g11_declaration():
    return {
        # discretionary
        "GAAR": False,
        "bankrupt": False,
        "confidentialInformation": False,
        "conflictOfInterest": False,
        "distortedCompetition": False,
        "distortingCompetition": False,
        "environmentalSocialLabourLaw": False,
        "graveProfessionalMisconduct": False,
        "influencedContractingAuthority": False,
        "misleadingInformation": False,
        "modernSlaveryReportingRequirements": True,
        "seriousMisrepresentation": False,
        "significantOrPersistentDeficiencies": False,
        "taxEvasion": False,
        "unspentTaxConvictions": False,
        "witheldSupportingDocuments": False,

        # mandatory
        "10WorkingDays": True,
        "MI": True,
        "accurateInformation": True,
        "accuratelyDescribed": True,
        "canProvideFromDayOne": True,
        "conspiracy": False,
        "corruptionBribery": False,
        "dunsNumberCompanyRegistrationNumber": True,
        "employersInsurance": (
            u"Not applicable - your organisation does not need employer\u2019s liability insurance because your "
            u"organisation employs only the owner or close family members."
        ),
        "environmentallyFriendly": True,
        "equalityAndDiversity": True,
        "fraudAndTheft": False,
        "fullAccountability": True,
        "helpBuyersComplyTechnologyCodesOfPractice": True,
        "informationChanges": True,
        "modernSlaveryTurnover": True,
        "offerServicesYourselves": True,
        "organisedCrime": False,
        "proofOfClaims": True,
        "publishContracts": True,
        "readUnderstoodGuidance": True,
        "servicesDoNotInclude": True,
        "servicesHaveOrSupportCloudHostingCloudSoftware": "Yes",
        "servicesHaveOrSupportCloudSupport": "Yes",
        "termsAndConditions": True,
        "termsOfParticipation": True,
        "terrorism": False,
        "understandHowToAskQuestions": True,
        "understandTool": True,
        "unfairCompetition": True,
    }


def _definite_pass_g12_declaration():
    g11_decl = _definite_pass_g11_declaration()

    # g12 hasn't (yet?) diverged enough to require a change
    return g11_decl


@contextmanager
def _empty_context_manager():
    yield


_g11 = ("g-cloud-11", _definite_pass_g11_declaration)
_g12 = ("g-cloud-12", _definite_pass_g12_declaration)


@pytest.mark.parametrize("declaration_update,use_baseline,should_pass", (
    # a definite pass
    ({}, False, True,),
    ({}, True, True,),
    # pass with arbitrary other, hopefully ignored, fields
    ({"bullockbefriendingBard": "Bous Stephanoumenos"}, False, True,),
    ({"bullockbefriendingBard": "Bous Stephanoumenos"}, True, True,),
    # definite fails
    ({"readUnderstoodGuidance": False}, False, False,),
    ({"readUnderstoodGuidance": False}, True, False,),
    ({"employersInsurance": "Through metempsychosis"}, False, False,),
    ({"employersInsurance": "Through metempsychosis"}, True, False,),
    # discretionary
    ({"graveProfessionalMisconduct": True}, False, False,),
    ({"graveProfessionalMisconduct": True}, True, True,),
    # Multiquestion discretionary
    ({"modernSlaveryReportingRequirements": False}, True, True,),
    ({"modernSlaveryReportingRequirements": False}, False, False,),
))
def test_g11_declaration_assessment(declaration_update, use_baseline, should_pass):
    # these test(s) are a bit funny in that they all make the same call to the function-under-test and then
    # assert a different thing about the return value, so we could improve on run time if necessary by only performing
    # the call once if necessary...
    schema = generate_schema("g-cloud-11", "declaration", "declaration")
    if use_baseline:
        schema = schema["definitions"]["baseline"]

    candidate = _definite_pass_g11_declaration()
    candidate.update(declaration_update)

    with (_empty_context_manager() if should_pass else pytest.raises(jsonschema.ValidationError)):
        jsonschema.validate(candidate, schema)


@pytest.mark.parametrize('fw_slug,base_decl_factory', (_g11, _g12,))
@pytest.mark.parametrize('use_baseline', (False, True,))
def test_g11_declaration_assessment_passes_if_answer_missing(fw_slug, base_decl_factory, use_baseline):
    schema = generate_schema(fw_slug, "declaration", "declaration")
    if use_baseline:
        schema = schema["definitions"]["baseline"]

    candidate = base_decl_factory()
    candidate.pop('modernSlaveryReportingRequirements')
    candidate['modernSlaveryTurnover'] = False

    jsonschema.validate(candidate, schema)
