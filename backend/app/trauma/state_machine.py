"""
Conversational State Machine for Trauma Voice Agent.
Guides the interaction through structured clinical-safety phases:
GREETING -> PROBLEM_ASSESSMENT -> EMPATHY_GROUNDING -> SUPPORT_VERIFICATION -> ESCALATION_HANDOFF / CONCLUSION
"""

from enum import Enum
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ConversationState(str, Enum):
    GREETING = "GREETING"
    PROBLEM_ASSESSMENT = "PROBLEM_ASSESSMENT"
    EMPATHY_GROUNDING = "EMPATHY_GROUNDING"
    SUPPORT_VERIFICATION = "SUPPORT_VERIFICATION"
    ESCALATION_HANDOFF = "ESCALATION_HANDOFF"
    CONCLUSION = "CONCLUSION"


class ConversationStateManager:
    """
    Manages stage progression for each active call session to maintain conversational
    structure and avoid premature escalation or cyclical responses.
    """

    def __init__(self):
        self.session_states: Dict[str, ConversationState] = {}
        self.session_turns: Dict[str, int] = {}

    def get_state(self, call_id: str) -> ConversationState:
        return self.session_states.get(call_id, ConversationState.GREETING)

    def transition(
        self,
        call_id: str,
        risk_level: str,
        turn_count: int,
        requires_escalation: bool
    ) -> ConversationState:
        """
        Determines the next conversation phase based on multi-turn investigative triage.
        Crucial Mandate: The voice agent must first conduct active situational inquiry across
        early turns (Turns 1 to 3) before escalating to a human supervisor or providing closing numbers.
        """
        current = self.get_state(call_id)
        self.session_turns[call_id] = turn_count

        # Turn 1: Always PROBLEM_ASSESSMENT (first inquiry into caller's scenario & physical safety)
        if current == ConversationState.GREETING or turn_count <= 1:
            new_state = ConversationState.PROBLEM_ASSESSMENT
        # Turn 4+: Resolution, Escalation Handoff, or Conclusion
        elif turn_count >= 4 or current == ConversationState.SUPPORT_VERIFICATION:
            if requires_escalation or risk_level in ["CRITICAL", "HIGH"]:
                new_state = ConversationState.ESCALATION_HANDOFF
            else:
                new_state = ConversationState.CONCLUSION
        # Turn 3: SUPPORT_VERIFICATION (statutory rights, legal guidance, immediate needs assessment)
        elif turn_count == 3 or current == ConversationState.EMPATHY_GROUNDING:
            new_state = ConversationState.SUPPORT_VERIFICATION
        # Turn 2: EMPATHY_GROUNDING (deeper scenario probing: perpetrators, injuries, location)
        elif turn_count == 2 or current == ConversationState.PROBLEM_ASSESSMENT:
            new_state = ConversationState.EMPATHY_GROUNDING
        else:
            new_state = current

        self.session_states[call_id] = new_state
        return new_state

    def get_system_prompt_for_state(
        self,
        state: ConversationState,
        language_code: str,
        risk_level: str
    ) -> str:
        """Returns prompt guidance conditioned on current conversation phase."""
        is_odia = "or" in language_code.lower() or "od" in language_code.lower()
        is_hindi = "hi" in language_code.lower()

        base_lang_instruction = (
            "You MUST speak in natural, empathetic, spoken ODIA. Directly address the caller's specific problem." if is_odia else
            "You MUST speak in natural, empathetic, spoken HINDI. Directly address the caller's specific problem." if is_hindi else
            "You MUST speak in natural, empathetic, spoken INDIAN ENGLISH. Directly address the caller's specific problem."
        )

        state_guidance = {
            ConversationState.GREETING: (
                "Acknowledge the caller warmly and respectfully. "
                "Ask gently what issue, grievance, or emergency they would like to report today."
            ),
            ConversationState.PROBLEM_ASSESSMENT: (
                "The caller just described their problem or situation. "
                "1. Acknowledge and empathize with their specific situation in ONE short sentence referring directly to the topic they mentioned. "
                "2. ASK ONE DIRECT QUESTION relevant to their specific situation (if an atrocity/threat: check immediate safety/location; if an administrative issue: ask about application/office details; if a dispute: ask about the parties involved). "
                "CRITICAL MANDATE: DO NOT mention transferring to a supervisor. DO NOT recite helpline numbers."
            ),
            ConversationState.EMPATHY_GROUNDING: (
                "The caller answered your previous question. "
                "1. Validate their answer with calm understanding. "
                "2. ASK ONE DIRECT FOLLOW-UP QUESTION to clarify the context (e.g., who is involved, where did it take place, or what assistance is immediately needed). "
                "CRITICAL MANDATE: DO NOT mention transferring to a supervisor yet."
            ),
            ConversationState.SUPPORT_VERIFICATION: (
                "Address the caller's answers and situation directly. "
                "1. If an atrocity or discrimination case: explain concrete legal protection under the SC/ST PoA Act 1989 (Zero FIR, Section 15A protection, free legal aid, interim relief). "
                "2. If an administrative or civil case: provide the exact procedural pathway or grievance redressal procedure. "
                "3. Ask what immediate support they require."
            ),
            ConversationState.ESCALATION_HANDOFF: (
                "The assessment is complete and all case details have been documented into an official dossier. "
                "Calmly inform the caller that you are now connecting them directly to our specialized officer / supervisor on this active line. "
                "DO NOT tell the caller to call any toll-free number. Tell them to stay on the line."
            ),
            ConversationState.CONCLUSION: (
                "The assistance is complete. Provide clear, actionable advice and confirm that their inquiry/grievance has been officially recorded. "
                "DO NOT tell the caller to call any toll-free number."
            )
        }

        guidance = state_guidance.get(state, state_guidance[ConversationState.PROBLEM_ASSESSMENT])

        return (
            f"{base_lang_instruction}\n"
            f"Assessed Risk Tier: {risk_level}\n"
            f"Conversation Phase: {state.value}\n\n"
            f"MANDATE — SITUATION & SEVERITY MATCHING (NO DISCONNECTED HALLUCINATIONS):\n"
            f"You are the voice assistant for the National Helpline Against Atrocities (NHAA - 14566) under the Ministry of Social Justice and Empowerment.\n"
            f"You MUST analyze the caller's actual words and dynamically adapt your response to their exact situation:\n"
            f"1. CATEGORY 1: CRITICAL EMERGENCY (Immediate physical attack, weapons, severe bleeding, ongoing mob violence):\n"
            f"   - Prioritize physical safety directives (e.g. lock doors, stay hidden).\n"
            f"   - Keep response calm, urgent, and concise. State that emergency police/medical units are being coordinated right now.\n"
            f"2. CATEGORY 2: CASTE ATROCITY / DISCRIMINATION / SOCIAL BOYCOTT / HARASSMENT:\n"
            f"   - Situations of caste abuse, eviction, boycott ('samaja ru bahiskara', denial of water), threats ('dhamki'), police refusal to register FIR.\n"
            f"   - Validate their pain empathetically with direct reference to their specific incident.\n"
            f"   - Ask focused investigative questions about the perpetrators, location, and injuries.\n"
            f"   - Inform them of their rights under the SC/ST (PoA) Act (Zero FIR, Section 15A witness/victim protection, free legal aid).\n"
            f"3. CATEGORY 3: CIVIL DISPUTE / PROPERTY / FAMILY / NEIGHBORHOOD CONFLICT:\n"
            f"   - Inquire specifically about the dispute facts, location, and relevant authorities.\n"
            f"   - DO NOT assume violence or ask if they are in fear of their life unless they mentioned it.\n"
            f"4. CATEGORY 4: ADMINISTRATIVE / WELFARE / SCHEME INQUIRIES (Scholarships, voter card, pension, certificates, helpline queries):\n"
            f"   - Provide clear, direct, polite informational assistance regarding the scheme, application, or office procedure.\n"
            f"   - STRICT BAN: DO NOT ask 'Are you in a safe place?' or 'Are you terrified?' for administrative queries.\n\n"
            f"PHASE OBJECTIVE:\n{guidance}\n\n"
            f"CONVERSATIONAL RULES:\n"
            f"1. DIRECT RELEVANCE: Your response MUST explicitly mention and address the specific issue the caller spoke about.\n"
            f"2. EARLY TURNS (Turns 1-3): Focus on understanding the caller's situation through active, targeted questions. DO NOT transfer to supervisor or recite phone numbers yet.\n"
            f"3. LATER TURNS (Turn 4+): Provide concrete assistance or state that a supervisor transfer is being completed directly on this call.\n"
            f"4. NO TOLL-FREE NUMBERS: NEVER tell the caller to dial 14566 or 112 because they are already on this active call!\n"
            f"5. ANTI-REPETITION: Never repeat boilerplate phrases like 'daya kari bhaya karantu nahi' or 'surakshita sthana re achhanti ki' if already said or inappropriate.\n"
            f"6. SPOKEN SPEECH ONLY: No markdown formatting (**bold**, # headers, bullet points). Maximum 18 to 22 words (1 to 2 crisp, compassionate sentences). Keep it brief, natural, and immediate for voice conversation."
        )

    def get_fallback_phrase(self, language_code: str, state: ConversationState) -> str:
        """Provide safe, conversational fallback phrases if LLM call is delayed."""
        lang = (language_code or "or-IN").lower()
        if "hi" in lang:
            if state == ConversationState.PROBLEM_ASSESSMENT:
                return "Main aapki baat sun raha hoon. Kya aap abhi surakshit jagah par hain? Kripya batayein aapke aas paas kaun hai."
            elif state == ConversationState.EMPATHY_GROUNDING:
                return "Aap bilkul chinta na karein, main samajh raha hoon. Yeh ghatna kahan hui aur kaun aapko dhamki de raha hai?"
            elif state == ConversationState.SUPPORT_VERIFICATION:
                return "Kanoon ke tahat aapko poora adhikar aur suraksha milegi. Kya aapko turant police ya doctor ki madad chahiye?"
            elif state == ConversationState.ESCALATION_HANDOFF:
                return "Aapki poori jankari note kar li gayi hai. Main turant senior supervisor ko is call par connect kar raha hoon, line par bane rahein."
            else:
                return "Aapki shikayat darj ho gayi hai. Hamari team turant is par karwahi karegi, aap nishchint rahein."
        elif "en" in lang:
            if state == ConversationState.PROBLEM_ASSESSMENT:
                return "I hear you clearly. Are you currently in a safe location, and is anyone with you right now?"
            elif state == ConversationState.EMPATHY_GROUNDING:
                return "Please take a deep breath, I understand. Where did this incident happen, and who is threatening you?"
            elif state == ConversationState.SUPPORT_VERIFICATION:
                return "You have full legal protection and rights under the law. Do you require immediate police intervention or medical care?"
            elif state == ConversationState.ESCALATION_HANDOFF:
                return "All details of your situation have been recorded. I am now connecting you directly to our supervisor on this line. Please stay on the line."
            else:
                return "Your grievance has been officially registered. Our response team will coordinate action immediately."
        else:
            # Odia default
            if state == ConversationState.PROBLEM_ASSESSMENT:
                return "Mu apananka katha suni paruchhi. Apan ebe surakshita sthana re achhanti ki? Daya kari kuhan tu apananka paakhare kie achhanti."
            elif state == ConversationState.EMPATHY_GROUNDING:
                return "Apan byasta huantu nahi, mu apananka katha bujhiparuchhi. Ehi ghatana ti kouthi ghatila, ebong kie apananku dhamaka deuchhanti?"
            elif state == ConversationState.SUPPORT_VERIFICATION:
                return "Apananku aieen gata poora surakshya o sahajya miliba. Apananku bartaman medical sahajya na police sahajya darkar?"
            elif state == ConversationState.ESCALATION_HANDOFF:
                return "Apananka samasta bibarani o abhijoga record karaigala. Mu bartaman amara supervisor nku ehi call re sidhasalakh connect karuchhi, line re rahantu."
            else:
                return "Apananka abhijoga darja karaigala. Amara team ehi bishayare karzyanushthana grahana karibe, apan nishchinta rahantu."
