"""
Build Indian Linguistic Risk Corpus (ILRC) - Curated Multilingual & Dialect Emergency Phrases.
Generates data/processed/indian_linguistic_risk_corpus.csv across core trauma domains,
now with first-class Sambalpuri (Kosli) and Santali tribal/regional expressions.
"""

import csv
from pathlib import Path

TEMPLATES = [
    # (en_p, en_s, hi_p, hi_s, od_p, od_s, sp_p, sp_s, sat_p, sat_s)
    ("", "", "", "", "", "", "", "", "", ""),
    ("Please ", " Please help.", "कृपया ", "। कृपया मदद करें।", "ଦୟାକରି ", "। ଦୟାକରି ସାହାଯ୍ୟ କରନ୍ତୁ।", "Daya kari ", " mor sahajya kara.", "Daya kate ", " banchaoing pe."),
    ("Right now, ", " I am scared.", "अभी, ", "। मैं डरा/डरी हूँ।", "ଏବେ, ", "। ମୁଁ ଭୟଭୀତ।", "Ebe, ", " mor darr laguchhe.", "Nita ge, ", " botor ge aikawkana."),
    ("I need help because ", " I need help.", "मुझे मदद चाहिए क्योंकि ", "। मुझे मदद चाहिए।", "ମୋତେ ସାହାଯ୍ୟ ଦରକାର କାରଣ ", "। ମୋତେ ସାହାଯ୍ୟ ଦରକାର।", "Mote sahajya darkar kanje ", " mote sahajya darkar.", "Masing darkar kanje ", " banchaoing pe."),
    ("Please understand, ", " This is urgent.", "कृपया समझिए, ", "। यह जरूरी है।", "ଦୟାକରି ବୁଝନ୍ତୁ, ", "। ଏହା ଜରୁରୀ।", "Bujha mor katha, ", " eha jaruri aichhe.", "Bujhau me, ", " aadi jaruri kana."),
    ("I am scared: ", " Please stay with me.", "मैं डरा/डरी हूँ: ", "। कृपया मेरे साथ रहें।", "ମୁଁ ଭୟଭୀତ: ", "। ଦୟାକରି ମୋ ସହିତ ରୁହନ୍ତୁ।", "Mor darr laguchhe: ", " mor sanghe thia hua.", "Botor aikawkana: ", " ing sang te tahenpe."),
    ("This is urgent: ", " I cannot handle this alone.", "यह जरूरी है: ", "। मैं इसे अकेले नहीं संभाल सकता/सकती।", "ଏହା ଜରୁରୀ: ", "। ମୁଁ ଏହାକୁ ଏକାକୀ ସମ୍ଭାଳିପାରୁନାହିଁ।", "Jaruri aichhe: ", " mu eka sambhali nai pare.", "Jaruri kana: ", " ing eskar bang sambhrao dadeakana."),
    ("Please act now: ", " Please do not ignore me.", "कृपया अभी कार्रवाई करें: ", "। कृपया मुझे अनदेखा न करें।", "ଦୟାକରି ଏବେ କାର୍ଯ୍ୟ କରନ୍ତୁ: ", "। ଦୟାକରି ମୋତେ ଅଣଦେଖା କରନ୍ତୁ ନାହିଁ।", "Ebe turant katha suna: ", " mote anadekha nai kara.", "Nita ge kami pe: ", " aalo pe bageana."),
    ("I need immediate help: ", " I need someone to help.", "मुझे तुरंत मदद चाहिए: ", "। मुझे किसी की मदद चाहिए।", "ମୋତେ ତୁରନ୍ତ ସାହାଯ୍ୟ ଦରକାର: ", "। ମୋତେ କାହାରୋ ସାହାଯ୍ୟ ଦରକାର।", "Turant sahajya darkar: ", " kahari madat pathao.", "Turat banchao darkar: ", " jahay hohoako pe."),
    ("For my safety, ", " Please take this seriously.", "मेरी सुरक्षा के लिए, ", "। कृपया इसे गंभीरता से लें।", "ମୋ ସୁରକ୍ଷା ପାଇଁ, ", "। ଦୟାକରି ଏହାକୁ ଗମ୍ଭୀରତାର ସହ ନିଅନ୍ତୁ।", "Mor surakshya lagi, ", " eha ke gambhira hisabe nia.", "Ingak suraksha lagi, ", " aadi jaruri kana.")
]

