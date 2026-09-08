import os
from fastapi.testclient import TestClient
from app.main import app
from app.trauma.prank_filter import PrankFilter
from app.database.supabase_client import SupabaseManager

client = TestClient(app)


def test_prank_filter_screening():
    # 1. Very short / silent call
    res_short = PrankFilter.evaluate(
        call_id="call_test_short",
        transcripts=["hello"],
        risk_score=0.1,
        duration_seconds=1.5
    )
    assert res_short.is_legitimate is False
    assert res_short.ticket_id is None
    assert "EMPTY_AUDIO" in res_short.reason or "PREMATURE_HANGUP" in res_short.reason

    # 2. Prank keyword call
    res_prank = PrankFilter.evaluate(
        call_id="call_test_prank",
        transcripts=["bhai ye prank call hai timepass kar raha hu haha"],
        risk_score=0.15,
        duration_seconds=12.0
    )
    assert res_prank.is_legitimate is False
    assert res_prank.ticket_id is None
    assert "PRANK" in res_prank.reason

    # 3. Legitimate distress call in Odia / Desia
    res_legit = PrankFilter.evaluate(
        call_id="call_test_legit",
        transcripts=["Mate maribaku godauchanti mu jungle re nuchi achhi sahajya kara"],
        risk_score=0.92,
        duration_seconds=18.0
    )
    assert res_legit.is_legitimate is True
    assert res_legit.ticket_id is not None
    assert res_legit.ticket_id.startswith("TKT-")


def test_public_complaints_endpoint_and_dpdp_deletion():
    db = SupabaseManager.get_instance()

    # Register a test complaint
    test_call_id = "call_dpdp_test_881"
    ticket_id = "TKT-TEST-881"
    complaint = db.register_complaint(
        call_id=test_call_id,
        ticket_id=ticket_id,
        summary="Test tribal grievance regarding water access denial.",
        risk_level="HIGH",
        language="des-IN"
    )
    assert complaint["ticket_ref"] == ticket_id

    # Create dummy wav file in recordings dir to test erasure
    rec_dir = os.path.join(os.path.dirname(__file__), "..", "..", "app", "static", "recordings")
    os.makedirs(rec_dir, exist_ok=True)
    test_wav = os.path.join(rec_dir, f"{test_call_id}.wav")
    with open(test_wav, "wb") as f:
        f.write(b"RIFFdummywavdata")
    assert os.path.exists(test_wav)

    # 1. Fetch public complaints (no auth required)
    get_res = client.get("/api/v1/complaints/recent")
    assert get_res.status_code == 200
    complaints = get_res.json().get("complaints", [])
    found = any(c.get("ticket_ref") == ticket_id for c in complaints)
    assert found is True

    # 2. DPDP Right to Erasure: Citizen deletes complaint
    del_res = client.delete(f"/api/v1/complaints/{ticket_id}")
    assert del_res.status_code == 200
    del_data = del_res.json()
    assert del_data["status"] == "success"
    assert "erased" in del_data["message"].lower()

    # 3. Verify physical file is erased from disk
    assert not os.path.exists(test_wav)

    # 4. Verify complaint is no longer returned in public listing
    get_res2 = client.get("/api/v1/complaints/recent")
    complaints2 = get_res2.json().get("complaints", [])
    found2 = any(c.get("ticket_ref") == ticket_id for c in complaints2)
    assert found2 is False
