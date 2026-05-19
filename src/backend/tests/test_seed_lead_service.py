"""
Tests for seed_lead_service (normalize_row, detect_duplicates).

Acceptance criteria tested:
- normalize_row strips and title-cases first_name.
- normalize_row returns error when first_name is blank.
- normalize_row returns error when company is blank.
- normalize_row title-cases last_name and company when present.
- normalize_row strips source; None when blank.
- detect_duplicates marks later rows with same (first_name, company) as duplicate.
- detect_duplicates is case-insensitive for key comparison.
- First occurrence of a key is not a duplicate.
"""

from core.contracts.seed_lead import SeedLeadRowInput, SeedLeadRowNormalized
from core.services.seed_lead_service import detect_duplicates, normalize_row


def _input(**kwargs) -> SeedLeadRowInput:
    return SeedLeadRowInput(**{"first_name": "Alice", **kwargs})


def test_normalize_strips_and_title_cases_first_name():
    norm = normalize_row(_input(first_name="  alice  "))
    assert norm.first_name == "Alice"


def test_normalize_blank_first_name_error():
    norm = normalize_row(_input(first_name="   "))
    assert "first_name is required" in norm.validation_errors


def test_normalize_blank_company_error():
    norm = normalize_row(_input(company=""))
    assert "company is required" in norm.validation_errors


def test_normalize_title_cases_company():
    norm = normalize_row(_input(company="acme corp"))
    assert norm.company == "Acme Corp"


def test_normalize_title_cases_last_name():
    norm = normalize_row(_input(last_name="smith", company="Acme"))
    assert norm.last_name == "Smith"


def test_normalize_none_last_name_stays_none():
    norm = normalize_row(_input(company="Acme", last_name=None))
    assert norm.last_name is None


def test_normalize_source_stripped():
    norm = normalize_row(_input(company="Acme", source="  LinkedIn  "))
    assert norm.source == "LinkedIn"


def test_normalize_blank_source_becomes_none():
    norm = normalize_row(_input(company="Acme", source="  "))
    assert norm.source is None


def test_normalize_is_duplicate_defaults_false():
    norm = normalize_row(_input(company="Acme"))
    assert norm.is_duplicate is False


def test_normalize_no_errors_on_valid_input():
    norm = normalize_row(SeedLeadRowInput(first_name="Alice", company="Acme"))
    assert norm.validation_errors == []


def test_detect_duplicates_first_occurrence_not_duplicate():
    rows = [
        SeedLeadRowNormalized(
            first_name="Alice", last_name=None, company="Acme",
            source=None, validation_errors=[], is_duplicate=False,
        )
    ]
    flags = detect_duplicates(rows)
    assert flags == [False]


def test_detect_duplicates_second_same_key_is_duplicate():
    row = SeedLeadRowNormalized(
        first_name="Alice", last_name=None, company="Acme",
        source=None, validation_errors=[], is_duplicate=False,
    )
    flags = detect_duplicates([row, row])
    assert flags == [False, True]


def test_detect_duplicates_case_insensitive():
    r1 = SeedLeadRowNormalized(
        first_name="Alice", last_name=None, company="Acme",
        source=None, validation_errors=[], is_duplicate=False,
    )
    r2 = SeedLeadRowNormalized(
        first_name="alice", last_name=None, company="acme",
        source=None, validation_errors=[], is_duplicate=False,
    )
    flags = detect_duplicates([r1, r2])
    assert flags == [False, True]


def test_detect_duplicates_different_companies_not_duplicate():
    r1 = SeedLeadRowNormalized(
        first_name="Alice", last_name=None, company="Acme",
        source=None, validation_errors=[], is_duplicate=False,
    )
    r2 = SeedLeadRowNormalized(
        first_name="Alice", last_name=None, company="Beta",
        source=None, validation_errors=[], is_duplicate=False,
    )
    flags = detect_duplicates([r1, r2])
    assert flags == [False, False]
