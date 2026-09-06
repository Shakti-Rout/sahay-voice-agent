import logging
from typing import Optional
from ..domain.models import (
    RiskAssessment,
    RiskLevel,
    DistressState,
    SafetyFlags
)
from .rules import SafetyRulesEngine

logger = logging.getLogger(__name__)


class TraumaController:
    """
    Central deterministic safety and triage authority.
    Applies safety rules, controls escalation, and constrains LLM autonomy.
    """

    def __init__(self):
        self.rules_engine = SafetyRulesEngine()

    def assess_and_control(
        self,
        call_id: str,
        distress_state: DistressState,
        latest_transcript: str
    ) -> RiskAssessment:
        """
        Evaluate full situation, apply deterministic overrides, and build RiskAssessment.
        """
        # 1. Check for deterministic rule overrides
        override_level, is_override, override_evidence = self.rules_engine.evaluate_overrides(
            latest_transcript, distress_state.safety_flags
        )

        final_evidence = list(set(distress_state.aggregated_evidence + override_evidence))

        if is_override and override_level == RiskLevel.CRITICAL:
            final_risk = RiskLevel.CRITICAL
            final_score = max(0.95, distress_state.rolling_distress_score)
            escalate = True
            action = "EMERGENCY ESCALATION: Connect to Emergency Services 112 / Instant Human Operator Takeover."
            logger.warning(f"[TraumaController] CRITICAL SAFETY OVERRIDE triggered for call {call_id}")

        elif is_override and override_level == RiskLevel.HIGH:
            final_risk = RiskLevel.HIGH if distress_state.current_risk_level != RiskLevel.CRITICAL else RiskLevel.CRITICAL
            final_score = max(0.75, distress_state.rolling_distress_score)
            escalate = True
            action = "PRIORITY ESCALATION: Alert human operator queue and provide grounding reassurance."

        else:
            final_risk = distress_state.current_risk_level
            final_score = distress_state.rolling_distress_score
            escalate = final_risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]

            if final_risk == RiskLevel.CRITICAL:
                action = "EMERGENCY ESCALATION: Transfer to senior supervisor and dispatch local support."
            elif final_risk == RiskLevel.HIGH:
                action = "HIGH DISTRESS: Offer direct counselor transfer and register incident report."
            elif final_risk == RiskLevel.MODERATE:
                action = "MODERATE DISTRESS: Provide empathetic guidance and legal assistance documentation."
            else:
                action = "STANDARD SUPPORT: Provide standard welfare and scheme information."

        # Determine automated multi-agency public service recommendations (PS 26093)
        recommended_services: List[str] = []
        if final_risk == RiskLevel.CRITICAL:
            recommended_services = [
                "Police Intervention: Immediate PCR 112 Emergency Dispatch",
                "Medical Assistance: Emergency 108 Trauma Ambulance",
                "Witness Protection: Statutory Protection under PoA Act Sec 15A",
                "Psychological Support: Tele-MANAS (14416) Crisis Trauma Unit",
                "Free Legal Aid: Immediate DLSA Defense Advocate Assigned"
            ]
        elif final_risk == RiskLevel.HIGH:
            recommended_services = [
                "Police Protection: Mandatory Zero FIR Registration under SC/ST PoA Act",
                "Witness & Victim Protection: Safe Shelter & Protection under Sec 15A",
                "Psychological Support: NHAA Clinical Trauma Counselor Referral",
                "Free Legal Aid: Special Public Prosecutor Assigned under Sec 15A(11)",
                "Interim Relief: Immediate Financial Relief under PoA Rules Sec 12(4)"
            ]
        elif final_risk == RiskLevel.MODERATE:
            recommended_services = [
                "Legal Aid: District Legal Services Authority (DLSA) Representation",
                "Grievance Redressal: Formal Atrocity / Discrimination Petition Lodged",
                "Counselor Referral: Mental Well-being & Stress Support"
            ]
        else:
            recommended_services = [
                "Administrative Guidance: MoSJE Welfare Schemes & Scholarships",
                "Standard Helpline Support: Formal Inquiry & Grievance Logged on 14566"
            ]

        final_svi = round(float(final_score), 3)
        svi_pct = int(round(final_svi * 100))

        assessment = RiskAssessment(
            call_id=call_id,
            risk_level=final_risk,
            risk_score=final_score,
            svi_score=final_svi,
            svi_percentage=svi_pct,
            sub_indices=distress_state.sub_indices,
            confidence=0.88,
            safety_flags=distress_state.safety_flags,
            evidence=final_evidence,
            recommended_action=action,
            recommended_services=recommended_services,
            requires_human_escalation=escalate
        )

        return assessment
