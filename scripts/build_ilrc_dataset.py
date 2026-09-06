"""
Build Indian Linguistic Risk Corpus (ILRC) - 500 Curated Emergency Phrases.
Generates data/processed/indian_linguistic_risk_corpus.csv across 10 trauma domains.
"""

import csv
from pathlib import Path

TEMPLATES = [
    # (en_prefix, en_suffix, hi_prefix, hi_suffix, od_prefix, od_suffix, hi_trans_prefix, hi_trans_suffix, od_trans_prefix, od_trans_suffix)
    ("", "", "", "", "", "", "", "", "", ""),
    ("Please ", " Please help.", "कृपया ", "। कृपया मदद करें।", "ଦୟାକରି ", "। ଦୟାକରି ସାହାଯ୍ୟ କରନ୍ତୁ।", "kripaya ", " kripaya madad karen", "dayakari ", " dayakari sahayya karantu"),
    ("Right now, ", " I am scared.", "अभी, ", "। मैं डरा/डरी हूँ।", "ଏବେ, ", "। ମୁଁ ଭୟଭୀତ।", "abhi ", " main dara/dari hoon", "ebe ", " mun bhayabhita"),
    ("I need help because ", " I need help.", "मुझे मदद चाहिए क्योंकि ", "। मुझे मदद चाहिए।", "ମୋତେ ସାହାଯ୍ୟ ଦରକାର କାରଣ ", "। ମୋତେ ସାହାଯ୍ୟ ଦରକାର।", "mujhe madad chahiye kyonki ", " mujhe madad chahiye", "mote sahayya darkar karana ", " mote sahayya darkar"),
    ("Please understand, ", " This is urgent.", "कृपया समझिए, ", "। यह जरूरी है।", "ଦୟାକରି ବୁଝନ୍ତୁ, ", "। ଏହା ଜରୁରୀ।", "kripaya samajhiye ", " yah zaroori hai", "dayakari bujhantu ", " eha jaruri"),
    ("I am scared: ", " Please stay with me.", "मैं डरा/डरी हूँ: ", "। कृपया मेरे साथ रहें।", "ମୁଁ ଭୟଭୀତ: ", "। ଦୟାକରି ମୋ ସହିତ ରୁହନ୍ତୁ।", "main dara/dari hoon ", " kripaya मेरे saath rahen", "mun bhayabhita ", " dayakari mo sahita ruhhantu"),
    ("This is urgent: ", " I cannot handle this alone.", "यह जरूरी है: ", "। मैं इसे अकेले नहीं संभाल सकता/सकती।", "ଏହା ଜରୁରୀ: ", "। ମୁଁ ଏହାକୁ ଏକାକୀ ସମ୍ଭାଳିପାରୁନାହିଁ।", "yah zaroori hai ", " main ise akele nahin sambhal sakta/sakti", "eha jaruri ", " mun ଏହାକୁ ekaki sambhaliparunahin"),
    ("Please act now: ", " Please do not ignore me.", "कृपया अभी कार्रवाई करें: ", "। कृपया मुझे अनदेखा न करें।", "ଦୟାକରି ଏବେ କାର୍ଯ୍ୟ କରନ୍ତୁ: ", "। ଦୟାକରି ମୋତେ ଅଣଦେଖା କରନ୍ତୁ ନାହିଁ।", "kripaya abhi karvai karen ", " kripaya mujhe andekha na karen", "dayakari ebe karya karantu ", " dayakari mote anadekha karantu nahin"),
    ("I need immediate help: ", " I need someone to help.", "मुझे तुरंत मदद चाहिए: ", "। मुझे किसी की मदद चाहिए।", "ମୋତେ ତୁରନ୍ତ ସାହାଯ୍ୟ ଦରକାର: ", "। ମୋତେ କାହାରୋ ସାହାଯ୍ୟ ଦରକାର।", "mujhe turant madad chahiye ", " mujhe kisi ki madad chahiye", "mote ତୁରନ୍ତ sahayya darkar ", " mote kaharo sahayya darkar"),
    ("For my safety, ", " Please take this seriously.", "मेरी सुरक्षा के लिए, ", "। कृपया इसे गंभीरता से लें।", "ମୋ ସୁରକ୍ଷା ପାଇଁ, ", "। ଦୟାକରି ଏହାକୁ ଗମ୍ଭୀରତାର ସହ ନିଅନ୍ତୁ।", "meri suraksha ke liye ", " kripaya ise gambhirta se len", "mo surakshya pain ", " dayakari ଏହାକୁ ଗମ୍ଭୀରତାର ସହ niantu")
]

