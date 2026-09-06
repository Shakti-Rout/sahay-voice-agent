"""
Verified Legal, Emergency, and Rehabilitation Knowledge Base.
Mandate: Zero Hallucination. Every document corresponds to official statutory acts and government helplines.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class KnowledgeDocument:
    id: str
    title: str
    category: str  # emergency | legal | medical | counselling | scheme
    source: str
    jurisdiction: str
    keywords: List[str]
    content: str
    content_odia: Optional[str] = None
    content_hindi: Optional[str] = None


VERIFIED_KNOWLEDGE_DOCUMENTS: List[KnowledgeDocument] = [
    KnowledgeDocument(
        id="NHAA-14566-CORE",
        title="NHAA 14566 National Helpline Against Atrocities",
        category="emergency",
        source="Ministry of Social Justice and Empowerment, Government of India",
        jurisdiction="National",
        keywords=["14566", "nhaa", "atrocity", "caste", "discrimination", "helpline", "complaint", "fir", "police"],
        content=(
            "The National Helpline Against Atrocities (14566) operates 24x7 toll-free under the Department "
            "of Social Justice & Empowerment. It ensures immediate registration of grievances under the SC/ST "
            "(Prevention of Atrocities) Act, tracks FIR progress, monitors investigation by DySP/ACP officers, "
            "and facilitates immediate relief and compensation to victims."
        ),
        content_odia=(
            "ଜାତୀୟ ଅତ୍ୟାଚାର ନିରୋଧ ହେଲ୍ପଲାଇନ (14566) ଏକ ନିଶୁଳ୍କ ୨୪ ଘଣ୍ଟିଆ ସେବା। ଏହା SC/ST ଅତ୍ୟାଚାର ନିବାରଣ ଆଇନ "
            "ଅଧୀନରେ ଅଭିଯୋଗ ପଞ୍ଜୀକରଣ, ତୁରନ୍ତ ସୁରକ୍ଷା ଓ କ୍ଷତିପୂରଣ ସହାୟତା ପ୍ରଦାନ କରେ।"
        ),
        content_hindi=(
            "राष्ट्रीय अत्याचार निवारण हेल्पलाइन (14566) सामाजिक न्याय एवं अधिकारिता मंत्रालय द्वारा संचालित एक 24x7 "
            "टोल-फ्री हेल्पलाइन है, जो SC/ST अत्याचार निवारण अधिनियम के तहत शिकायतों को दर्ज कराने और तत्काल सुरक्षा "
            "व मुआवजा दिलाने में मदद करती है।"
        )
    ),
    KnowledgeDocument(
        id="POA-SEC-15A-RIGHTS",
        title="Section 15A SC/ST Prevention of Atrocities Act - Rights of Victims and Witnesses",
        category="legal",
        source="Scheduled Castes and the Scheduled Tribes (Prevention of Atrocities) Act, 1989 (Amended 2015)",
        jurisdiction="National",
        keywords=["15a", "protection", "witness", "threat", "intimidation", "safe shelter", "rights", "poa act"],
        content=(
            "Under Section 15A of the PoA Act: (1) Victims and witnesses have the fundamental right to be treated "
            "with dignity and compassion. (2) It is the state's duty to protect victims and witnesses from intimidation, "
            "threat, coercion, or violence. (3) State must provide safe shelter, relocation, police escorts, and "
            "round-the-clock protection when threats exist."
        ),
        content_odia=(
            "SC/ST ଅତ୍ୟାଚାର ନିବାରଣ ଆଇନର ଧାରା 15A ଅନୁଯାୟୀ, ପୀଡ଼ିତ ଓ ସାକ୍ଷୀମାନଙ୍କୁ ସମ୍ମାନର ସହ ବ୍ୟବହାର କରିବା ଏବଂ "
            "ଧମକ ବା ହିଂସାରୁ ସମ୍ପୂର୍ଣ୍ଣ ପୋଲିସ ସୁରକ୍ଷା ଓ ନିରାପଦ ଆଶ୍ରୟ ଯୋଗାଇଦେବା ସରକାରଙ୍କ ଦାୟିତ୍ୱ।"
        ),
        content_hindi=(
            "अत्याचार निवारण अधिनियम की धारा 15A के तहत पीड़ितों और गवाहों को गरिमा के साथ जीने, किसी भी धमकी से "
            "सुरक्षा पाने तथा सुरक्षित आश्रय और पुलिस सुरक्षा प्राप्त करने का कानूनी अधिकार है।"
        )
    ),
    KnowledgeDocument(
        id="POA-SEC-15A-LEGAL-AID",
        title="Section 15A(6) Free Legal Aid and Representation",
        category="legal",
        source="SC/ST PoA Act & National Legal Services Authority (NALSA)",
        jurisdiction="National",
        keywords=["legal aid", "lawyer", "advocate", "free", "nalsa", "dlsa", "court", "representation", "15100"],
        content=(
            "Section 15A(6) mandates free legal aid to all victims of atrocities through District Legal Services "
            "Authorities (DLSA) and Legal Aid Clinics. Victims are entitled to an advocate of their choice from the "
            "Special Public Prosecutor panel or legal aid panel at state expense. National Legal Aid Helpline: 15100."
        ),
        content_odia=(
            "ଧାରା 15A(6) ଅନୁସାରେ ସମସ୍ତ ପୀଡ଼ିତଙ୍କୁ ଜିଲ୍ଲା ଆଇନ ସେବା ପ୍ରାଧିକରଣ (DLSA) ମାଧ୍ୟମରେ ମାଗଣା ଓକିଲ ଓ ଆଇନଗତ "
            "ସହାୟତା ମିଳିବାର ଅଧିକାର ରହିଛି। NALSA ହେଲ୍ପଲାଇନ: 15100।"
        ),
        content_hindi=(
            "धारा 15A(6) के अंतर्गत सभी पीड़ितों को जिला विधिक सेवा प्राधिकरण (DLSA) द्वारा निःशुल्क कानूनी सहायता "
            "और वकील उपलब्ध कराया जाता है। राष्ट्रीय विधिक सेवा हेल्पलाइन: 15100।"
        )
    ),
    KnowledgeDocument(
        id="EMERGENCY-112-POLICE",
        title="National Emergency Support System (112)",
        category="emergency",
        source="Ministry of Home Affairs (MHA), Government of India",
        jurisdiction="National",
        keywords=["112", "police", "danger", "attack", "emergency", "urgent", "lathi", "weapon", "beat", "sos"],
        content=(
            "112 is India's unified single emergency response number for immediate police, fire, or ambulance "
            "dispatch. Calls are geo-tagged and prioritized for instant distress response with Emergency Response "
            "Vehicles (ERVs) dispatched within minutes."
        ),
        content_odia=(
            "112 ହେଉଛି ଜାତୀୟ ଜରୁରୀକାଳୀନ ହେଲ୍ପଲାଇନ। ଯଦି ଜୀବନ ପ୍ରତି ବିପଦ ଥାଏ କିମ୍ବା ତୁରନ୍ତ ପୋଲିସ ସହାୟତା ଦରକାର, "
            "ତେବେ 112 ରେ କଲ କରନ୍ତୁ।"
        ),
        content_hindi=(
            "112 भारत का एकीकृत आपातकालीन नंबर है। किसी भी शारीरिक खतरे, हमले या पुलिस की त्वरित सहायता के लिए "
            "तुरंत 112 पर कॉल किया जा सकता है।"
        )
    ),
    KnowledgeDocument(
        id="TELE-MANAS-14416",
        title="Tele-MANAS Psychological Trauma & Mental Health Support (14416)",
        category="counselling",
        source="Ministry of Health and Family Welfare, Government of India",
        jurisdiction="National",
        keywords=["14416", "tele manas", "crying", "anxiety", "depression", "panic", "fear", "counselling", "mental health"],
        content=(
            "Tele-MANAS (14416) is a 24x7 toll-free mental health helpline providing free, confidential psychological "
            "first-aid, trauma counselling, and psychiatric support in 20+ regional Indian languages by certified "
            "mental health professionals."
        ),
        content_odia=(
            "ଟେଲି-ମାନସ (14416) ଏକ ନିଶୁଳ୍କ ମାନସିକ ସ୍ୱାସ୍ଥ୍ୟ ଓ ପରାମର୍ଶ ହେଲ୍ପଲାଇନ। ମାନସିକ ଆଘାତ, ଭୟ ବା ଚିନ୍ତାରୁ ମୁକ୍ତି "
            "ପାଇଁ ବିଶେଷଜ୍ଞ କାଉନସେଲରଙ୍କ ସହ କଥା ହୋଇପାରିବେ।"
        ),
        content_hindi=(
            "टेली-मानस (14416) भारत सरकार का 24x7 मानसिक स्वास्थ्य परामर्श हेल्पलाइन है, जहां आघात, घबराहट और चिंता "
            "के समय प्रशिक्षित मनोवैज्ञानिकों से निःशुल्क परामर्श प्राप्त किया जा सकता है।"
        )
    ),
    KnowledgeDocument(
        id="POA-RELIEF-REHABILITATION",
        title="Statutory Relief and Economic Rehabilitation Scheme",
        category="scheme",
        source="Central Sector Scheme for Implementation of PCR & PoA Acts",
        jurisdiction="National",
        keywords=["compensation", "relief", "money", "fund", "hospital", "injury", "financial aid", "damages"],
        content=(
            "Under PoA Rules (Schedule-II), victims of atrocities are entitled to cash relief ranging from ₹85,000 "
            "to ₹8,25,000 based on the nature of atrocity. 50% of the relief amount is mandatorily released within 7 days "
            "upon FIR registration and medical examination, with remaining balance released upon chargesheet submission."
        ),
        content_odia=(
            "ଅତ୍ୟାଚାର ନିବାରଣ ନିୟମ ଅନୁସାରେ ପୀଡ଼ିତଙ୍କୁ ₹୮୫,୦୦୦ ରୁ ₹୮,୨୫,୦୦୦ ପର୍ଯ୍ୟନ୍ତ ସରକାରୀ ଆର୍ଥିକ କ୍ଷତିପୂରଣ ଏବଂ ପୁନର୍ବାସ "
            "ସହାୟତା ମିଳିବାର ପ୍ରାବଧାନ ରହିଛି। FIR ପରେ ପ୍ରଥମ କିସ୍ତି ୭ ଦିନ ମଧ୍ୟରେ ମିଳିଥାଏ।"
        ),
        content_hindi=(
            "अत्याचार निवारण नियमों के तहत पीड़ितों को अपराध की गंभीरता के आधार पर ₹85,000 से लेकर ₹8,25,000 तक की "
            "आर्थिक सहायता और राहत दी जाती है। 50% राशि FIR दर्ज होने और मेडिकल जांच के 7 दिनों के भीतर जारी की जाती है।"
        )
    ),
    KnowledgeDocument(
        id="PFA-GROUNDING-CRISIS",
        title="Psychological First Aid (PFA) & Acute Trauma De-escalation Protocol",
        category="counselling",
        source="WHO Psychological First Aid Guidelines & Tele-MANAS Grounding Standards",
        jurisdiction="National",
        keywords=["grounding", "breathing", "panic", "hyperventilating", "trembling", "crying", "scared", "shivering", "calm down", "breathe", "darichhi", "dara"],
        content=(
            "Immediate Trauma De-escalation Protocol: (1) Voice Modulation: Low pitch, slow tempo, steady acoustic cadence. "
            "(2) 4-4-4 Box Breathing: 'Apan shanta hoantu. Lamba swasa niantu, 4 second dharantu, dheere dheere chhadantu.' "
            "(3) Sensory Reorientation: Name 3 safe objects in sight, feel feet firmly on the ground. "
            "(4) Presence Validation: 'Mu apananka sathire achhi. Apan ebe surakshita sthana re achhanti.'"
        ),
        content_odia=(
            "ଆପଣ ଶାନ୍ତ ହୁଅନ୍ତୁ, ଗଭୀର ଲମ୍ବା ନିଶ୍ୱାସ ନିଅନ୍ତୁ। ମୁଁ ଆପଣଙ୍କ ସହିତ ଅଛି ଏବଂ ଆପଣଙ୍କ କଥା ଧ୍ୟାନର ସହ ଶୁଣୁଛି। "
            "ଧୀରେ ଧୀରେ କୁହନ୍ତୁ କ'ଣ ଘଟିଛି, ଆମେ ଆପଣଙ୍କୁ ସମ୍ପୂର୍ଣ୍ଣ ସୁରକ୍ଷା ଓ ସାହାଯ୍ୟ ପ୍ରଦାନ କରିବୁ।"
        ),
        content_hindi=(
            "आप गहरी सांस लीजिए और शांत हो जाइए। मैं आपके साथ हूं और आपकी पूरी बात सुन रहा हूं। "
            "धीरे-धीरे बताइए कि क्या हुआ है, आपको उचित सुरक्षा और तुरंत कानूनी व आपातकालीन सहायता मिलेगी।"
        )
    )
]