# Base phrases across 10 trauma domains, with explicit Sambalpuri (sp) and Santali (sat) phrases
BASE_PHRASES = [
    # 1. Immediate_Danger (including forest pursuit & wilderness)
    ("Immediate_Danger", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION",
     "I am in immediate danger.", "मैं तुरंत खतरे में हूँ।", "ମୁଁ ତୁରନ୍ତ ବିପଦରେ ଅଛି।",
     "Mu ebe khatara bipad re achhe.", "Ing turat khatra re menakana.",
     "danger", "danger", "ବିପଦ", "bipad, khatara", "khatra, bipod"),

    ("Immediate_Danger", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION",
     "They are chasing to kill me and I am hiding in the jungle.",
     "वे मुझे मारने के लिए दौड़ा रहे हैं और मैं जंगल में छिपा हूँ।",
     "ସେମାନେ ମୋତେ ମାରିବାକୁ ଗୋଡ଼ାଉଛନ୍ତି ଏବଂ ମୁଁ ଜଙ୍ଗଲରେ ଲୁଚିକି ଅଛି।",
     "Mor pache godauchhan marba boli, mu bana dongar re nuchi achhe.",
     "Gojing lagid ko panjayedina, bir re ukanakana.",
     "chasing, jungle, hiding", "marne, jungle, chhipa", "ଗୋଡ଼ାଉଛନ୍ତି, ଜଙ୍ଗଲ, ଲୁଚିକି",
     "godauchhan, marba, bana, dongar, nuchi", "panjayedina, gojing, bir, ukanakana"),

    ("Immediate_Danger", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION",
     "Please help me right now.", "कृपया अभी मेरी मदद करें।", "ଦୟାକରି ଏବେ ମୋତେ ସାହାଯ୍ୟ କରନ୍ତୁ।",
     "Daya kari ebe mor sahajya kara.", "Daya kate nita ge banchaoing pe.",
     "help now", "madad abhi", "ସାହାଯ୍ୟ ଏବେ", "sahajya ebe", "banchaoing nita"),

    ("Immediate_Danger", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION",
     "Someone is coming after me.", "कोई मेरे पीछे आ रहा है।", "କେହି ମୋ ପଛେ ପଛେ ଆସୁଛି।",
     "Kehi mor pache pache asuchhe.", "Jahay ing pachhe panjayedina.",
     "following me", "peeche aa raha", "ପଛେ ଆସୁଛି", "pache asuchhe", "panjayedina"),

    ("Immediate_Danger", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION",
     "I am not safe here.", "मैं यहाँ सुरक्षित नहीं हूँ।", "ମୁଁ ଏଠାରେ ସୁରକ୍ଷିତ ନୁହେଁ।",
     "Mu eithi safe nai nuhe.", "Ing nonde surakshit banukana.",
     "not safe", "surakshit nahi", "ସୁରକ୍ଷିତ ନୁହେଁ", "safe nai", "bang surakshit"),

    # 2. Physical_Assault
    ("Physical_Assault", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION",
     "Someone is hitting me.", "कोई मुझे मार रहा है।", "କେହି ମୋତେ ମାରୁଛି।",
     "Kehi mor pita karuchhe.", "Jahay dalan kanako.",
     "hitting, attack", "maar raha", "ମାରୁଛି", "mor pita, maruchhe", "dalan kanako"),

    ("Physical_Assault", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION",
     "I am being attacked with sticks and weapons.", "मुझ पर लाठी और हथियारों से हमला हो रहा है।", "ମୋ ଉପରେ ଲାଠି ଓ ଅସ୍ତ୍ରଶସ୍ତ୍ରରେ ଆକ୍ରମଣ ହେଉଛି।",
     "Mor upare lathi talwar dhariki attack karchhan.", "Ing re lathi kapi hasiyara te dalan kanako.",
     "attack, sticks, weapons", "lathi, hamla", "ଲାଠି, ଆକ୍ରମଣ, ଖଣ୍ଡା",
     "lathi, talwar, attack", "lathi, kapi, hasiyara, dalan"),

    ("Physical_Assault", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION",
     "Someone is beating me.", "कोई मुझे पीट रहा है।", "କେହି ମୋତେ ପିଟୁଛି।",
     "Kehi mote lathi re marba karuchhe.", "Jahay inge dalidinkana.",
     "beating", "peet raha", "ପିଟୁଛି", "pita karuchhe", "dalidinkana"),

    ("Physical_Assault", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION",
     "Please stop them from hurting me.", "कृपया उन्हें मुझे चोट पहुँचाने से रोकें।", "ଦୟାକରି ସେମାନଙ୍କୁ ମୋତେ ଆଘାତ କରିବାରୁ ରୋକନ୍ତୁ।",
     "Tanke roka mote marbaru.", "Unko aatkawko pe dal khon.",
     "hurt, stop", "chot, roko", "ଆଘାତ, ରୋକନ୍ତୁ", "roka, marbaru", "aatkaw, dal"),

    ("Physical_Assault", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION",
     "I have been physically assaulted.", "मेरे साथ शारीरिक हमला हुआ है।", "ମୋ ଉପରେ ଶାରୀରିକ ଆକ୍ରମଣ ହୋଇଛି।",
     "Mor upare sharirik mara pita heichhe.", "Ing re daldal hoyakana.",
     "physical assault", "shariirik hamla", "ଶାରୀରିକ ଆକ୍ରମଣ", "mara pita", "daldal"),

    # 3. Death_Threat
    ("Death_Threat", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION",
     "Someone threatened to kill me.", "किसी ने मुझे जान से मारने की धमकी दी है।", "କେହି ମୋତେ ମାରିଦେବାକୁ ଧମକ ଦେଇଛି।",
     "Kehi mate marba boli dhamki deuchhe.", "Jahay goje lagid menakada.",
     "kill, threat", "jaan se maar, dhamki", "ମାରିଦେବା, ଧମକ", "marba, dhamki", "goje, dhamki"),

    ("Death_Threat", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION",
     "They are threatening my life.", "वे मेरी जान को धमकी दे रहे हैं।", "ସେମାନେ ମୋ ଜୀବନକୁ ଧମକ ଦେଉଛନ୍ତି।",
     "Semaney mor jiban marba boli kahete achhan.", "Unko ingak jivi goje menako.",
     "life threat", "jaan ko dhamki", "ଜୀବନ, ଧମକ", "jiban, marba", "jivi, goje"),

    ("Death_Threat", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION",
     "I received a death threat.", "मुझे जान से मारने की धमकी मिली है।", "ମୋତେ ମାରିଦେବାର ଧମକ ମିଳିଛି।",
     "Mote marba dhamki milichhe.", "Ing goje dhamki namakana.",
     "death threat", "dhamki mili", "ଧମକ ମିଳିଛି", "marba dhamki", "goje dhamki"),

    ("Death_Threat", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION",
     "I am afraid they will kill me.", "मुझे डर है कि वे मुझे मार देंगे।", "ମୋତେ ଭୟ ଲାଗୁଛି ଯେ ସେମାନେ ମୋତେ ମାରିଦେବେ।",
     "Mote darr laguchhe se mane marba.", "Ing botor aikawkana unko gojina.",
     "fear, kill", "darr, maar denge", "ଭୟ, ମାରିଦେବେ", "darr, marba", "botor, gojina"),

    ("Death_Threat", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION",
     "Someone said they would kill me.", "किसी ने कहा कि वह मुझे मार देगा।", "କେହି କହିଛି ଯେ ସେ ମୋତେ ମାରିଦେବ।",
     "Kehi kahila se mote marba.", "Jahay menkeda se gojina.",
     "kill threat", "maar dega", "ମାରିଦେବ", "marba", "gojina"),

    # 4. Sexual_Violence
    ("Sexual_Violence", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION",
     "I am being sexually assaulted.", "मेरे साथ यौन हिंसा हो रही है।", "ମୋ ସହ ଯୌନ ହିଂସା ହେଉଛି।",
     "Mor sahita kharap byabahar jouna hinsa huchhe.", "Ing sahite kharap kami dalan kanako.",
     "sexual assault", "yaun hinsa", "ଯୌନ ହିଂସା", "jouna hinsa, kharap", "kharap kami"),

    ("Sexual_Violence", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION",
     "Someone is forcing sexual contact.", "कोई मुझे गलत काम के लिए मजबूर कर रहा है।", "କେହି ମୋତେ ଯୌନ ସମ୍ପର୍କ ପାଇଁ ବାଧ୍ୟ କରୁଛି।",
     "Kehi mote kharap kam lagi badhya karchhe.", "Jahay ing kharap kami lagid badhyo kana.",
     "forced contact", "majboor", "ବାଧ୍ୟ କରୁଛି", "badhya karchhe", "badhyo"),

    ("Sexual_Violence", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION",
     "I need help because of sexual violence.", "यौन हिंसा के कारण मुझे मदद चाहिए।", "ଯୌନ ହିଂସା ଯୋଗୁଁ ମୋତେ ସାହାଯ୍ୟ ଦରକାର।",
     "Jouna hinsa lagi mote sahajya darkar.", "Kharap kami khatir banchao darkar.",
     "sexual violence, help", "yaun hinsa, madad", "ଯୌନ ହିଂସା, ସାହାଯ୍ୟ", "jouna hinsa", "kharap kami"),

    ("Sexual_Violence", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION",
     "Please get me somewhere safe.", "कृपया मुझे किसी सुरक्षित जगह ले जाएँ।", "ଦୟାକରି ମୋତେ କୌଣସି ସୁରକ୍ଷିତ ସ୍ଥାନକୁ ନେଇଯାଆନ୍ତୁ।",
     "Daya kari mote kete safe jaga ku nia.", "Daya kate jahana surakshit thar te idiying pe.",
     "safe place", "surakshit jagah", "ସୁରକ୍ଷିତ ସ୍ଥାନ", "safe jaga", "surakshit thar"),

    ("Sexual_Violence", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION",
     "I am being forced against my will.", "मेरी इच्छा के विरुद्ध मुझे मजबूर किया जा रहा है।", "ମୋ ଇଚ୍ଛା ବିରୁଦ୍ଧରେ ମୋତେ ବାଧ୍ୟ କରାଯାଉଛି।",
     "Mor ichha bina mote badhya karchhan.", "Ingak kushi bina badhyo kanako.",
     "forced, against will", "ichha ke virudh", "ଇଚ୍ଛା ବିରୁଦ୍ଧରେ", "ichha bina", "kushi bina"),

    # 5. Domestic_Violence
    ("Domestic_Violence", "HIGH", "IMMEDIATE", "SAFETY_ESCALATION",
     "My partner is hurting me.", "मेरा साथी मुझे चोट पहुँचा रहा है।", "ମୋ ସାଥୀ ମୋତେ ଆଘାତ କରୁଛନ୍ତି।",
     "Mor ghare sanghar loka mote maruchhe.", "Ingak gharonj hor dalidinkana.",
     "partner, hurt", "chot, maar", "ସାଥୀ, ଆଘାତ", "ghare, maruchhe", "gharonj, dal"),

    ("Domestic_Violence", "HIGH", "IMMEDIATE", "SAFETY_ESCALATION",
     "My husband is hitting me.", "मेरे पति मुझे मार रहे हैं।", "ମୋ ସ୍ୱାମୀ ମୋତେ ମାରୁଛନ୍ତି।",
     "Mor samasta loga ghare mara pita karchhe.", "Ing bahu/herel dalidinkana.",
     "husband, hitting", "pati maar", "ସ୍ୱାମୀ, ମାରୁଛନ୍ତି", "samasta, pita", "herel, dal"),

    ("Domestic_Violence", "HIGH", "IMMEDIATE", "SAFETY_ESCALATION",
     "My in-laws are threatening me.", "ससुराल वाले मुझे धमका रहे हैं।", "ଶାଶୁଘର ଲୋକେ ମୋତେ ଧମକ ଦେଉଛନ୍ତି।",
     "Sasughara loka mote dhamki deuchhan.", "Sasur ghar hor dhamki emok kanako.",
     "in-laws, threat", "dhamka rahe", "ଶାଶୁଘର, ଧମକ", "sasughara, dhamki", "sasur ghar, dhamki"),

    ("Domestic_Violence", "HIGH", "IMMEDIATE", "SAFETY_ESCALATION",
     "Someone at home is attacking me.", "घर में कोई मुझ पर हमला कर रहा है।", "ଘରେ କେହି ମୋ ଉପରେ ଆକ୍ରମଣ କରୁଛି।",
     "Ghare ghusi kehi mote maruchhe.", "Orak re bolo kate dalidinkana.",
     "home attack", "ghar me hamla", "ଘରେ ଆକ୍ରମଣ", "ghare ghusi", "orak re bolo"),

    ("Domestic_Violence", "HIGH", "IMMEDIATE", "SAFETY_ESCALATION",
     "I am afraid to go home.", "मुझे घर जाने में डर लग रहा है।", "ମୋତେ ଘରକୁ ଯିବାକୁ ଭୟ ଲାଗୁଛି।",
     "Mote ghara jibaku darr laguchhe.", "Ing orak te chalak botor aikawkana.",
     "afraid, home", "ghar jane me darr", "ଘରକୁ ଭୟ", "ghara jibaku darr", "orak chalak botor"),

    # 6. Child_Endangerment
    ("Child_Endangerment", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION",
     "A child is in danger.", "एक बच्चा खतरे में है।", "ଗୋଟିଏ ଶିଶୁ ବିପଦରେ ଅଛି।",
     "Pila ta khatara bipad re aichhe.", "Gidra khatra re menaya.",
     "child danger", "bachha khatre me", "ଶିଶୁ ବିପଦରେ", "pila, bipad", "gidra, khatra"),

    ("Child_Endangerment", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION",
     "Someone is hurting the child.", "कोई बच्चे को चोट पहुँचा रहा है।", "କେହି ଶିଶୁକୁ ଆଘାତ କରୁଛି।",
     "Kehi pila ke maruchhe.", "Jahay gidra e dalidinkana.",
     "child hurt", "bachhe ko chot", "ଶିଶୁକୁ ଆଘାତ", "pila ke maruchhe", "gidra dal"),

    ("Child_Endangerment", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION",
     "Please protect this child.", "कृपया इस बच्चे की रक्षा करें।", "ଦୟାକରି ଏହି ଶିଶୁକୁ ସୁରକ୍ଷା ଦିଅନ୍ତୁ।",
     "Daya kari e pila ke banchao.", "Daya kate noa gidra e banchaoe pe.",
     "protect child", "bachhe ki raksha", "ଶିଶୁକୁ ସୁରକ୍ଷା", "pila banchao", "gidra banchao"),

    ("Child_Endangerment", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION",
     "The child is being threatened.", "बच्चे को धमकी दी जा रही है।", "ଶିଶୁକୁ ଧମକ ଦିଆଯାଉଛି।",
     "Pila ke dhamki deuchhan.", "Gidra e dhamki emay kanako.",
     "child threat", "bachhe ko dhamki", "ଶିଶୁକୁ ଧମକ", "pila dhamki", "gidra dhamki"),

    ("Child_Endangerment", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION",
     "I cannot keep the child safe.", "मैं बच्चे को सुरक्षित नहीं रख पा रहा हूँ।", "ମୁଁ ଶିଶୁକୁ ସୁରକ୍ଷିତ ରଖିପାରୁନାହିଁ।",
     "Mu pila ke safe nai rakhi pare.", "Ing gidra surakshit bang doho dadeakana.",
     "child unsafe", "bachha surakshit nahi", "ଶିଶୁ ଅସୁରକ୍ଷିତ", "pila safe nai", "gidra bang surakshit"),

    # 7. Social_Boycott & Caste Atrocity (Critical for MoSJE / PoA Act)
    ("Social_Boycott", "HIGH", "IMMEDIATE", "SAFETY_ESCALATION",
     "The village committee has socially boycotted us and banned water.",
     "गांव ने हमारा सामाजिक बहिष्कार कर दिया है और पानी बंद कर दिया है।",
     "ଗାଁ କମିଟି ଆମକୁ ସାମାଜିକ ବାସନ୍ଦ କରିଛି ଏବଂ ପିଇବା ପାଣି ବନ୍ଦ କରିଦେଇଛି।",
     "Gaon loka samaja ru khedi dele o pani debaku mana karle.",
     "Ato hor ato khon ko orok kidina ar dak nu mana akada ko.",
     "boycott, water ban", "samajik bahishkar, pani band", "ସାମାଜିକ ବାସନ୍ଦ, ପାଣି ବନ୍ଦ",
     "khedi dele, pani mana, samaja ru", "dak nu mana, ato khon orok"),

    ("Social_Boycott", "HIGH", "IMMEDIATE", "SAFETY_ESCALATION",
     "They are not allowing us to take water from the public tube well.",
     "वे हमें सार्वजनिक नलकूप से पानी नहीं लेने दे रहे हैं।",
     "ସେମାନେ ଆମକୁ ସରକାରୀ ନଳକୂପରୁ ପାଣି ନେବାକୁ ଦେଉନାହାନ୍ତି।",
     "Sarkari tube-well ru pani nebaku mana karchhan jati dekhi.",
     "Sarkari tube-well khon dak nu bang emok kanako jat khatir.",
     "water denied, tube well", "pani nahi lene de rahe", "ପାଣି ନେବାକୁ ମନା",
     "tube-well pani mana", "dak bang emok"),

    ("Social_Boycott", "HIGH", "IMMEDIATE", "SAFETY_ESCALATION",
     "They threatened us with caste abuse and expulsion.",
     "उन्होंने जातिसूचक गाली देकर हमें गांव से निकालने की धमकी दी।",
     "ସେମାନେ ଜାତିଆଣ ଗାଳି ଦେଇ ଆମକୁ ଗାଁରୁ ବାହାର କରିବାକୁ ଧମକ ଦେଲେ।",
     "Jati nam dhariki gali dele o gaon ru kadhideba kahile.",
     "Jat nutum te gali em keda ar ato khon orok ko menkeda.",
     "caste abuse, expulsion", "jati gali, nikalne ki dhamki", "ଜାତିଆଣ ଗାଳି, ଗାଁରୁ ବାହାର",
     "jati gali, gaon ru kadhideba", "jat gali, ato khon orok"),

    ("Social_Boycott", "HIGH", "IMMEDIATE", "SAFETY_ESCALATION",
     "Nobody is speaking to us or selling us rations.",
     "कोई हमसे बात नहीं कर रहा और राशन नहीं दे रहा है।",
     "କେହି ଆମ ସହ କଥା ହେଉନାହାନ୍ତି କି ରାସନ ଦେଉନାହାନ୍ତି।",
     "Kahi katha nai heba o ration dokan ru sauda nai deuchhan.",
     "Jahay katha bang kanako ar ration dukan khon sauda bang emok kanako.",
     "boycott, rations denied", "baat nahi, ration nahi", "କଥା ମନା, ରାସନ ବନ୍ଦ",
     "katha nai, ration nai", "katha bang, ration bang"),

    ("Social_Boycott", "HIGH", "IMMEDIATE", "SAFETY_ESCALATION",
     "They blocked the road to our house.",
     "उन्होंने हमारे घर का रास्ता बंद कर दिया है।",
     "ସେମାନେ ଆମ ଘର ରାସ୍ତା ବନ୍ଦ କରିଦେଇଛନ୍ତି।",
     "Mor ghara bata banda karidele.",
     "Ingak orak dahar bondo keda ko.",
     "road blocked", "rasta band", "ରାସ୍ତା ବନ୍ଦ", "bata banda", "dahar bondo"),

    # 8. Medical_Emergency
    ("Medical_Emergency", "CRITICAL", "IMMEDIATE", "MEDICAL_ESCALATION",
     "I cannot breathe properly.", "मैं ठीक से साँस नहीं ले पा रहा/रही हूँ।", "ମୁଁ ଠିକ୍ ଭାବରେ ନିଶ୍ୱାସ ନେଇପାରୁନାହିଁ।",
     "Mu thik se niswasa nai nei pare.", "Ing thik te sahed bang doho dadeakana.",
     "cannot breathe", "saans nahi", "ନିଶ୍ୱାସ ନେଇପାରୁନାହିଁ", "niswasa nai", "sahed bang"),

    ("Medical_Emergency", "CRITICAL", "IMMEDIATE", "MEDICAL_ESCALATION",
     "I need an ambulance.", "मुझे एम्बुलेंस चाहिए।", "ମୋତେ ଆମ୍ବୁଲାନ୍ସ ଦରକାର।",
     "Mote ambulance darkar.", "Ing ambulance darkar.",
     "ambulance", "ambulance", "ଆମ୍ବୁଲାନ୍ସ", "ambulance", "ambulance"),

    ("Medical_Emergency", "CRITICAL", "IMMEDIATE", "MEDICAL_ESCALATION",
     "Someone has collapsed.", "कोई बेहोश होकर गिर गया है।", "କେହି ବେହୋସ ହୋଇ ପଡ଼ିଯାଇଛନ୍ତି।",
     "Kehi behosh hoiki padigala.", "Jahay behosh kate nurheyena.",
     "collapsed, unconscious", "behosh ho gaya", "ବେହୋସ ହୋଇ ପଡ଼ିଯାଇଛନ୍ତି", "behosh padigala", "behosh nurheyena"),

    ("Medical_Emergency", "CRITICAL", "IMMEDIATE", "MEDICAL_ESCALATION",
     "I am bleeding heavily from head injury.", "सिर पर चोट से बहुत खून बह रहा है।", "ମୁଣ୍ଡ ଆଘାତରୁ ବହୁତ ରକ୍ତ ବୋହୁଛି।",
     "Munda phatiki bahut rakata bahuchhe.", "Bohok ghao khon aadi mayang jorok kana.",
     "bleeding, head injury", "khoon, chot", "ରକ୍ତ, ମୁଣ୍ଡ ଆଘାତ", "rakata, munda phatiki", "mayang, bohok"),

    ("Medical_Emergency", "CRITICAL", "IMMEDIATE", "MEDICAL_ESCALATION",
     "I need medical help now.", "मुझे अभी चिकित्सकीय मदद चाहिए।", "ମୋତେ ଏବେ ଚିକିତ୍ସା ସାହାଯ୍ୟ ଦରକାର।",
     "Mote ebe daktari sahajya darkar.", "Ing nita daktar banchao darkar.",
     "medical help", "chikitsa", "ଚିକିତ୍ସା ସାହାଯ୍ୟ", "daktari sahajya", "daktar banchao"),

    # 9. Self_Harm_Crisis
    ("Self_Harm_Crisis", "CRITICAL", "IMMEDIATE", "CRISIS_SUPPORT_ESCALATION",
     "I am thinking about ending my life.", "मैं अपनी जान देने के बारे में सोच रहा/रही हूँ।", "ମୁଁ ମୋ ଜୀବନ ହାରିବା ବିଷୟରେ ଭାବୁଛି।",
     "Mu mor jiban hariba boli bhabuchhe.", "Ing jivi goj lagid bhabna kanain.",
     "end life, suicide", "jaan dena", "ଜୀବନ ହାରିବା, ଆତ୍ମହତ୍ୟା", "jiban hariba", "jivi goj"),

    ("Self_Harm_Crisis", "CRITICAL", "IMMEDIATE", "CRISIS_SUPPORT_ESCALATION",
     "I do not feel safe with myself.", "मुझे अपने साथ सुरक्षित महसूस नहीं हो रहा।", "ମୁଁ ନିଜ ସହିତ ସୁରକ୍ଷିତ ଅନୁଭବ କରୁନାହିଁ।",
     "Mu nije surakshita nai lagbar.", "Ing nije surakshit bang bujhavkana.",
     "not safe, self", "surakshit nahi", "ସୁରକ୍ଷିତ ଅନୁଭବ କରୁନାହିଁ", "nije surakshita nai", "surakshit bang"),

    ("Self_Harm_Crisis", "CRITICAL", "IMMEDIATE", "CRISIS_SUPPORT_ESCALATION",
     "I need someone to stay with me.", "मुझे किसी के साथ रहने की जरूरत है।", "ମୋ ସହିତ କେହି ରହିବା ଦରକାର।",
     "Mor sahita kehi thia heba darkar.", "Ing sang te jahay tahen darkar.",
     "stay with me", "saath rahna", "ମୋ ସହିତ କେହି ରହିବା", "mor sahita", "ing sang te"),

    ("Self_Harm_Crisis", "CRITICAL", "IMMEDIATE", "CRISIS_SUPPORT_ESCALATION",
     "I am in extreme trauma and hopelessness.", "मैं अत्यधिक आघात और निराशा में हूँ।", "ମୁଁ ଅତ୍ୟଧିକ ମାନସିକ ଆଘାତ ଓ ନିରାଶାରେ ଅଛି।",
     "Mu aadi dukha o bipad re achhe.", "Ing aadi duk ar aashahin re menakana.",
     "trauma, hopeless", "aaghat, nirasha", "ମାନସିକ ଆଘାତ, ନିରାଶା", "dukha, bipad", "duk, aashahin"),

    ("Self_Harm_Crisis", "CRITICAL", "IMMEDIATE", "CRISIS_SUPPORT_ESCALATION",
     "Please help me stay safe.", "कृपया मुझे सुरक्षित रहने में मदद करें।", "ଦୟାକରି ମୋତେ ସୁରକ୍ଷିତ ରହିବାରେ ସାହାଯ୍ୟ କରନ୍ତୁ।",
     "Mote safe rahiba lagi help kara.", "Ing surakshit tahen lagi banchaoing pe.",
     "stay safe", "surakshit rahna", "ସୁରକ୍ଷିତ ରହିବାରେ", "safe rahiba", "surakshit tahen"),

    # 10. Emergency_Assistance
    ("Emergency_Assistance", "HIGH", "IMMEDIATE", "SAFETY_ESCALATION",
     "Please send the police to my location.", "कृपया मेरे स्थान पर पुलिस भेजें।", "ଦୟାକରି ମୋ ସ୍ଥାନକୁ ପୋଲିସ ପଠାନ୍ତୁ।",
     "Mor jaga ku police gadi pathao.", "Ingak thar te police gadi kulpe.",
     "police, send help", "police bhejo", "ପୋଲିସ ପଠାନ୍ତୁ", "police gadi pathao", "police gadi kulpe"),

    ("Emergency_Assistance", "HIGH", "IMMEDIATE", "SAFETY_ESCALATION",
     "I need the 112 police vehicle immediately.", "मुझे तुरंत 112 पुलिस की गाड़ी चाहिए।", "ମୋତେ ତୁରନ୍ତ ୧୧୨ ପୋଲିସ ଗାଡ଼ି ଦରକାର।",
     "Mote turant 112 police gadi darkar.", "Ing turat 112 police gadi darkar.",
     "112 police", "112 gaadi", "୧୧୨ ପୋଲିସ", "112 police gadi", "112 police"),

    ("Emergency_Assistance", "HIGH", "IMMEDIATE", "SAFETY_ESCALATION",
     "They broke into our house and broke everything.", "वे हमारे घर में घुस गए और सब कुछ तोड़ दिया।", "ସେମାନେ ଆମ ଘରେ ପଶି ସବୁ ଭାଙ୍ଗିଦେଲେ।",
     "Ghare ghusi sabu jinis bhangi dele.", "Orak re bolo kate sanam jinis bhangao keda ko.",
     "house break, vandalize", "ghar me todphod", "ଘରେ ପଶି ଭାଙ୍ଗିଦେଲେ", "ghare ghusi, bhangi dele", "orak bolo, bhangao"),

    ("Emergency_Assistance", "HIGH", "IMMEDIATE", "SAFETY_ESCALATION",
     "I need urgent government assistance.", "मुझे तत्काल सरकारी सहायता चाहिए।", "ମୋତେ ତୁରନ୍ତ ସରକାରୀ ସାହାଯ୍ୟ ଦରକାର।",
     "Mote turant sarkari sahajya darkar.", "Ing turat sarkari banchao darkar.",
     "government help", "sarkari sahayata", "ସରକାରୀ ସାହାଯ୍ୟ", "sarkari sahajya", "sarkari banchao"),

    ("Emergency_Assistance", "HIGH", "IMMEDIATE", "SAFETY_ESCALATION",
     "Please connect me to an officer immediately.", "कृपया मुझे तुरंत एक अधिकारी से जोड़ें।", "ଦୟାକରି ମୋତେ ତୁରନ୍ତ ଜଣେ ଅଧିକାରୀଙ୍କ ସହ ଯୋଡ଼ନ୍ତୁ।",
     "Babu/officer sanghe katha karao turant.", "Daya kate kamin/officer sang te ropor ochoying pe.",
     "connect officer", "adhikari se jodo", "ଅଧିକାରୀଙ୍କ ସହ ଯୋଡ଼ନ୍ତୁ", "officer sanghe katha", "officer sang ropor")
]


