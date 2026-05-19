"""
Tests for ICP extraction contracts.

Acceptance criteria tested:
- ICPSignal validates confidence in [0.0, 1.0].
- ICPSignal requires non-empty content and evidence_text.
- ICPExtractionRequest requires non-empty chunk_texts.
- ICPExtractionResult groups signals under document/pipeline/client IDs.
- EventEnvelope validates event_type, idempotency_key, and client_id.
"""

import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from core.contracts.icp import ICPExtractionRequest, ICPExtractionResult, ICPSignal
from core.contracts.run import EventEnvelope


def test_icp_signal_valid():
    sig = ICPSignal(
        item_type="icp_signal",
        content="Target companies have 50+ engineers",
        evidence_text="Our customers typically employ over 50 engineers",
        confidence=0.85,
    )
    assert sig.confidence == 0.85


def test_icp_signal_confidence_out_of_range():
    with pytest.raises(ValidationError):
        ICPSignal(
            content="x", evidence_text="y", confidence=1.5
        )


def test_icp_signal_empty_content_invalid():
    with pytest.raises(ValidationError):
        ICPSignal(content="", evidence_text="evidence", confidence=0.5)


def test_icp_signal_empty_evidence_invalid():
    with pytest.raises(ValidationError):
        ICPSignal(content="content", evidence_text="", confidence=0.5)


def test_icp_extraction_request_empty_chunks_raises():
    with pytest.raises(ValidationError, match="chunk_texts must not be empty"):
        ICPExtractionRequest(
            document_id=uuid.uuid4(),
            pipeline_id=uuid.uuid4(),
            client_id=uuid.uuid4(),
            chunk_texts=[],
        )


def test_icp_extraction_result_groups_signals():
    doc_id = uuid.uuid4()
    pipe_id = uuid.uuid4()
    cid = uuid.uuid4()
    sig = ICPSignal(content="text", evidence_text="source", confidence=0.7)
    result = ICPExtractionResult(
        document_id=doc_id,
        pipeline_id=pipe_id,
        client_id=cid,
        signals=[sig],
    )
    assert len(result.signals) == 1
    assert result.document_id == doc_id


def test_event_envelope_valid():
    env = EventEnvelope(
        event_type="document.uploaded",
        client_id=uuid.uuid4(),
        pipeline_id=uuid.uuid4(),
        idempotency_key="doc:abc123",
        occurred_at=datetime.now(UTC),
        producer="api",
    )
    assert env.event_version == "1.0"
    assert env.payload == {}