# 50 base phrases (5 per category)
BASE_PHRASES = [
    # 1. Immediate_Danger
    ("Immediate_Danger", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "I am in immediate danger.", "मैं तुरंत खतरे में हूँ।", "ମୁଁ ତୁରନ୍ତ ବିପଦରେ ଅଛି।", "main turant खतरे में hoon", "mun ତୁରନ୍ତ ବିପଦରେ achhi", "danger", "danger", "ବିପଦ"),
    ("Immediate_Danger", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "Please help me right now.", "कृपया अभी मेरी मदद करें।", "ଦୟାକରି ଏବେ ମୋତେ ସାହାଯ୍ୟ କରନ୍ତୁ।", "kripaya abhi meri madad karen", "dayakari ebe mote sahayya karantu", "help now", "help now", "ସାହାଯ୍ୟ"),
    ("Immediate_Danger", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "I need emergency help.", "मुझे आपातकालीन मदद चाहिए।", "ମୋତେ ଜରୁରୀ ସାହାଯ୍ୟ ଦରକାର।", "mujhe आपातकालीन madad chahiye", "mote jaruri sahayya darkar", "emergency help", "emergency help", "ଜରୁରୀ ସାହାଯ୍ୟ"),
    ("Immediate_Danger", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "Someone is coming after me.", "कोई मेरे पीछे आ रहा है।", "କେହି ମୋ ପଛେ ପଛେ ଆସୁଛି।", "कोई मेरे पीछे आ रहा hai", "କେହି mo ପଛେ ପଛେ ଆସୁଛି", "following me", "following me", "ପଛେ"),
    ("Immediate_Danger", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "I am not safe here.", "मैं यहाँ सुरक्षित नहीं हूँ।", "ମୁଁ ଏଠାରେ ସୁରକ୍ଷିତ ନୁହେଁ।", "main यहाँ सुरक्षित nahin hoon", "mun ଏଠାରେ ସୁରକ୍ଷିତ ନୁହେଁ", "not safe", "not safe", "ସୁରକ୍ଷିତ ନୁହେଁ"),

    # 2. Physical_Assault
    ("Physical_Assault", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "Someone is hitting me.", "कोई मुझे मार रहा है।", "କେହି ମୋତେ ମାରୁଛି।", "कोई mujhe मार रहा hai", "କେହି mote ମାରୁଛି", "hitting, attack", "hitting, attack", "ମାରୁଛି"),
    ("Physical_Assault", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "I am being attacked.", "मुझ पर हमला हो रहा है।", "ମୋ ଉପରେ ଆକ୍ରମଣ ହେଉଛି।", "मुझ पर हमला हो रहा hai", "mo ଉପରେ ଆକ୍ରମଣ ହେଉଛି", "attack", "attack", "ଆକ୍ରମଣ"),
    ("Physical_Assault", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "Someone is beating me.", "कोई मुझे पीट रहा है।", "କେହି ମୋତେ ପିଟୁଛି।", "कोई mujhe पीट रहा hai", "କେହି mote ପିଟୁଛି", "beating", "beating", "ପିଟୁଛି"),
    ("Physical_Assault", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "Please stop them from hurting me.", "कृपया उन्हें मुझे चोट पहुँचाने से रोकें।", "ଦୟାକରି ସେମାନଙ୍କୁ ମୋତେ ଆଘାତ କରିବାରୁ ରୋକନ୍ତୁ।", "kripaya उन्हें mujhe चोट पहुँचाने se रोकें", "dayakari ସେମାନଙ୍କୁ mote ଆଘାତ କରିବାରୁ ରୋକନ୍ତୁ", "hurt, stop", "hurt, stop", "ଆଘାତ"),
    ("Physical_Assault", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "I have been physically assaulted.", "मेरे साथ शारीरिक हमला हुआ है।", "ମୋ ଉପରେ ଶାରୀରିକ ଆକ୍ରମଣ ହୋଇଛି।", "मेरे saath शारीरिक हमला हुआ hai", "mo ଉପରେ ଶାରୀରିକ ଆକ୍ରମଣ ହୋଇଛି", "physical assault", "physical assault", "ଶାରୀରିକ ଆକ୍ରମଣ"),

    # 3. Death_Threat
    ("Death_Threat", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "Someone threatened to kill me.", "किसी ने मुझे जान से मारने की धमकी दी है।", "କେହି ମୋତେ ମାରିଦେବାକୁ ଧମକ ଦେଇଛି।", "kisi ने mujhe जान se मारने ki धमकी दी hai", "କେହି mote ମାରିଦେବାକୁ ଧମକ ଦେଇଛି", "kill, threat", "kill, threat", "ମାରିଦେବା, ଧମକ"),
    ("Death_Threat", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "They are threatening my life.", "वे मेरी जान को धमकी दे रहे हैं।", "ସେମାନେ ମୋ ଜୀବନକୁ ଧମକ ଦେଉଛନ୍ତି।", "वे meri जान को धमकी दे रहे हैं", "ସେମାନେ mo ଜୀବନକୁ ଧମକ ଦେଉଛନ୍ତି", "life threat", "life threat", "ଜୀବନ, ଧମକ"),
    ("Death_Threat", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "I received a death threat.", "मुझे जान से मारने की धमकी मिली है।", "ମୋତେ ମାରିଦେବାର ଧମକ ମିଳିଛି।", "mujhe जान se मारने ki धमकी मिली hai", "mote ମାରିଦେବାର ଧମକ ମିଳିଛି", "death threat", "death threat", "ଧମକ"),
    ("Death_Threat", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "I am afraid they will kill me.", "मुझे डर है कि वे मुझे मार देंगे।", "ମୋତେ ଭୟ ଲାଗୁଛି ଯେ ସେମାନେ ମୋତେ ମାରିଦେବେ।", "mujhe डर hai कि वे mujhe मार देंगे", "mote ଭୟ ଲାଗୁଛି ଯେ ସେମାନେ mote ମାରିଦେବେ", "fear, kill", "fear, kill", "ଭୟ"),
    ("Death_Threat", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "Someone said they would kill me.", "किसी ने कहा कि वह मुझे मार देगा।", "କେହି କହିଛି ଯେ ସେ ମୋତେ ମାରିଦେବ।", "kisi ने कहा कि वह mujhe मार देगा", "କେହି କହିଛି ଯେ ସେ mote ମାରିଦେବ", "kill threat", "kill threat", "ମାରିଦେବ"),

    # 4. Sexual_Violence
    ("Sexual_Violence", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "I am being sexually assaulted.", "मेरे साथ यौन हिंसा हो रही है।", "ମୋ ସହ ଯୌନ ହିଂସା ହେଉଛି।", "मेरे saath यौन हिंसा हो रही hai", "mo ସହ ଯୌନ ହିଂସା ହେଉଛି", "sexual assault", "sexual assault", "ଯୌନ ହିଂସା"),
    ("Sexual_Violence", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "Someone is forcing sexual contact.", "कोई मुझे यौन संपर्क के लिए मजबूर कर रहा है।", "କେହି ମୋତେ ଯୌନ ସମ୍ପର୍କ ପାଇଁ ବାଧ୍ୟ କରୁଛି।", "कोई mujhe यौन संपर्क ke liye मजबूर kar रहा hai", "କେହି mote ଯୌନ ସମ୍ପର୍କ pain ବାଧ୍ୟ କରୁଛି", "forced sexual contact", "forced sexual contact", "ବାଧ୍ୟ"),
    ("Sexual_Violence", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "I need help because of sexual violence.", "यौन हिंसा के कारण मुझे मदद चाहिए।", "ଯୌନ ହିଂସା ଯୋଗୁଁ ମୋତେ ସାହାଯ୍ୟ ଦରକାର।", "यौन हिंसा ke कारण mujhe madad chahiye", "ଯୌନ ହିଂସା ଯୋଗୁଁ mote sahayya darkar", "sexual violence, help", "sexual violence, help", "ଯୌନ ହିଂସା"),
    ("Sexual_Violence", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "Please get me somewhere safe.", "कृपया मुझे किसी सुरक्षित जगह ले जाएँ।", "ଦୟାକରି ମୋତେ କୌଣସି ସୁରକ୍ଷିତ ସ୍ଥାନକୁ ନେଇଯାଆନ୍ତୁ।", "kripaya mujhe kisi सुरक्षित जगह ले जाएँ", "dayakari mote କୌଣସି ସୁରକ୍ଷିତ ସ୍ଥାନକୁ ନେଇଯାଆନ୍ତୁ", "safe place", "safe place", "ସୁରକ୍ଷିତ ସ୍ଥାନ"),
    ("Sexual_Violence", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "I am being forced against my will.", "मेरी इच्छा के विरुद्ध मुझे मजबूर किया जा रहा है।", "ମୋ ଇଚ୍ଛା ବିରୁଦ୍ଧରେ ମୋତେ ବାଧ୍ୟ କରାଯାଉଛି।", "meri इच्छा ke विरुद्ध mujhe मजबूर किया जा रहा hai", "mo ଇଚ୍ଛା ବିରୁଦ୍ଧରେ mote ବାଧ୍ୟ କରାଯାଉଛି", "forced, against will", "forced, against will", "ବାଧ୍ୟ"),

    # 5. Domestic_Violence
    ("Domestic_Violence", "HIGH", "IMMEDIATE", "SAFETY_ESCALATION", "My partner is hurting me.", "मेरा साथी मुझे चोट पहुँचा रहा है।", "ମୋ ସାଥୀ ମୋତେ ଆଘାତ କରୁଛନ୍ତି।", "मेरा साथी mujhe चोट पहुँचा रहा hai", "mo ସାଥୀ mote ଆଘାତ କରୁଛନ୍ତି", "partner, hurt", "partner, hurt", "ସାଥୀ"),
    ("Domestic_Violence", "HIGH", "IMMEDIATE", "SAFETY_ESCALATION", "My husband is hitting me.", "मेरे पति मुझे मार रहे हैं।", "ମୋ ସ୍ୱାମୀ ମୋତେ ମାରୁଛନ୍ତି।", "मेरे पति mujhe मार रहे हैं", "mo ସ୍ୱାମୀ mote ମାରୁଛନ୍ତି", "husband, hitting", "husband, hitting", "ସ୍ୱାମୀ, ମାରୁଛନ୍ତି"),
    ("Domestic_Violence", "HIGH", "IMMEDIATE", "SAFETY_ESCALATION", "My wife is threatening me.", "मेरी पत्नी मुझे धमका रही है।", "ମୋ ସ୍ତ୍ରୀ ମୋତେ ଧମକ ଦେଉଛନ୍ତି।", "meri पत्नी mujhe धमका रही hai", "mo ସ୍ତ୍ରୀ mote ଧମକ ଦେଉଛନ୍ତି", "wife, threat", "wife, threat", "ସ୍ତ୍ରୀ, ଧମକ"),
    ("Domestic_Violence", "HIGH", "IMMEDIATE", "SAFETY_ESCALATION", "Someone at home is attacking me.", "घर में कोई मुझ पर हमला कर रहा है।", "ଘରେ କେହି ମୋ ଉପରେ ଆକ୍ରମଣ କରୁଛି।", "घर में कोई मुझ पर हमला kar रहा hai", "ଘରେ କେହି mo ଉପରେ ଆକ୍ରମଣ କରୁଛି", "home, attack", "home, attack", "ଘର, ଆକ୍ରମଣ"),
    ("Domestic_Violence", "HIGH", "IMMEDIATE", "SAFETY_ESCALATION", "I am afraid to go home.", "मुझे घर जाने में डर लग रहा है।", "ମୋତେ ଘରକୁ ଯିବାକୁ ଭୟ ଲାଗୁଛି।", "mujhe घर जाने में डर लग रहा hai", "mote ଘରକୁ ଯିବାକୁ ଭୟ ଲାଗୁଛି", "afraid, home", "afraid, home", "ଭୟ, ଘର"),

    # 6. Child_Endangerment
    ("Child_Endangerment", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "A child is in danger.", "एक बच्चा खतरे में है।", "ଗୋଟିଏ ଶିଶୁ ବିପଦରେ ଅଛି।", "एक बच्चा खतरे में hai", "ଗୋଟିଏ ଶିଶୁ ବିପଦରେ achhi", "child, danger", "child, danger", "ଶିଶୁ, ବିପଦ"),
    ("Child_Endangerment", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "Someone is hurting the child.", "कोई बच्चे को चोट पहुँचा रहा है।", "କେହି ଶିଶୁକୁ ଆଘାତ କରୁଛି।", "कोई बच्चे को चोट पहुँचा रहा hai", "କେହି ଶିଶୁକୁ ଆଘାତ କରୁଛି", "child, hurt", "child, hurt", "ଶିଶୁ, ଆଘାତ"),
    ("Child_Endangerment", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "Please protect this child.", "कृपया इस बच्चे की रक्षा करें।", "ଦୟାକରି ଏହି ଶିଶୁକୁ ସୁରକ୍ଷା ଦିଅନ୍ତୁ।", "kripaya इस बच्चे ki रक्षा karen", "dayakari ଏହି ଶିଶୁକୁ surakshya ଦିଅନ୍ତୁ", "protect child", "protect child", "ଶିଶୁ, ସୁରକ୍ଷା"),
    ("Child_Endangerment", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "The child is being threatened.", "बच्चे को धमकी दी जा रही है।", "ଶିଶୁକୁ ଧମକ ଦିଆଯାଉଛି।", "बच्चे को धमकी दी जा रही hai", "ଶିଶୁକୁ ଧମକ ଦିଆଯାଉଛି", "child, threat", "child, threat", "ଶିଶୁ, ଧମକ"),
    ("Child_Endangerment", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "I cannot keep the child safe.", "मैं बच्चे को सुरक्षित नहीं रख पा रहा/रही हूँ।", "ମୁଁ ଶିଶୁକୁ ସୁରକ୍ଷିତ ରଖିପାରୁନାହିଁ।", "main बच्चे को सुरक्षित nahin रख पा रहा/रही hoon", "mun ଶିଶୁକୁ ସୁରକ୍ଷିତ ରଖିପାରୁନାହିଁ", "child, unsafe", "child, unsafe", "ଶିଶୁ, ଅସୁରକ୍ଷିତ"),

    # 7. Kidnapping_Restraint
    ("Kidnapping_Restraint", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "I am being held against my will.", "मुझे मेरी इच्छा के विरुद्ध रोका गया है।", "ମୋତେ ମୋ ଇଚ୍ଛା ବିରୁଦ୍ଧରେ ଅଟକାଇ ରଖାଯାଇଛି।", "mujhe meri इच्छा ke विरुद्ध रोका गया hai", "mote mo ଇଚ୍ଛା ବିରୁଦ୍ଧରେ ଅଟକାଇ ରଖାଯାଇଛି", "held, against will", "held, against will", "ଅଟକାଇ"),
    ("Kidnapping_Restraint", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "I cannot leave this place.", "मैं इस जगह से जा नहीं सकता/सकती।", "ମୁଁ ଏହି ସ୍ଥାନରୁ ଯାଇପାରୁନାହିଁ।", "main इस जगह se जा nahin sakta/sakti", "mun ଏହି ସ୍ଥାନରୁ ଯାଇପାରୁନାହିଁ", "cannot leave", "cannot leave", "ଯାଇପାରୁନାହିଁ"),
    ("Kidnapping_Restraint", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "Someone is keeping me here.", "कोई मुझे यहाँ रोककर रख रहा है।", "କେହି ମୋତେ ଏଠାରେ ଅଟକାଇ ରଖିଛି।", "कोई mujhe यहाँ रोककर रख रहा hai", "କେହି mote ଏଠାରେ ଅଟକାଇ ରଖିଛି", "kept here", "kept here", "ଅଟକାଇ"),
    ("Kidnapping_Restraint", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "I have been kidnapped.", "मेरा अपहरण कर लिया गया है।", "ମୋତେ ଅପହରଣ କରାଯାଇଛି।", "मेरा अपहरण kar लिया गया hai", "mote ଅପହରଣ କରାଯାଇଛି", "kidnapped", "kidnapped", "ଅପହରଣ"),
    ("Kidnapping_Restraint", "CRITICAL", "IMMEDIATE", "SAFETY_ESCALATION", "Please help me escape safely.", "कृपया मुझे सुरक्षित निकलने में मदद करें।", "ଦୟାକରି ମୋତେ ସୁରକ୍ଷିତ ଭାବେ ବାହାରିବାରେ ସାହାଯ୍ୟ କରନ୍ତୁ।", "kripaya mujhe सुरक्षित निकलने में madad karen", "dayakari mote ସୁରକ୍ଷିତ ଭାବେ ବାହାରିବାରେ sahayya karantu", "escape, safe", "escape, safe", "ବାହାରିବା"),

    # 8. Medical_Emergency
    ("Medical_Emergency", "CRITICAL", "IMMEDIATE", "MEDICAL_ESCALATION", "I cannot breathe properly.", "मैं ठीक से साँस नहीं ले पा रहा/रही हूँ।", "ମୁଁ ଠିକ୍ ଭାବରେ ନିଶ୍ୱାସ ନେଇପାରୁନାହିଁ।", "main ठीक se साँस nahin ले पा रहा/रही hoon", "mun ଠିକ୍ ଭାବରେ ନିଶ୍ୱାସ ନେଇପାରୁନାହିଁ", "cannot breathe", "cannot breathe", "ନିଶ୍ୱାସ"),
    ("Medical_Emergency", "CRITICAL", "IMMEDIATE", "MEDICAL_ESCALATION", "I need an ambulance.", "मुझे एम्बुलेंस चाहिए।", "ମୋତେ ଆମ୍ବୁଲାନ୍ସ ଦରକାର।", "mujhe एम्बुलेंस chahiye", "mote ଆମ୍ବୁଲାନ୍ସ darkar", "ambulance", "ambulance", "ଆମ୍ବୁଲାନ୍ସ"),
    ("Medical_Emergency", "CRITICAL", "IMMEDIATE", "MEDICAL_ESCALATION", "Someone has collapsed.", "कोई बेहोश होकर गिर गया है।", "କେହି ବେହୋସ ହୋଇ ପଡ଼ିଯାଇଛନ୍ତି।", "कोई बेहोश होकर गिर गया hai", "କେହି ବେହୋସ ହୋଇ ପଡ଼ିଯାଇଛନ୍ତି", "collapsed, unconscious", "collapsed, unconscious", "ବେହୋସ"),
    ("Medical_Emergency", "CRITICAL", "IMMEDIATE", "MEDICAL_ESCALATION", "I am seriously injured.", "मुझे गंभीर चोट लगी है।", "ମୋତେ ଗୁରୁତର ଆଘାତ ଲାଗିଛି।", "mujhe गंभीर चोट लगी hai", "mote ଗୁରୁତର ଆଘାତ ଲାଗିଛି", "serious injury", "serious injury", "ଗୁରୁତର ଆଘାତ"),
    ("Medical_Emergency", "CRITICAL", "IMMEDIATE", "MEDICAL_ESCALATION", "I need medical help now.", "मुझे अभी चिकित्सकीय मदद चाहिए।", "ମୋତେ ଏବେ ଚିକିତ୍ସା ସାହାଯ୍ୟ ଦରକାର।", "mujhe abhi चिकित्सकीय madad chahiye", "mote ebe ଚିକିତ୍ସା sahayya darkar", "medical help", "medical help", "ଚିକିତ୍ସା"),

    # 9. Self_Harm_Crisis
    ("Self_Harm_Crisis", "CRITICAL", "IMMEDIATE", "CRISIS_SUPPORT_ESCALATION", "I am thinking about hurting myself.", "मैं खुद को नुकसान पहुँचाने के बारे में सोच रहा/रही हूँ।", "ମୁଁ ନିଜକୁ ଆଘାତ କରିବା ବିଷୟରେ ଭାବୁଛି।", "main खुद को नुकसान पहुँचाने ke बारे में सोच रहा/रही hoon", "mun ନିଜକୁ ଆଘାତ କରିବା ବିଷୟରେ ଭାବୁଛି", "hurt myself", "hurt myself", "ନିଜକୁ ଆଘାତ"),
    ("Self_Harm_Crisis", "CRITICAL", "IMMEDIATE", "CRISIS_SUPPORT_ESCALATION", "I do not feel safe with myself.", "मुझे अपने साथ सुरक्षित महसूस नहीं हो रहा।", "ମୁଁ ନିଜ ସହିତ ସୁରକ୍ଷିତ ଅନୁଭବ କରୁନାହିଁ।", "mujhe अपने saath सुरक्षित महसूस nahin हो रहा", "mun ନିଜ sahita ସୁରକ୍ଷିତ ଅନୁଭବ କରୁନାହିଁ", "not safe, self", "not safe, self", "ସୁରକ୍ଷିତ ନୁହେଁ"),
    ("Self_Harm_Crisis", "CRITICAL", "IMMEDIATE", "CRISIS_SUPPORT_ESCALATION", "I need someone to stay with me.", "मुझे किसी के साथ रहने की जरूरत है।", "ମୋ ସହିତ କେହି ରହିବା ଦରକାର।", "mujhe kisi ke saath रहने ki जरूरत hai", "mo sahita କେହି ରହିବା darkar", "stay with me", "stay with me", "ମୋ ସହିତ"),
    ("Self_Harm_Crisis", "CRITICAL", "IMMEDIATE", "CRISIS_SUPPORT_ESCALATION", "I am in a mental health crisis.", "मैं मानसिक स्वास्थ्य संकट में हूँ।", "ମୁଁ ମାନସିକ ସ୍ୱାସ୍ଥ୍ୟ ସଙ୍କଟରେ ଅଛି।", "main मानसिक स्वास्थ्य संकट में hoon", "mun ମାନସିକ ସ୍ୱାସ୍ଥ୍ୟ ସଙ୍କଟରେ achhi", "mental health crisis", "mental health crisis", "ମାନସିକ ସଙ୍କଟ"),
    ("Self_Harm_Crisis", "CRITICAL", "IMMEDIATE", "CRISIS_SUPPORT_ESCALATION", "Please help me stay safe.", "कृपया मुझे सुरक्षित रहने में मदद करें।", "ଦୟାକରି ମୋତେ ସୁରକ୍ଷିତ ରହିବାରେ ସାହାଯ୍ୟ କରନ୍ତୁ।", "kripaya mujhe सुरक्षित रहने में madad karen", "dayakari mote ସୁରକ୍ଷିତ ରହିବାରେ sahayya karantu", "stay safe", "stay safe", "ସୁରକ୍ଷିତ"),

    # 10. Emergency_Assistance
    ("Emergency_Assistance", "HIGH", "IMMEDIATE", "SAFETY_ESCALATION", "Please contact emergency services.", "कृपया आपातकालीन सेवाओं से संपर्क करें।", "ଦୟାକରି ଜରୁରୀକାଳୀନ ସେବା ସହ ଯୋଗାଯୋଗ କରନ୍ତୁ।", "kripaya आपातकालीन सेवाओं se संपर्क karen", "dayakari ଜରୁରୀକାଳୀନ ସେବା ସହ ଯୋଗାଯୋଗ karantu", "emergency services", "emergency services", "ଜରୁରୀକାଳୀନ ସେବା"),
    ("Emergency_Assistance", "HIGH", "IMMEDIATE", "SAFETY_ESCALATION", "Please send help to my location.", "कृपया मेरे स्थान पर मदद भेजें।", "ଦୟାକରି ମୋ ସ୍ଥାନକୁ ସାହାଯ୍ୟ ପଠାନ୍ତୁ।", "kripaya मेरे स्थान पर madad भेजें", "dayakari mo ସ୍ଥାନକୁ sahayya ପଠାନ୍ତୁ", "send help, location", "send help, location", "ସାହାଯ୍ୟ, ସ୍ଥାନ"),
    ("Emergency_Assistance", "HIGH", "IMMEDIATE", "SAFETY_ESCALATION", "I need the police.", "मुझे पुलिस चाहिए।", "ମୋତେ ପୋଲିସ ଦରକାର।", "mujhe पुलिस chahiye", "mote ପୋଲିସ darkar", "police", "police", "ପୋଲିସ"),
    ("Emergency_Assistance", "HIGH", "IMMEDIATE", "SAFETY_ESCALATION", "Please call an emergency number.", "कृपया आपातकालीन नंबर पर फोन करें।", "ଦୟାକରି ଜରୁରୀକାଳୀନ ନମ୍ବରକୁ ଫୋନ୍ କରନ୍ତୁ।", "kripaya आपातकालीन नंबर पर फोन karen", "dayakari ଜରୁରୀକାଳୀନ ନମ୍ବରକୁ ଫୋନ୍ karantu", "emergency number", "emergency number", "ଜରୁରୀକାଳୀନ ନମ୍ବର"),
    ("Emergency_Assistance", "HIGH", "IMMEDIATE", "SAFETY_ESCALATION", "I need urgent assistance.", "मुझे तुरंत सहायता चाहिए।", "ମୋତେ ତୁରନ୍ତ ସାହାଯ୍ୟ ଦରକାର।", "mujhe turant सहायता chahiye", "mote ତୁରନ୍ତ sahayya darkar", "urgent assistance", "urgent assistance", "ତୁରନ୍ତ ସାହାଯ୍ୟ")
]