def generate_corpus():
    out_dir = Path(__file__).resolve().parent.parent / "data" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "indian_linguistic_risk_corpus.csv"

    rows = []
    phrase_id = 1

    for (cat, sev, urg, exp_act, en_base, hi_base, od_base, sp_base, sat_base,
         en_kw, hi_kw, od_kw, sp_kw, sat_kw) in BASE_PHRASES:

        en_core = en_base.rstrip(".!?,")
        hi_core = hi_base.rstrip(".!?,")
        od_core = od_base.rstrip(".!?,")
        sp_core = sp_base.rstrip(".!?,")
        sat_core = sat_base.rstrip(".!?,")

        for t_idx, (en_p, en_s, hi_p, hi_s, od_p, od_s, sp_p, sp_s, sat_p, sat_s) in enumerate(TEMPLATES):
            row_id = f"ILRC_{phrase_id:03d}"

            if t_idx == 0:
                en_text = en_base
                hi_text = hi_base
                od_text = od_base
                sp_text = sp_base
                sat_text = sat_base
            else:
                en_text = f"{en_p}{en_core}{en_s}"
                hi_text = f"{hi_p}{hi_core}{hi_s}"
                od_text = f"{od_p}{od_core}{od_s}"
                sp_text = f"{sp_p}{sp_core}{sp_s}"
                sat_text = f"{sat_p}{sat_core}{sat_s}"

            rows.append({
                "id": row_id,
                "category": cat,
                "severity": sev,
                "urgency": urg,
                "expected_action": exp_act,
                "english": en_text,
                "hindi": hi_text,
                "odia": od_text,
                "sambalpuri": sp_text,
                "santali": sat_text,
                "english_keywords": en_kw,
                "hindi_keywords": hi_kw,
                "odia_keywords": od_kw,
                "sambalpuri_keywords": sp_kw,
                "santali_keywords": sat_kw,
                "notes": "Multilingual emergency phrase including native Sambalpuri (Kosli) and Santali dialect variations."
            })
            phrase_id += 1

    fieldnames = [
        "id", "category", "severity", "urgency", "expected_action",
        "english", "hindi", "odia", "sambalpuri", "santali",
        "english_keywords", "hindi_keywords", "odia_keywords",
        "sambalpuri_keywords", "santali_keywords", "notes"
    ]

    with open(out_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Also copy to root data/ directory for top-level discovery
    root_file = Path(__file__).resolve().parent.parent / "data" / "indian_linguistic_risk_corpus.csv"
    with open(root_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Successfully generated {len(rows)} ILRC rows with Sambalpuri & Santali support:")
    print(f"  * {out_file}")
    print(f"  * {root_file}")


if __name__ == "__main__":
    generate_corpus()
