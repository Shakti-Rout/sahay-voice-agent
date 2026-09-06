import pytest
from app.rag.retriever import VerifiedRAGRetriever


def test_rag_retrieves_poa_rights_for_threat():
    retriever = VerifiedRAGRetriever()
    query = "Se mate dhamaka deichhi mo ghara bhangideba"
    context = retriever.retrieve_context(query, risk_level="HIGH", language_code="or-IN")

    assert context != ""
    assert "POA-SEC-15A" in context or "14566" in context or "112" in context


def test_rag_retrieves_emergency_112_for_critical():
    retriever = VerifiedRAGRetriever()
    query = "Help lathi dhari attack karuchhanti urgent"
    context = retriever.retrieve_context(query, risk_level="CRITICAL", language_code="en-IN")

    assert "112" in context or "EMERGENCY" in context


def test_rag_retrieves_telemanas_for_counselling():
    retriever = VerifiedRAGRetriever()
    query = "I am having extreme panic and crying, anxiety"
    context = retriever.retrieve_context(query, risk_level="MODERATE", language_code="en-IN")

    assert "14416" in context or "TELE-MANAS" in context