def generate_corpus():
    out_dir = Path(__file__).resolve().parent.parent / "data" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "indian_linguistic_risk_corpus.csv"

    rows = []
    phrase_id = 1

    for cat, sev, urg, exp_act, en_base, hi_base, od_base, hi_tr_base, od_tr_base, en_kw, hi_kw, od_kw in BASE_PHRASES:
        # Strip trailing punctuation for template formatting
        en_core = en_base.rstrip(".!?,")
        hi_core = hi_base.rstrip("।!?,")
        od_core = od_base.rstrip("।!?,")
        hi_tr_core = hi_tr_base.rstrip(".!?,")
        od_tr_core = od_tr_base.rstrip(".!?,")

        for t_idx, (en_p, en_s, hi_p, hi_s, od_p, od_s, hi_tr_p, hi_tr_s, od_tr_p, od_tr_s) in enumerate(TEMPLATES):
            row_id = f"ILRC_{phrase_id:03d}"

            if t_idx == 0:
                en_text = en_base
                hi_text = hi_base
                od_text = od_base
                hi_tr_text = hi_tr_base
                od_tr_text = od_tr_base
            else:
                en_text = f"{en_p}{en_core}{en_s}"
                hi_text = f"{hi_p}{hi_core}{hi_s}"
                od_text = f"{od_p}{od_core}{od_s}"
                hi_tr_text = f"{hi_tr_p}{hi_tr_core}{hi_tr_s}"
                od_tr_text = f"{od_tr_p}{od_tr_core}{od_tr_s}"

            rows.append({
                "id": row_id,
                "category": cat,
                "severity": sev,
                "urgency": urg,
                "expected_action": exp_act,
                "english": en_text,
                "hindi": hi_text,
                "odia": od_text,
                "hindi_transliteration": hi_tr_text,
                "odia_transliteration": od_tr_text,
                "english_keywords": en_kw,
                "hindi_keywords": hi_kw,
                "odia_keywords": od_kw,
                "notes": "Synthetic evaluation phrase; native-speaker validation recommended."
            })
            phrase_id += 1

    with open(out_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "category", "severity", "urgency", "expected_action",
            "english", "hindi", "odia", "hindi_transliteration", "odia_transliteration",
            "english_keywords", "hindi_keywords", "odia_keywords", "notes"
        ])
        writer.writeheader()
        writer.writerows(rows)

    # Also copy to root data/ directory for easy top-level discovery
    root_file = Path(__file__).resolve().parent.parent / "data" / "indian_linguistic_risk_corpus.csv"
    with open(root_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "category", "severity", "urgency", "expected_action",
            "english", "hindi", "odia", "hindi_transliteration", "odia_transliteration",
            "english_keywords", "hindi_keywords", "odia_keywords", "notes"
        ])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Successfully generated {len(rows)} ILRC rows:")
    print(f"  * {out_file}")
    print(f"  * {root_file}")


if __name__ == "__main__":
    generate_corpus()
