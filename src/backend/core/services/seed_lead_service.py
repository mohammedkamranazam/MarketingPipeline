"""
Acceptance Criteria:
- normalize_row(row_input) -> SeedLeadRowNormalized strips and title-cases first_name,
  title-cases last_name and company when present, strips source and notes.
- normalize_row returns validation_errors containing 'first_name is required'
  when first_name is blank after stripping.
- normalize_row returns validation_errors containing 'company is required'
  when company is blank after stripping.
- is_duplicate defaults to False; deduplication is determined at batch level by callers.
- detect_duplicates(rows) -> list[bool] marks rows as duplicate when a later row has
  the same normalized (first_name, company) pair as a prior row in the same list.
- All returned values are plain Python types; no ORM objects returned.
"""

from core.contracts.seed_lead import SeedLeadRowInput, SeedLeadRowNormalized


def normalize_row(row_input: SeedLeadRowInput) -> SeedLeadRowNormalized:
    errors: list[str] = []

    first_name = (row_input.first_name or "").strip().title()
    if not first_name:
        errors.append("first_name is required")

    last_name = (row_input.last_name or "").strip().title() or None
    company = (row_input.company or "").strip().title() or None
    if not company:
        errors.append("company is required")

    source = (row_input.source or "").strip() or None

    return SeedLeadRowNormalized(
        first_name=first_name,
        last_name=last_name,
        company=company,
        source=source,
        validation_errors=errors,
        is_duplicate=False,
    )


def detect_duplicates(rows: list[SeedLeadRowNormalized]) -> list[bool]:
    seen: set[tuple[str, str | None]] = set()
    result: list[bool] = []
    for row in rows:
        key = (row.first_name.lower(), (row.company or "").lower())
        if key in seen:
            result.append(True)
        else:
            seen.add(key)
            result.append(False)
    return result
