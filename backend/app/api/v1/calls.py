import logging
from fastapi import APIRouter, Request, HTTPException
from ...config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.api_route("/calls/webhook/exotel", methods=["GET", "POST"])
async def exotel_inbound_webhook(request: Request):
    """
    Exotel Inbound Call Webhook.
    Exotel queries this URL when a citizen dials the virtual helpline number.
    Returns instructions to bridge audio via AgentStream WebSocket.
    """
    data = {}
    if request.query_params:
        data.update(dict(request.query_params))

    content_type = request.headers.get("content-type", "").lower()
    if "application/json" in content_type:
        try:
            body = await request.json()
            if isinstance(body, dict):
                data.update(body)
        except Exception:
            pass
    elif "form" in content_type:
        try:
            form = await request.form()
            data.update(dict(form))
        except Exception:
            pass
    else:
        try:
            body = await request.json()
            if isinstance(body, dict):
                data.update(body)
        except Exception:
            try:
                form = await request.form()
                data.update(dict(form))
            except Exception:
                pass

    call_sid = data.get("CallSid") or data.get("call_sid") or data.get("CallSID") or "unknown_call"
    caller = data.get("From") or data.get("from") or data.get("Caller") or "unknown_caller"
    logger.info(f"[ExotelWebhook] Incoming call from {caller} (CallSid: {call_sid})")

    # Construct WebSocket connection URL for Exotel AgentStream
    forwarded_proto = request.headers.get("x-forwarded-proto", "").lower()
    is_secure = request.url.scheme == "https" or forwarded_proto == "https" or settings.ENVIRONMENT == "production"
    ws_scheme = "wss" if is_secure else "ws"
    ws_url = f"{ws_scheme}://{request.headers.get('host', 'localhost:8000')}/ws/exotel/{call_sid}"

    # Return Exotel voice response connecting to AgentStream
    response_payload = {
        "status": "success",
        "call_sid": call_sid,
        "action": "stream",
        "stream_url": ws_url,
        "sample_rate": 8000,
        "codec": "audio/x-mulaw"
    }

    return response_payload


@router.get("/calls/{call_id}")
async def get_call_session(call_id: str):
    """Retrieve session metadata for an active or completed call."""
    return {
        "call_id": call_id,
        "production_helpline": settings.PRODUCTION_HELPLINE_NUMBER,
        "status": "in_progress",
        "telephony_provider": settings.TELEPHONY_PROVIDER
    }


@router.post("/calls/{call_id}/escalate")
async def force_escalation(call_id: str, reason: str = "operator_manual_trigger"):
    """Force instant escalation to a human operator."""
    logger.warning(f"[Escalation] Manual operator escalation triggered for {call_id}: {reason}")
    return {
        "call_id": call_id,
        "escalated": True,
        "reason": reason,
        "assigned_operator": "Operator-Duty-01",
        "status": "dispatched"
    }
