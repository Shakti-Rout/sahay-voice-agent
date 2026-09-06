"""
Operator Triage Dashboard REST Endpoints.
Provides live session statistics, pending emergency escalations, and operator triage actions.
"""

import logging
from fastapi import APIRouter
from ...database.supabase_client import SupabaseManager
from ...websocket.dashboard_ws import broadcaster

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Returns aggregated triage statistics for the supervisor dashboard."""
    db = SupabaseManager.get_instance()
    active_sessions = db.get_active_sessions()
    escalations = db.get_recent_escalations()

    # Compute risk breakdowns
    risk_counts = {"CRITICAL": 0, "HIGH": 0, "MODERATE": 0, "LOW": 0}
    for item in db.in_memory_assessments:
        lvl = item.get("risk_level", "LOW")
        if lvl in risk_counts:
            risk_counts[lvl] += 1

    return {
        "active_calls": len([s for s in active_sessions if s.get("status") in ["initiated", "in_progress"]]),
        "total_calls_today": len(active_sessions),
        "pending_escalations": len([e for e in escalations if e.get("status") == "pending"]),
        "risk_breakdown": risk_counts,
        "active_operators": len(broadcaster.active_connections),
        "official_helpline": "NHAA 14566",
        "emergency_bridge": "112 / 108"
    }


@router.get("/dashboard/escalations")
async def get_pending_escalations():
    """Returns active escalations requiring human intervention."""
    db = SupabaseManager.get_instance()
    return db.get_recent_escalations()


@router.get("/dashboard/sessions")
async def get_recent_sessions():
    """Returns recent call sessions."""
    db = SupabaseManager.get_instance()
    return db.get_active_sessions()


@router.post("/dashboard/escalations/{call_id}/acknowledge")
async def acknowledge_escalation(call_id: str, operator_id: str = "OP-14566-CORE"):
    """Operator acknowledges taking over the escalated call."""
    db = SupabaseManager.get_instance()
    for esc in db.in_memory_escalations:
        if esc.get("external_call_id") == call_id:
            esc["status"] = "acknowledged"
            esc["assigned_operator"] = operator_id

    await broadcaster.broadcast("escalation_acknowledged", {
        "call_id": call_id,
        "operator_id": operator_id
    })

    return {"status": "success", "call_id": call_id, "operator_id": operator_id}
