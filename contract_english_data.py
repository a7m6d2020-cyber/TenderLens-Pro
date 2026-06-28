"""
═══════════════════════════════════════════════════════════════════════════════
Contract English Tutor — قاعدة البيانات التعليمية
مصطلحات الإنجليزية التعاقدية (FIDIC وغيرها) + الدروس + نصوص القراءة
═══════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# قاعدة المصطلحات: كل مصطلح يحتوي على:
#   en          : المصطلح بالإنجليزية
#   ipa         : النطق الصوتي الدولي IPA
#   syllables   : تقطيع المقاطع مع النبر (CAPS = المقطع المنبور)
#   ar          : الترجمة العربية
#   def_ar      : الشرح بالعربية
#   ex_en       : جملة مثال من سياق العقود
#   ex_ar       : ترجمة الجملة
#   collocations: متلازمات لفظية شائعة
#   cat         : التصنيف
#   tip         : نصيحة نطق/استخدام للمتحدث العربي (اختياري)
# ─────────────────────────────────────────────────────────────────────────────

VOCAB: list[dict] = [
    # ══ 1. أطراف العقد ══════════════════════════════════════════════════════
    {"en": "Employer", "ipa": "/ɪmˈplɔɪər/", "syllables": "im-PLOY-er",
     "ar": "صاحب العمل / رب العمل",
     "def_ar": "الطرف الذي يطلب تنفيذ الأعمال ويلتزم بدفع قيمة العقد. في عقود الفيديك هو المالك وليس «الموظِّف» بالمعنى الوظيفي.",
     "ex_en": "The Employer shall give the Contractor right of access to the Site within the time stated in the Contract Data.",
     "ex_ar": "يمنح صاحبُ العمل المقاولَ حقَّ الدخول إلى الموقع خلال المدة المحددة في بيانات العقد.",
     "collocations": ["Employer's Representative", "Employer's Requirements", "Employer-caused delay"],
     "cat": "أطراف العقد",
     "tip": "النبر على المقطع الثاني: im-PLOY-er. لا تنطقها «إمبلوير» بنبرٍ على الأول."},

    {"en": "Contractor", "ipa": "/kənˈtræktər/", "syllables": "kun-TRAK-tur",
     "ar": "المقاول",
     "def_ar": "الطرف الذي يتعهد بتنفيذ الأعمال وإكمالها وإصلاح أي عيوب فيها مقابل قيمة العقد.",
     "ex_en": "The Contractor shall execute the Works in accordance with the Contract and with the Engineer's instructions.",
     "ex_ar": "ينفّذ المقاولُ الأعمالَ وفقاً للعقد ولتعليمات المهندس.",
     "collocations": ["Contractor's Documents", "Contractor's Equipment", "main contractor"],
     "cat": "أطراف العقد",
     "tip": "النبر على TRAK وليس على CON. قارن: CON-tract (اسم: عقد) مقابل con-TRACT-or (مقاول)."},

    {"en": "Subcontractor", "ipa": "/ˌsʌbˈkɒntræktər/", "syllables": "sub-KON-trak-tur",
     "ar": "مقاول الباطن",
     "def_ar": "شخص أو شركة يتعاقد معها المقاول الرئيسي لتنفيذ جزء من الأعمال. يبقى المقاول الرئيسي مسؤولاً عن أعماله أمام صاحب العمل.",
     "ex_en": "The Contractor shall be responsible for the acts or defaults of any Subcontractor as if they were the acts or defaults of the Contractor.",
     "ex_ar": "يكون المقاول مسؤولاً عن أفعال أو تقصير أي مقاول باطن كما لو كانت أفعاله أو تقصيره هو.",
     "collocations": ["nominated Subcontractor", "domestic subcontractor", "subcontract works"],
     "cat": "أطراف العقد"},

    {"en": "Engineer", "ipa": "/ˌendʒɪˈnɪər/", "syllables": "en-ji-NEER",
     "ar": "المهندس (الاستشاري)",
     "def_ar": "في الكتاب الأحمر للفيديك: الشخص المعيَّن من صاحب العمل لإدارة العقد، يصدر التعليمات والشهادات ويجري «التقديرات» (Determinations).",
     "ex_en": "The Engineer may issue to the Contractor instructions which may be necessary for the execution of the Works.",
     "ex_ar": "يجوز للمهندس أن يصدر للمقاول التعليمات اللازمة لتنفيذ الأعمال.",
     "collocations": ["the Engineer's instruction", "the Engineer's determination", "Engineer's Representative"],
     "cat": "أطراف العقد",
     "tip": "النبر على المقطع الأخير NEER — من الأخطاء الشائعة نبر الأول."},

    {"en": "Party / Parties", "ipa": "/ˈpɑːti/", "syllables": "PAR-tee",
     "ar": "طرف / أطراف (العقد)",
     "def_ar": "أحد طرفي العقد (صاحب العمل أو المقاول). كلمة Parties بحرف كبير تعني طرفي العقد تحديداً.",
     "ex_en": "Each Party shall keep confidential all documents provided by the other Party.",
     "ex_ar": "يحافظ كل طرف على سرية جميع المستندات المقدَّمة من الطرف الآخر.",
     "collocations": ["third party", "the Parties agree", "either Party"],
     "cat": "أطراف العقد",
     "tip": "حرف P انفجاري مهموس — لا تنطقه B. تدرّب: Party وليس Barty."},

    {"en": "DAAB (Dispute Avoidance/Adjudication Board)", "ipa": "/dɑːb/", "syllables": "DAAB",
     "ar": "مجلس تجنّب وفضّ المنازعات",
     "def_ar": "هيئة محايدة (عضو أو ثلاثة) تُعيَّن في عقود فيديك 2017 لتجنّب المنازعات والفصل فيها قبل اللجوء إلى التحكيم.",
     "ex_en": "Either Party may refer a Dispute to the DAAB for its decision.",
     "ex_ar": "يجوز لأي من الطرفين إحالة النزاع إلى مجلس فضّ المنازعات لإصدار قراره.",
     "collocations": ["refer a dispute to the DAAB", "DAAB's decision", "standing DAAB"],
     "cat": "أطراف العقد"},

    {"en": "Assignment", "ipa": "/əˈsaɪnmənt/", "syllables": "uh-SINE-munt",
     "ar": "التنازل / حوالة الحق",
     "def_ar": "نقل طرفٍ حقوقَه أو التزاماته في العقد إلى غيره. غالباً لا يجوز إلا بموافقة الطرف الآخر.",
     "ex_en": "Neither Party shall assign the whole or any part of the Contract without the prior agreement of the other Party.",
     "ex_ar": "لا يجوز لأي طرف التنازل عن العقد كلياً أو جزئياً دون موافقة مسبقة من الطرف الآخر.",
     "collocations": ["assign the contract", "assignment of rights", "prior written consent"],
     "cat": "أطراف العقد",
     "tip": "حرف g لا يُنطق: uh-SINE-ment وليس «أسيجنمنت»."},

    # ══ 2. وثائق العقد ══════════════════════════════════════════════════════
    {"en": "Letter of Acceptance", "ipa": "/ˈletər əv əkˈseptəns/", "syllables": "LET-ter ov ak-SEP-tans",
     "ar": "خطاب القبول / خطاب الترسية",
     "def_ar": "الخطاب الرسمي الذي يقبل به صاحبُ العمل عرضَ المقاول، وبه ينعقد العقد عادةً.",
     "ex_en": "The Contract shall come into full force and effect on the date of the Letter of Acceptance.",
     "ex_ar": "يدخل العقد حيّز النفاذ الكامل اعتباراً من تاريخ خطاب القبول.",
     "collocations": ["issue the Letter of Acceptance", "date of the Letter of Acceptance"],
     "cat": "وثائق العقد"},

    {"en": "Particular Conditions", "ipa": "/pəˈtɪkjʊlə kənˈdɪʃənz/", "syllables": "pur-TIK-yu-lur kun-DI-shunz",
     "ar": "الشروط الخاصة",
     "def_ar": "الشروط التي تعدّل أو تكمّل الشروط العامة لتناسب المشروع المحدد. لها أولوية على الشروط العامة عند التعارض.",
     "ex_en": "The Particular Conditions shall take precedence over the General Conditions in case of any conflict.",
     "ex_ar": "تكون للشروط الخاصة الأولوية على الشروط العامة في حال وجود أي تعارض.",
     "collocations": ["General Conditions", "take precedence over", "order of priority"],
     "cat": "وثائق العقد"},

    {"en": "Specification", "ipa": "/ˌspesɪfɪˈkeɪʃən/", "syllables": "spes-i-fi-KAY-shun",
     "ar": "المواصفات",
     "def_ar": "الوثيقة التي تحدد المتطلبات الفنية للأعمال: المواد، الجودة، طرق التنفيذ، والاختبارات.",
     "ex_en": "The Plant and Materials shall comply with the Specification and the applicable standards.",
     "ex_ar": "تكون التجهيزات والمواد مطابقةً للمواصفات والمعايير المعمول بها.",
     "collocations": ["comply with the Specification", "technical specification", "as specified"],
     "cat": "وثائق العقد",
     "tip": "النبر على KAY. لاحظ تتابع المقاطع — كلمة من 5 مقاطع."},

    {"en": "Bill of Quantities (BOQ)", "ipa": "/bɪl əv ˈkwɒntɪtiz/", "syllables": "BILL ov KWON-ti-teez",
     "ar": "جدول الكميات",
     "def_ar": "وثيقة تُفصّل بنود الأعمال وكمياتها وأسعار وحداتها، وتُستخدم أساساً للقياس والدفع في عقود إعادة القياس.",
     "ex_en": "The quantities set out in the Bill of Quantities are estimated quantities and shall not be taken as the actual quantities.",
     "ex_ar": "الكميات الواردة في جدول الكميات كميات تقديرية ولا تُعتبر الكميات الفعلية.",
     "collocations": ["priced Bill of Quantities", "remeasurement", "unit rates"],
     "cat": "وثائق العقد"},

    {"en": "Performance Security", "ipa": "/pəˈfɔːməns sɪˈkjʊərɪti/", "syllables": "pur-FOR-muns si-KYOOR-i-tee",
     "ar": "ضمان حسن التنفيذ / الضمان النهائي",
     "def_ar": "ضمان (غالباً خطاب ضمان بنكي) يقدمه المقاول لضمان وفائه بالتزاماته التعاقدية.",
     "ex_en": "The Contractor shall obtain a Performance Security for proper performance, in the amount stated in the Contract Data.",
     "ex_ar": "يستصدر المقاول ضمانَ حسن تنفيذ بالمبلغ المحدد في بيانات العقد ضماناً للأداء السليم.",
     "collocations": ["provide a Performance Security", "call/claim under the security", "bank guarantee"],
     "cat": "وثائق العقد"},

    {"en": "Tender", "ipa": "/ˈtendər/", "syllables": "TEN-der",
     "ar": "العطاء / العرض",
     "def_ar": "العرض المقدَّم من المقاول لتنفيذ الأعمال بسعرٍ معيّن، ويشمل خطاب العطاء وكل الوثائق المرفقة به.",
     "ex_en": "The Contractor shall be deemed to have based the Tender on the data made available by the Employer.",
     "ex_ar": "يُعتبر المقاول قد بنى عطاءه على البيانات التي أتاحها صاحب العمل.",
     "collocations": ["submit a tender", "invitation to tender", "tender documents", "Letter of Tender"],
     "cat": "وثائق العقد"},

    {"en": "Drawings", "ipa": "/ˈdrɔːɪŋz/", "syllables": "DRAW-ingz",
     "ar": "المخططات / الرسومات",
     "def_ar": "الرسومات الهندسية للأعمال كما هي مدرجة في العقد، وأي رسومات معدَّلة أو إضافية يصدرها صاحب العمل أو المهندس.",
     "ex_en": "The Contractor shall give notice to the Engineer whenever the Works are likely to be delayed unless a necessary drawing is issued within a reasonable time.",
     "ex_ar": "يُخطر المقاولُ المهندسَ كلما كان من المحتمل تأخر الأعمال ما لم يصدر المخطط اللازم خلال وقت معقول.",
     "collocations": ["issue drawings", "shop drawings", "as-built drawings"],
     "cat": "وثائق العقد",
     "tip": "لا تنطق حرف w الثانية بقوة: DRAW-ings وليس «دراوينجز» بواوٍ ثقيلة."},

    # ══ 3. الوقت والبرنامج ══════════════════════════════════════════════════
    {"en": "Commencement Date", "ipa": "/kəˈmensmənt deɪt/", "syllables": "ku-MENS-munt DAYT",
     "ar": "تاريخ المباشرة / بدء الأعمال",
     "def_ar": "التاريخ الذي يجب أن يبدأ فيه المقاول تنفيذ الأعمال، ومنه تُحسب مدة الإنجاز.",
     "ex_en": "The Engineer shall give the Contractor not less than 14 days' notice of the Commencement Date.",
     "ex_ar": "يوجّه المهندس للمقاول إشعاراً بتاريخ المباشرة قبل حلوله بما لا يقل عن 14 يوماً.",
     "collocations": ["notice of the Commencement Date", "commence the Works"],
     "cat": "الوقت والبرنامج"},

    {"en": "Time for Completion", "ipa": "/taɪm fə kəmˈpliːʃən/", "syllables": "TIME fur kum-PLEE-shun",
     "ar": "مدة الإنجاز",
     "def_ar": "المدة المحددة في العقد لإكمال الأعمال (أو أي قسم منها) محسوبةً من تاريخ المباشرة، شاملةً أي تمديد ممنوح.",
     "ex_en": "The Contractor shall complete the whole of the Works within the Time for Completion.",
     "ex_ar": "ينجز المقاول كامل الأعمال خلال مدة الإنجاز.",
     "collocations": ["extension of the Time for Completion", "within the Time for Completion"],
     "cat": "الوقت والبرنامج"},

    {"en": "Extension of Time (EOT)", "ipa": "/ɪkˈstenʃən əv taɪm/", "syllables": "ik-STEN-shun ov TIME",
     "ar": "تمديد مدة الإنجاز",
     "def_ar": "حق المقاول في إطالة مدة الإنجاز عند حدوث تأخير بسبب لا يتحمّله، مثل التغييرات أو تأخر صاحب العمل أو الظروف الاستثنائية.",
     "ex_en": "The Contractor shall be entitled to an Extension of Time if completion is or will be delayed by a Variation.",
     "ex_ar": "يستحق المقاول تمديداً لمدة الإنجاز إذا تأخر الإنجاز أو كان سيتأخر بسبب تغيير.",
     "collocations": ["claim an EOT", "grant an extension", "entitlement to EOT"],
     "cat": "الوقت والبرنامج",
     "tip": "Extension تبدأ بـ /ɪk/ وليس /e/: ik-STEN-shun."},

    {"en": "Programme", "ipa": "/ˈprəʊɡræm/", "syllables": "PROH-gram",
     "ar": "البرنامج الزمني",
     "def_ar": "الجدول الزمني التفصيلي الذي يقدمه المقاول مبيّناً تسلسل وتوقيت تنفيذ الأعمال. (الإملاء البريطاني: programme، الأمريكي: schedule).",
     "ex_en": "The Contractor shall submit an initial programme for the execution of the Works within 28 days after the Commencement Date.",
     "ex_ar": "يقدّم المقاول برنامجاً زمنياً أولياً لتنفيذ الأعمال خلال 28 يوماً من تاريخ المباشرة.",
     "collocations": ["submit a programme", "revised programme", "baseline programme"],
     "cat": "الوقت والبرنامج"},

    {"en": "Delay", "ipa": "/dɪˈleɪ/", "syllables": "di-LAY",
     "ar": "تأخير",
     "def_ar": "تجاوز الوقت المخطط له. يُصنَّف إلى تأخير يستحق تعويضاً (Compensable)، أو تمديداً فقط (Excusable)، أو لا شيء (Culpable: بسبب المقاول).",
     "ex_en": "If the Contractor suffers delay due to an act of prevention by the Employer, the Contractor shall be entitled to an extension of time.",
     "ex_ar": "إذا لحق بالمقاول تأخير بسبب فعلٍ معوِّق من صاحب العمل، استحق المقاول تمديداً للمدة.",
     "collocations": ["delay damages", "critical delay", "concurrent delay", "delay analysis"],
     "cat": "الوقت والبرنامج",
     "tip": "النبر على LAY. وانتبه: delay (تأخير) ≠ daily (يومي)."},

    {"en": "Taking-Over Certificate", "ipa": "/ˈteɪkɪŋ ˈəʊvə səˈtɪfɪkət/", "syllables": "TAY-king OH-vur sur-TIF-i-kut",
     "ar": "شهادة التسلّم / الاستلام الابتدائي",
     "def_ar": "الشهادة التي يصدرها المهندس عند إكمال الأعمال جوهرياً واجتيازها اختبارات الإكمال، وبها تنتقل عهدة الأعمال إلى صاحب العمل.",
     "ex_en": "The Works shall be taken over by the Employer when a Taking-Over Certificate has been issued.",
     "ex_ar": "يتسلّم صاحبُ العمل الأعمالَ عند صدور شهادة التسلّم.",
     "collocations": ["issue the Taking-Over Certificate", "apply for taking over", "substantially complete"],
     "cat": "الوقت والبرنامج",
     "tip": "Certificate: النبر على TIF — sur-TIF-i-kut، والحرف الأخير مخفّف /kət/."},

    {"en": "Defects Notification Period (DNP)", "ipa": "/ˈdiːfekts ˌnəʊtɪfɪˈkeɪʃən ˈpɪəriəd/", "syllables": "DEE-fekts no-ti-fi-KAY-shun PEER-ee-ud",
     "ar": "فترة الإخطار بالعيوب / فترة الضمان",
     "def_ar": "الفترة التالية للتسلّم التي يجوز خلالها لصاحب العمل الإخطار بأي عيوب ليصلحها المقاول على نفقته (تقابل فترة الصيانة في الأنظمة العربية).",
     "ex_en": "The Contractor shall remedy any defect notified by the Employer during the Defects Notification Period.",
     "ex_ar": "يصلح المقاول أيَّ عيبٍ يُخطره به صاحبُ العمل خلال فترة الإخطار بالعيوب.",
     "collocations": ["expiry of the DNP", "remedy defects", "extension of the DNP"],
     "cat": "الوقت والبرنامج"},

    {"en": "Suspension", "ipa": "/səˈspenʃən/", "syllables": "su-SPEN-shun",
     "ar": "تعليق / إيقاف الأعمال",
     "def_ar": "إيقاف مؤقت لتنفيذ الأعمال كلها أو بعضها بتعليمات من المهندس أو بحق المقاول عند عدم الدفع.",
     "ex_en": "The Engineer may at any time instruct the Contractor to suspend progress of part or all of the Works.",
     "ex_ar": "يجوز للمهندس في أي وقت أن يأمر المقاول بتعليق سير الأعمال كلها أو جزء منها.",
     "collocations": ["suspend the Works", "suspension of work", "resume work"],
     "cat": "الوقت والبرنامج"},

    {"en": "Critical Path", "ipa": "/ˈkrɪtɪkəl pɑːθ/", "syllables": "KRIT-i-kul PAATH",
     "ar": "المسار الحرج",
     "def_ar": "سلسلة الأنشطة المتتابعة الأطول في البرنامج الزمني؛ أي تأخير فيها يؤخر إنجاز المشروع كله.",
     "ex_en": "Only delays to activities on the critical path will entitle the Contractor to an extension of time.",
     "ex_ar": "لا يستحق المقاول تمديداً للمدة إلا عن التأخيرات التي تصيب أنشطة المسار الحرج.",
     "collocations": ["critical path method (CPM)", "float", "critical activity"],
     "cat": "الوقت والبرنامج",
     "tip": "‏th في path مهموسة /θ/ كالثاء العربية: «باث» بثاء، وليس «بات»."},

    # ══ 4. الدفع والمال ═════════════════════════════════════════════════════
    {"en": "Contract Price", "ipa": "/ˈkɒntrækt praɪs/", "syllables": "KON-trakt PRICE",
     "ar": "قيمة العقد",
     "def_ar": "المبلغ المتفق عليه مقابل تنفيذ الأعمال، ويشمل التعديلات التي تطرأ وفقاً للعقد.",
     "ex_en": "The Contract Price shall be agreed or determined under Sub-Clause 12.3 and be subject to adjustments in accordance with the Contract.",
     "ex_ar": "تُتَّفق قيمة العقد أو تُقدَّر بموجب البند الفرعي 12.3 وتخضع للتعديلات وفقاً للعقد.",
     "collocations": ["adjustment to the Contract Price", "lump sum price", "accepted contract amount"],
     "cat": "الدفع والمال",
     "tip": "Contract اسمٌ هنا فالنبر على الأول: KON-trakt."},

    {"en": "Advance Payment", "ipa": "/ədˈvɑːns ˈpeɪmənt/", "syllables": "ud-VAANS PAY-munt",
     "ar": "الدفعة المقدّمة",
     "def_ar": "مبلغ يدفعه صاحب العمل للمقاول قبل بدء الأعمال (قرض بدون فائدة للتعبئة) ويُستردّ بالخصم من المستخلصات.",
     "ex_en": "The advance payment shall be repaid through percentage deductions from the interim payments.",
     "ex_ar": "تُستردّ الدفعة المقدمة عبر استقطاعات نسبية من الدفعات المرحلية.",
     "collocations": ["advance payment guarantee", "repayment of the advance", "mobilisation"],
     "cat": "الدفع والمال"},

    {"en": "Interim Payment Certificate (IPC)", "ipa": "/ˈɪntərɪm ˈpeɪmənt səˈtɪfɪkət/", "syllables": "IN-tur-im PAY-munt sur-TIF-i-kut",
     "ar": "شهادة الدفع المرحلية / المستخلص",
     "def_ar": "الشهادة الدورية (شهرية غالباً) التي يصدرها المهندس محدداً المبلغ المستحق للمقاول عن الأعمال المنفَّذة.",
     "ex_en": "The Engineer shall issue an Interim Payment Certificate within 28 days after receiving the Contractor's Statement.",
     "ex_ar": "يُصدر المهندس شهادة دفع مرحلية خلال 28 يوماً من تسلّم كشف المقاول.",
     "collocations": ["issue an IPC", "certified amount", "payment application/statement"],
     "cat": "الدفع والمال"},

    {"en": "Retention Money", "ipa": "/rɪˈtenʃən ˈmʌni/", "syllables": "ri-TEN-shun MUN-ee",
     "ar": "المبالغ المحتجزة / محتجز الضمان",
     "def_ar": "نسبة (5–10٪ عادة) تُخصم من كل مستخلص وتُحتجز ضماناً لإصلاح العيوب، وتُردّ نصفين: عند التسلّم وعند انتهاء فترة الضمان.",
     "ex_en": "The first half of the Retention Money shall be certified for payment when the Taking-Over Certificate has been issued.",
     "ex_ar": "يُعتمد صرف النصف الأول من المبالغ المحتجزة عند صدور شهادة التسلّم.",
     "collocations": ["release of retention", "retention percentage", "retention bond"],
     "cat": "الدفع والمال"},

    {"en": "Provisional Sum", "ipa": "/prəˈvɪʒənəl sʌm/", "syllables": "pruh-VIZH-un-ul SUM",
     "ar": "المبلغ الاحتياطي / الاعتمادي",
     "def_ar": "مبلغ مُدرج في العقد لأعمال أو مواد غير محددة بدقة عند التعاقد، ولا يُصرف إلا بتعليمات المهندس وبالقدر المنفَّذ فعلاً.",
     "ex_en": "Each Provisional Sum shall only be used, in whole or in part, in accordance with the Engineer's instructions.",
     "ex_ar": "لا يُستخدم أي مبلغ احتياطي، كلياً أو جزئياً، إلا وفقاً لتعليمات المهندس.",
     "collocations": ["expend a provisional sum", "prime cost sum"],
     "cat": "الدفع والمال"},

    {"en": "Final Statement", "ipa": "/ˈfaɪnəl ˈsteɪtmənt/", "syllables": "FY-nul STAYT-munt",
     "ar": "الكشف النهائي / المستخلص الختامي",
     "def_ar": "الكشف الذي يقدمه المقاول بعد انتهاء فترة الضمان مبيّناً كل المبالغ التي يعتبرها مستحقة له نهائياً بموجب العقد.",
     "ex_en": "Within 56 days after receiving the Performance Certificate, the Contractor shall submit the draft final statement.",
     "ex_ar": "يقدّم المقاول مسوّدة الكشف النهائي خلال 56 يوماً من تسلّمه شهادة الأداء.",
     "collocations": ["draft final statement", "final payment certificate", "discharge"],
     "cat": "الدفع والمال"},

    {"en": "Financing Charges", "ipa": "/ˈfaɪnænsɪŋ ˈtʃɑːdʒɪz/", "syllables": "FY-nan-sing CHAR-jiz",
     "ar": "أعباء / فوائد التمويل",
     "def_ar": "الفوائد المستحقة للمقاول عن تأخر صاحب العمل في سداد المبالغ المعتمدة (تُحسب شهرياً بمعدل مركّب في الفيديك).",
     "ex_en": "The Contractor shall be entitled to financing charges compounded monthly on the amount unpaid during the period of delay.",
     "ex_ar": "يستحق المقاول أعباء تمويل مركّبة شهرياً على المبلغ غير المسدَّد طوال فترة التأخير.",
     "collocations": ["delayed payment", "compounded monthly", "interest on late payment"],
     "cat": "الدفع والمال"},

    # ══ 5. التغييرات والمطالبات ═════════════════════════════════════════════
    {"en": "Variation", "ipa": "/ˌveəriˈeɪʃən/", "syllables": "vair-ee-AY-shun",
     "ar": "تغيير / أمر تغييري",
     "def_ar": "أي تعديل على الأعمال (زيادة، حذف، تغيير نوعية أو تسلسل) يصدر به أمر أو موافقة وفقاً لبند التغييرات.",
     "ex_en": "Variations may be initiated by the Engineer at any time prior to the issue of the Taking-Over Certificate.",
     "ex_ar": "يجوز للمهندس استحداث التغييرات في أي وقت قبل صدور شهادة التسلّم.",
     "collocations": ["Variation Order (VO)", "instruct a Variation", "valuation of variations"],
     "cat": "التغييرات والمطالبات",
     "tip": "حرف V بإطباق الشفة على الأسنان — لا تنطقه F: Variation وليس Fariation."},

    {"en": "Claim", "ipa": "/kleɪm/", "syllables": "KLAYM",
     "ar": "مطالبة",
     "def_ar": "طلب أحد الطرفين استحقاقاً بموجب العقد: مالاً إضافياً، أو تمديداً للمدة، أو غير ذلك، وفق إجراءات وإخطارات محددة.",
     "ex_en": "If the Contractor considers himself entitled to additional payment, the Contractor shall give a Notice of Claim to the Engineer.",
     "ex_ar": "إذا رأى المقاول أنه يستحق مبالغ إضافية، وجّه إشعارَ مطالبةٍ إلى المهندس.",
     "collocations": ["submit/lodge a claim", "Notice of Claim", "fully detailed claim", "time-barred"],
     "cat": "التغييرات والمطالبات"},

    {"en": "Notice", "ipa": "/ˈnəʊtɪs/", "syllables": "NOH-tis",
     "ar": "إشعار / إخطار",
     "def_ar": "بلاغ كتابي رسمي يقتضيه العقد. كثير من الحقوق تسقط إذا لم يُرسل الإشعار خلال المهلة المحددة (شرط الإسقاط).",
     "ex_en": "The Contractor shall give a Notice to the Engineer no later than 28 days after the Contractor became aware of the event.",
     "ex_ar": "يوجّه المقاول إشعاراً إلى المهندس في موعد أقصاه 28 يوماً من علمه بالحدث.",
     "collocations": ["give notice", "notice period", "condition precedent", "written notice"],
     "cat": "التغييرات والمطالبات",
     "tip": "‏NOH-tis بصوت /əʊ/ — وليس «نوتيس» بواو قصيرة."},

    {"en": "Determination", "ipa": "/dɪˌtɜːmɪˈneɪʃən/", "syllables": "di-tur-mi-NAY-shun",
     "ar": "تقدير / قرار (المهندس)",
     "def_ar": "قرار المهندس «المنصف» في مسألة متنازع عليها بعد فشل التشاور للاتفاق، ويكون ملزماً مؤقتاً حتى يُراجع ودياً أو بالتحكيم.",
     "ex_en": "The Engineer shall make a fair determination of the matter, in accordance with the Contract, taking due regard of all relevant circumstances.",
     "ex_ar": "يُصدر المهندس تقديراً منصفاً للمسألة وفقاً للعقد، مراعياً جميع الظروف ذات الصلة.",
     "collocations": ["fair determination", "agreement or determination", "consultation"],
     "cat": "التغييرات والمطالبات"},

    {"en": "Particulars", "ipa": "/pəˈtɪkjʊləz/", "syllables": "pur-TIK-yu-lurz",
     "ar": "التفاصيل المؤيِّدة (للمطالبة)",
     "def_ar": "البيانات والمستندات التفصيلية التي تُثبت أساس المطالبة ومقدارها (السجلات المعاصرة، التحليلات، الحسابات).",
     "ex_en": "The Contractor shall submit full supporting particulars of the basis of the Claim and of the additional payment claimed.",
     "ex_ar": "يقدّم المقاول التفاصيل المؤيِّدة الكاملة لأساس المطالبة وللمبلغ الإضافي المُطالَب به.",
     "collocations": ["supporting particulars", "contemporary records", "substantiation"],
     "cat": "التغييرات والمطالبات"},

    {"en": "Omission", "ipa": "/əˈmɪʃən/", "syllables": "oh-MISH-un",
     "ar": "حذف (من نطاق الأعمال)",
     "def_ar": "إلغاء جزء من الأعمال بأمر تغييري. لا يجوز حذف عمل لإسناده إلى مقاول آخر إلا باتفاق.",
     "ex_en": "Each Variation may include omission of any work unless it is to be carried out by others.",
     "ex_ar": "يجوز أن يشمل أي تغييرٍ حذفَ أي عملٍ ما لم يكن سيُنفَّذ بواسطة آخرين.",
     "collocations": ["omission of work", "descope", "omit from the scope"],
     "cat": "التغييرات والمطالبات"},

    {"en": "Unforeseeable", "ipa": "/ˌʌnfɔːˈsiːəbəl/", "syllables": "un-for-SEE-uh-bul",
     "ar": "غير قابل للتوقُّع",
     "def_ar": "ما لا يمكن لمقاولٍ متمرّس توقُّعه بصورة معقولة عند تقديم العطاء — معيار أساسي في مطالبات الظروف الفيزيائية.",
     "ex_en": "If the Contractor encounters physical conditions which were Unforeseeable, the Contractor shall give a Notice to the Engineer.",
     "ex_ar": "إذا صادف المقاول ظروفاً فيزيائية غير قابلة للتوقع، وجّه إشعاراً إلى المهندس.",
     "collocations": ["Unforeseeable physical conditions", "experienced contractor", "reasonably foreseeable"],
     "cat": "التغييرات والمطالبات"},

    # ══ 6. المخاطر والمسؤولية ═══════════════════════════════════════════════
    {"en": "Liquidated Damages", "ipa": "/ˈlɪkwɪdeɪtɪd ˈdæmɪdʒɪz/", "syllables": "LIK-wi-day-tid DAM-i-jiz",
     "ar": "التعويضات الاتفاقية / غرامة التأخير",
     "def_ar": "مبلغ محدد سلفاً في العقد يُدفع عن كل يوم تأخير، بدلاً من إثبات الضرر الفعلي. في الفيديك تسمى Delay Damages.",
     "ex_en": "The Contractor shall pay delay damages to the Employer for every day which shall elapse between the Time for Completion and the date of taking over.",
     "ex_ar": "يدفع المقاول لصاحب العمل تعويضات تأخير عن كل يوم ينقضي بين مدة الإنجاز وتاريخ التسلّم.",
     "collocations": ["delay damages", "cap on liquidated damages", "penalty clause", "genuine pre-estimate"],
     "cat": "المخاطر والمسؤولية",
     "tip": "‏Damages بالجمع = تعويضات (مصطلح قانوني). Damage بالمفرد = ضرر مادي."},

    {"en": "Indemnify", "ipa": "/ɪnˈdemnɪfaɪ/", "syllables": "in-DEM-ni-fy",
     "ar": "يعوّض / يُبرئ من المسؤولية",
     "def_ar": "يلتزم بحماية الطرف الآخر من الخسائر والمطالبات والدعاوى الناشئة عن أمر معيّن وتحمّلها عنه.",
     "ex_en": "The Contractor shall indemnify and hold harmless the Employer against all claims arising out of the Contractor's negligence.",
     "ex_ar": "يعوّض المقاولُ صاحبَ العمل ويُبرئه من جميع المطالبات الناشئة عن إهمال المقاول.",
     "collocations": ["indemnify and hold harmless", "indemnity clause", "mutual indemnities"],
     "cat": "المخاطر والمسؤولية",
     "tip": "النبر على DEM. ولاحظ الثلاثي الشهير: indemnify / indemnity / indemnification."},

    {"en": "Force Majeure / Exceptional Events", "ipa": "/ˌfɔːs mæˈʒɜːr/", "syllables": "FORS ma-ZHUR",
     "ar": "القوة القاهرة / الأحداث الاستثنائية",
     "def_ar": "حدث خارج عن سيطرة الطرف، لم يكن بوسعه توقّعه أو تجنّبه، يمنعه من أداء التزاماته (حرب، كوارث طبيعية...). فيديك 2017 تسميها Exceptional Events.",
     "ex_en": "If a Party is prevented from performing its obligations by Force Majeure, it shall give notice within 14 days after becoming aware of the event.",
     "ex_ar": "إذا مُنع أحد الطرفين من أداء التزاماته بسبب قوة قاهرة، وجّه إشعاراً خلال 14 يوماً من علمه بالحدث.",
     "collocations": ["force majeure event", "prevented from performing", "beyond a Party's control"],
     "cat": "المخاطر والمسؤولية",
     "tip": "مصطلح فرنسي الأصل: «فورس ماجور» بجيم معطّشة /ʒ/ كالجيم الشامية."},

    {"en": "Liability", "ipa": "/ˌlaɪəˈbɪlɪti/", "syllables": "ly-uh-BIL-i-tee",
     "ar": "مسؤولية (قانونية)",
     "def_ar": "الالتزام القانوني بتحمّل تبعات فعلٍ أو إخلال. تُحدَّد في العقود حدودها القصوى واستثناءاتها.",
     "ex_en": "The total liability of the Contractor to the Employer shall not exceed the sum stated in the Contract Data.",
     "ex_ar": "لا يتجاوز إجماليُّ مسؤولية المقاول تجاه صاحب العمل المبلغَ المحدد في بيانات العقد.",
     "collocations": ["limitation of liability", "joint and several liability", "exclude liability"],
     "cat": "المخاطر والمسؤولية",
     "tip": "خمسة مقاطع والنبر على BIL: ly-uh-BIL-i-tee."},

    {"en": "Consequential Loss", "ipa": "/ˌkɒnsɪˈkwenʃəl lɒs/", "syllables": "kon-si-KWEN-shul LOSS",
     "ar": "الخسارة التبعية / غير المباشرة",
     "def_ar": "خسائر لا تنشأ مباشرة من الإخلال بل تبعاً له، كفوات الربح وفقدان العقود. تُستبعد عادة من المسؤولية إلا في حالات محددة.",
     "ex_en": "Neither Party shall be liable to the other for loss of profit or for any indirect or consequential loss.",
     "ex_ar": "لا يكون أي من الطرفين مسؤولاً تجاه الآخر عن فوات الربح أو أي خسارة غير مباشرة أو تبعية.",
     "collocations": ["indirect loss", "loss of profit", "exclusion clause"],
     "cat": "المخاطر والمسؤولية"},

    {"en": "Negligence", "ipa": "/ˈneɡlɪdʒəns/", "syllables": "NEG-li-juns",
     "ar": "إهمال / تقصير",
     "def_ar": "الإخلال بواجب بذل العناية المعقولة. «الإهمال الجسيم» (gross negligence) درجة أشد تُسقط غالباً حدود المسؤولية.",
     "ex_en": "The limitation of liability shall not apply in cases of fraud, gross negligence or deliberate default.",
     "ex_ar": "لا يسري حدُّ المسؤولية في حالات الغش أو الإهمال الجسيم أو التقصير المتعمَّد.",
     "collocations": ["gross negligence", "negligent act or omission", "duty of care"],
     "cat": "المخاطر والمسؤولية",
     "tip": "النبر على الأول NEG، والجيم معطّشة /dʒ/."},

    {"en": "Insurance", "ipa": "/ɪnˈʃʊərəns/", "syllables": "in-SHOOR-uns",
     "ar": "تأمين",
     "def_ar": "تغطية المخاطر لدى شركة تأمين. تشترط العقود تأمين الأعمال والمعدات والمسؤولية تجاه الغير وإصابات العمال.",
     "ex_en": "The insuring Party shall maintain the insurances in full force and effect during the period of the Contract.",
     "ex_ar": "يحافظ الطرفُ الملتزم بالتأمين على سريان وثائق التأمين بكامل قوتها طوال مدة العقد.",
     "collocations": ["all-risks insurance (CAR)", "third party liability insurance", "policy / premium / deductible"],
     "cat": "المخاطر والمسؤولية",
     "tip": "النبر على SHOOR وليس على IN — خطأ شائع جداً عند العرب."},

    # ══ 7. الجودة والعيوب ═══════════════════════════════════════════════════
    {"en": "Defect", "ipa": "/ˈdiːfekt/", "syllables": "DEE-fekt",
     "ar": "عيب",
     "def_ar": "قصور في الأعمال يجعلها مخالفة للعقد: في المواد أو المصنعية أو التصميم (إن كان من مسؤولية المقاول).",
     "ex_en": "The Contractor shall, at his own cost, remedy any defect or damage notified during the Defects Notification Period.",
     "ex_ar": "يصلح المقاول على نفقته الخاصة أيَّ عيب أو ضرر يُخطَر به خلال فترة الإخطار بالعيوب.",
     "collocations": ["latent defect", "patent defect", "remedy/rectify a defect", "defective work"],
     "cat": "الجودة والعيوب",
     "tip": "الاسم DEE-fekt بنبرٍ على الأول. الفعل de-FECT (ينشقّ) بنبر على الثاني — معنى مختلف تماماً!"},

    {"en": "Tests on Completion", "ipa": "/tests ɒn kəmˈpliːʃən/", "syllables": "TESTS on kum-PLEE-shun",
     "ar": "اختبارات الإكمال / التشغيل",
     "def_ar": "الاختبارات المنصوص عليها في العقد والتي يجب اجتيازها قبل تسلّم الأعمال.",
     "ex_en": "The Contractor shall give notice of the date after which the Contractor will be ready to carry out the Tests on Completion.",
     "ex_ar": "يُخطر المقاول بالتاريخ الذي سيكون بعده مستعداً لإجراء اختبارات الإكمال.",
     "collocations": ["pass the tests", "retesting", "failure to pass"],
     "cat": "الجودة والعيوب"},

    {"en": "Workmanship", "ipa": "/ˈwɜːkmənʃɪp/", "syllables": "WURK-mun-ship",
     "ar": "المصنعية / جودة التنفيذ",
     "def_ar": "مستوى المهارة والإتقان في تنفيذ الأعمال. تشترط العقود مصنعية بمستوى أصول الصنعة (good workmanship).",
     "ex_en": "All materials and workmanship shall be of the respective kinds described in the Contract and in accordance with good practice.",
     "ex_ar": "تكون جميع المواد والمصنعية من الأنواع الموصوفة في العقد ووفقاً لأصول الصنعة.",
     "collocations": ["good workmanship", "proper and workmanlike manner", "materials and workmanship"],
     "cat": "الجودة والعيوب"},

    {"en": "Plant", "ipa": "/plɑːnt/", "syllables": "PLAANT",
     "ar": "التجهيزات الآلية (الدائمة)",
     "def_ar": "في الفيديك: الأجهزة والمعدات التي ستصبح جزءاً دائماً من الأعمال (مضخات، مصاعد، محولات) — وليست «نباتاً» ولا «مصنعاً»!",
     "ex_en": "Plant and Materials shall become the property of the Employer when delivered to the Site.",
     "ex_ar": "تؤول ملكية التجهيزات والمواد إلى صاحب العمل عند توريدها إلى الموقع.",
     "collocations": ["Plant and Materials", "Contractor's Equipment (المعدات المؤقتة)"],
     "cat": "الجودة والعيوب",
     "tip": "فرّق بين Plant (تجهيزات دائمة) و Contractor's Equipment (معدات إنشاء مؤقتة)."},

    {"en": "Inspection", "ipa": "/ɪnˈspekʃən/", "syllables": "in-SPEK-shun",
     "ar": "فحص / معاينة",
     "def_ar": "حق المهندس وصاحب العمل في فحص الأعمال والمواد في أي وقت، دون أن يُعفي ذلك المقاولَ من التزاماته.",
     "ex_en": "The Employer's Personnel shall at all reasonable times have full access to the Site for inspection.",
     "ex_ar": "يكون لأفراد صاحب العمل في جميع الأوقات المعقولة حقُّ الوصول الكامل إلى الموقع للمعاينة.",
     "collocations": ["inspection and testing", "right to inspect", "covered up (أعمال مغطاة)"],
     "cat": "الجودة والعيوب"},

    {"en": "Rejection", "ipa": "/rɪˈdʒekʃən/", "syllables": "ri-JEK-shun",
     "ar": "رفض (الأعمال أو المواد)",
     "def_ar": "حق المهندس في رفض أي تجهيزات أو مواد أو مصنعية معيبة أو غير مطابقة للعقد، وطلب إصلاحها أو استبدالها.",
     "ex_en": "The Engineer may reject any Plant, Materials or workmanship found to be defective or otherwise not in accordance with the Contract.",
     "ex_ar": "يجوز للمهندس رفضُ أي تجهيزات أو مواد أو مصنعية يتبين أنها معيبة أو غير مطابقة للعقد.",
     "collocations": ["reject the works", "non-conformance", "remedial work"],
     "cat": "الجودة والعيوب"},

    # ══ 8. الإنهاء والإخلال ═════════════════════════════════════════════════
    {"en": "Termination", "ipa": "/ˌtɜːmɪˈneɪʃən/", "syllables": "tur-mi-NAY-shun",
     "ar": "إنهاء العقد",
     "def_ar": "إنهاء العلاقة التعاقدية قبل اكتمالها: إما لإخلال أحد الطرفين، أو «للملاءمة» بإرادة صاحب العمل المنفردة.",
     "ex_en": "The Employer shall be entitled to terminate the Contract if the Contractor abandons the Works.",
     "ex_ar": "يحق لصاحب العمل إنهاء العقد إذا هجر المقاول الأعمال.",
     "collocations": ["termination for default", "termination for convenience", "notice of termination"],
     "cat": "الإنهاء والإخلال"},

    {"en": "Breach", "ipa": "/briːtʃ/", "syllables": "BREECH",
     "ar": "إخلال / خرق (للعقد)",
     "def_ar": "عدم وفاء طرف بالتزام تعاقدي. «الإخلال الجوهري» (material breach) يخوّل الطرف الآخر إنهاء العقد والمطالبة بالتعويض.",
     "ex_en": "Termination shall be without prejudice to any other rights of the Employer arising from the Contractor's breach of Contract.",
     "ex_ar": "لا يخلّ الإنهاءُ بأي حقوق أخرى لصاحب العمل ناشئةٍ عن إخلال المقاول بالعقد.",
     "collocations": ["material/fundamental breach", "in breach of contract", "remedy the breach"],
     "cat": "الإنهاء والإخلال",
     "tip": "تُنطق بياء طويلة /iː/ وتش: «بريتش». لا تخلط بينها وبين breech أو bridge."},

    {"en": "Default", "ipa": "/dɪˈfɔːlt/", "syllables": "di-FAWLT",
     "ar": "تقصير / تخلُّف عن الوفاء",
     "def_ar": "إخفاق طرف في أداء التزاماته. «إشعار التقصير» يمنح المقصِّر مهلة للإصلاح قبل الإنهاء.",
     "ex_en": "If the Contractor fails to remedy the default within 14 days after receiving the Employer's notice, the Employer may terminate the Contract.",
     "ex_ar": "إذا لم يعالج المقاول تقصيرَه خلال 14 يوماً من تسلّم إشعار صاحب العمل، جاز لصاحب العمل إنهاء العقد.",
     "collocations": ["notice to correct", "in default", "event of default", "cure period"],
     "cat": "الإنهاء والإخلال",
     "tip": "النبر على FAWLT: di-FAWLT — وليس DEE-folt كما في لغة الحاسوب الدارجة."},

    {"en": "Insolvency", "ipa": "/ɪnˈsɒlvənsi/", "syllables": "in-SOL-vun-see",
     "ar": "إعسار / إفلاس",
     "def_ar": "عجز الطرف مالياً عن سداد ديونه أو خضوعه لإجراءات تصفية — سبب فوري لإنهاء العقد دون مهلة إصلاح.",
     "ex_en": "The Employer may terminate the Contract immediately if the Contractor becomes bankrupt or insolvent.",
     "ex_ar": "يجوز لصاحب العمل إنهاء العقد فوراً إذا أفلس المقاول أو أعسر.",
     "collocations": ["bankruptcy", "liquidation", "goes into liquidation", "receivership"],
     "cat": "الإنهاء والإخلال"},

    {"en": "Without prejudice to", "ipa": "/wɪˈðaʊt ˈpredʒʊdɪs/", "syllables": "wi-THOUT PREJ-uh-dis",
     "ar": "دون إخلال بـ / مع عدم المساس بـ",
     "def_ar": "عبارة تحفظ الحقوق الأخرى: ممارسة هذا الحق لا تُسقط ولا تمسّ بقية الحقوق.",
     "ex_en": "This right is without prejudice to any other rights the Employer may have under the Contract or otherwise.",
     "ex_ar": "هذا الحق دون إخلالٍ بأي حقوق أخرى قد تكون لصاحب العمل بموجب العقد أو غيره.",
     "collocations": ["without prejudice to any other rights", "without prejudice communications"],
     "cat": "الإنهاء والإخلال",
     "tip": "‏th في without مجهورة /ð/ كالذال العربية: «ويذاوت»."},

    # ══ 9. تسوية المنازعات ══════════════════════════════════════════════════
    {"en": "Dispute", "ipa": "/dɪˈspjuːt/", "syllables": "di-SPYOOT",
     "ar": "نزاع",
     "def_ar": "خلاف بين الطرفين حول مطالبة أو مسألة تعاقدية بعد رفضها أو تجاهلها — يدخل عندها في مسار تسوية المنازعات.",
     "ex_en": "Any Dispute which is not resolved amicably shall be finally settled by international arbitration.",
     "ex_ar": "أيُّ نزاعٍ لا يُسوَّى ودياً يُحسم نهائياً بالتحكيم الدولي.",
     "collocations": ["dispute resolution", "refer a dispute", "amicable settlement"],
     "cat": "تسوية المنازعات",
     "tip": "النبر على SPYOOT في الاسم والفعل معاً."},

    {"en": "Arbitration", "ipa": "/ˌɑːbɪˈtreɪʃən/", "syllables": "ar-bi-TRAY-shun",
     "ar": "التحكيم",
     "def_ar": "تسوية النزاع نهائياً أمام محكَّم أو هيئة تحكيم بدلاً من القضاء، بقرار «نهائي وملزم» قابل للتنفيذ دولياً (اتفاقية نيويورك).",
     "ex_en": "The dispute shall be finally settled under the Rules of Arbitration of the International Chamber of Commerce by three arbitrators.",
     "ex_ar": "يُحسم النزاع نهائياً وفق قواعد التحكيم لغرفة التجارة الدولية بواسطة ثلاثة محكَّمين.",
     "collocations": ["arbitration clause", "arbitral award", "seat of arbitration", "ICC Rules"],
     "cat": "تسوية المنازعات"},

    {"en": "Amicable Settlement", "ipa": "/ˈæmɪkəbəl ˈsetəlmənt/", "syllables": "AM-i-kuh-bul SET-ul-munt",
     "ar": "التسوية الودية",
     "def_ar": "محاولة حل النزاع بالتفاوض أو الصلح قبل التحكيم — مرحلة إلزامية في الفيديك (28 يوماً بعد إشعار عدم الرضا).",
     "ex_en": "Both Parties shall attempt to settle the dispute amicably before the commencement of arbitration.",
     "ex_ar": "يحاول الطرفان تسوية النزاع ودياً قبل بدء التحكيم.",
     "collocations": ["settle amicably", "negotiation", "good faith discussions"],
     "cat": "تسوية المنازعات",
     "tip": "النبر على AM الأولى: AM-i-kuh-bul — وليس a-MIK-able."},

    {"en": "Governing Law", "ipa": "/ˈɡʌvənɪŋ lɔː/", "syllables": "GUV-ur-ning LAW",
     "ar": "القانون الواجب التطبيق",
     "def_ar": "قانون الدولة الذي يحكم تفسير العقد وتنفيذه، ويُحدَّد صراحةً في بيانات العقد.",
     "ex_en": "The Contract shall be governed by and construed in accordance with the laws of the Kingdom of Saudi Arabia.",
     "ex_ar": "يخضع العقد لأنظمة المملكة العربية السعودية ويُفسَّر وفقاً لها.",
     "collocations": ["governed by", "construed in accordance with", "jurisdiction"],
     "cat": "تسوية المنازعات"},

    {"en": "Final and Binding", "ipa": "/ˈfaɪnəl ənd ˈbaɪndɪŋ/", "syllables": "FY-nul and BINE-ding",
     "ar": "نهائي ومُلزِم",
     "def_ar": "وصف القرار الذي لا يقبل الطعن ويجب على الطرفين تنفيذه (كحكم التحكيم، أو قرار المجلس إذا لم يُعترض عليه في المهلة).",
     "ex_en": "If no Notice of Dissatisfaction is given within 28 days, the DAAB's decision shall become final and binding upon both Parties.",
     "ex_ar": "إذا لم يُقدَّم إشعار عدم رضا خلال 28 يوماً، أصبح قرار المجلس نهائياً وملزماً للطرفين.",
     "collocations": ["binding upon the Parties", "Notice of Dissatisfaction (NOD)", "comply promptly"],
     "cat": "تسوية المنازعات"},

    # ══ 10. اللغة القانونية الأساسية ════════════════════════════════════════
    {"en": "shall", "ipa": "/ʃæl/", "syllables": "SHAL",
     "ar": "يجب / يلتزم (صيغة الإلزام)",
     "def_ar": "أهم كلمة في لغة العقود: تفيد الالتزام القانوني الواجب. «The Contractor shall...» = يلتزم المقاول بـ... وليست مستقبلاً بسيطاً.",
     "ex_en": "The Contractor shall submit a Statement at the end of each month.",
     "ex_ar": "يلتزم المقاول بتقديم كشفٍ في نهاية كل شهر.",
     "collocations": ["shall be entitled to", "shall not", "shall be deemed"],
     "cat": "اللغة القانونية",
     "tip": "قارن: shall = التزام واجب | may = حق جوازي | will = إخبار مستقبلي | must = اشتراط."},

    {"en": "may", "ipa": "/meɪ/", "syllables": "MAY",
     "ar": "يجوز له (صيغة الجواز)",
     "def_ar": "تمنح حقاً أو صلاحية تقديرية دون إلزام: «The Engineer may...» = يجوز للمهندس، له أن يفعل أو لا يفعل.",
     "ex_en": "The Employer may carry out the work himself if the Contractor fails to remedy the defect.",
     "ex_ar": "يجوز لصاحب العمل تنفيذ العمل بنفسه إذا لم يصلح المقاولُ العيب.",
     "collocations": ["may at any time", "may, at its sole discretion", "may but shall not be obliged to"],
     "cat": "اللغة القانونية"},

    {"en": "hereinafter", "ipa": "/ˌhɪərɪnˈɑːftər/", "syllables": "heer-in-AHF-tur",
     "ar": "المشار إليه فيما بعد بـ",
     "def_ar": "تُستخدم عند أول ذكر لتعريف تسمية مختصرة: (hereinafter referred to as “the Contractor”) = ويشار إليه فيما بعد بـ«المقاول».",
     "ex_en": "ABC Construction Co. (hereinafter referred to as “the Contractor”) agrees to execute the Works.",
     "ex_ar": "توافق شركة ABC للإنشاءات (ويُشار إليها فيما بعد بـ«المقاول») على تنفيذ الأعمال.",
     "collocations": ["hereinafter referred to as", "hereinafter called"],
     "cat": "اللغة القانونية",
     "tip": "عائلة here- تشير إلى هذا المستند: herein (في هذا العقد)، hereby (بموجب هذا)، hereto (إلى هذا)."},

    {"en": "thereof / therein / thereto", "ipa": "/ðeərˈɒv/", "syllables": "thair-OV",
     "ar": "منه / فيه / إليه (عائدة على المذكور)",
     "def_ar": "عائلة there- تعود على آخر شيء ذُكر: thereof = منه/الخاص به، therein = فيه، thereto = إليه، thereunder = بموجبه.",
     "ex_en": "The Contract and any amendment thereof shall be binding upon the Parties.",
     "ex_ar": "يكون العقد وأي تعديل له ملزِماً للطرفين.",
     "collocations": ["or any part thereof", "the terms thereof", "attached thereto"],
     "cat": "اللغة القانونية",
     "tip": "‏th هنا مجهورة /ð/ كالذال: «ذير أوف»."},

    {"en": "notwithstanding", "ipa": "/ˌnɒtwɪθˈstændɪŋ/", "syllables": "not-with-STAN-ding",
     "ar": "على الرغم من / بصرف النظر عن",
     "def_ar": "أداة ترجيح قوية: البند الذي يبدأ بها يَغلِب على ما يخالفه. «Notwithstanding Clause 5» = على الرغم مما ورد في البند 5.",
     "ex_en": "Notwithstanding any other provision of the Contract, the total liability shall not exceed the Contract Price.",
     "ex_ar": "على الرغم من أي حكم آخر في العقد، لا تتجاوز المسؤوليةُ الإجمالية قيمةَ العقد.",
     "collocations": ["notwithstanding the foregoing", "notwithstanding anything to the contrary"],
     "cat": "اللغة القانونية",
     "tip": "كلمة واحدة من 4 مقاطع، النبر على STAN. ترجّح البند الذي تتصدّره على غيره."},

    {"en": "pursuant to", "ipa": "/pəˈsjuːənt tuː/", "syllables": "pur-SYOO-unt too",
     "ar": "بموجب / عملاً بـ",
     "def_ar": "تعني «استناداً إلى» أو «تنفيذاً لـ» نص محدد: pursuant to Sub-Clause 8.4 = بموجب البند الفرعي 8.4.",
     "ex_en": "The Engineer issued a Variation pursuant to Sub-Clause 13.3 of the Conditions.",
     "ex_ar": "أصدر المهندس تغييراً بموجب البند الفرعي 13.3 من الشروط.",
     "collocations": ["pursuant to Clause...", "in accordance with", "under the Contract"],
     "cat": "اللغة القانونية"},

    {"en": "subject to", "ipa": "/ˈsʌbdʒɪkt tuː/", "syllables": "SUB-jikt too",
     "ar": "مع مراعاة / رهناً بـ",
     "def_ar": "تُخضِع الحكم لقيد آخر: «Subject to Clause 10» = مع مراعاة البند 10 (فالبند 10 يقيّد هذا الحكم ويعلو عليه).",
     "ex_en": "Subject to Sub-Clause 2.5, the Employer shall make payment within 56 days.",
     "ex_ar": "مع مراعاة البند الفرعي 2.5، يسدد صاحبُ العمل الدفعة خلال 56 يوماً.",
     "collocations": ["subject to the provisions of", "subject always to"],
     "cat": "اللغة القانونية",
     "tip": "عكس notwithstanding تماماً: subject to = البند الآخر يَغلِب | notwithstanding = بندي أنا يَغلِب."},

    {"en": "deemed", "ipa": "/diːmd/", "syllables": "DEEMD",
     "ar": "يُعتبر / يُعدّ (حكماً)",
     "def_ar": "افتراض قانوني: يُعامَل الشيء كأنه واقع وإن لم يقع فعلاً. «shall be deemed to have been received» = يُعتبر مستلَماً حكماً.",
     "ex_en": "If no notice is given, the Contractor shall be deemed to have accepted the measurement as correct.",
     "ex_ar": "إذا لم يُقدَّم إشعار، اعتُبر المقاول قابلاً بالقياس باعتباره صحيحاً.",
     "collocations": ["shall be deemed to", "deemed acceptance", "deemed to have knowledge"],
     "cat": "اللغة القانونية"},

    {"en": "whereas", "ipa": "/weərˈæz/", "syllables": "wair-AZ",
     "ar": "حيث إنّ (في الديباجة)",
     "def_ar": "تفتتح فقرات التمهيد (Recitals) في صدر العقد التي تسرد خلفيته وأغراضه، وليست التزامات بحد ذاتها.",
     "ex_en": "WHEREAS the Employer desires that the Works should be executed by the Contractor...",
     "ex_ar": "حيث إنّ صاحب العمل يرغب في أن ينفّذ المقاولُ الأعمالَ...",
     "collocations": ["recitals", "NOW THEREFORE it is agreed as follows"],
     "cat": "اللغة القانونية"},

    {"en": "in accordance with", "ipa": "/ɪn əˈkɔːdəns wɪð/", "syllables": "in uh-KOR-duns with",
     "ar": "وفقاً لـ / طبقاً لـ",
     "def_ar": "أكثر عبارة تكراراً في العقود: تعني الالتزام بمطابقة النص المُحال إليه تماماً.",
     "ex_en": "The Works shall be executed in accordance with the Contract and to the satisfaction of the Engineer.",
     "ex_ar": "تُنفَّذ الأعمال وفقاً للعقد وبما يرضي المهندس.",
     "collocations": ["in accordance with the Contract", "in compliance with", "as per"],
     "cat": "اللغة القانونية",
     "tip": "النبر في accordance على KOR: uh-KOR-duns."},

    {"en": "entitled to", "ipa": "/ɪnˈtaɪtəld tuː/", "syllables": "in-TY-tuld too",
     "ar": "يستحق / يحق له",
     "def_ar": "صيغة تقرير الحقوق: «shall be entitled to» = يكون مستحقاً لـ. أساس صياغة المطالبات: entitlement = الاستحقاق.",
     "ex_en": "The Contractor shall be entitled, subject to Sub-Clause 20.2, to an extension of time and payment of such Cost.",
     "ex_ar": "يستحق المقاول، مع مراعاة البند الفرعي 20.2، تمديداً للمدة ودفعَ تلك التكلفة.",
     "collocations": ["entitlement", "shall be entitled to", "entitled to payment"],
     "cat": "اللغة القانونية",
     "tip": "‏t الوسطى تُنطق خفيفة مثل d في النطق الأمريكي: in-TY-duld."},

    {"en": "provided that", "ipa": "/prəˈvaɪdɪd ðæt/", "syllables": "pruh-VY-did that",
     "ar": "شريطة أن / بشرط",
     "def_ar": "تُدخل شرطاً أو قيداً أو استثناءً على الحكم السابق (proviso). من أهم أدوات تقييد الالتزامات.",
     "ex_en": "The Contractor may use the access route, provided that the Contractor maintains it at his own cost.",
     "ex_ar": "يجوز للمقاول استخدام طريق الوصول، شريطة أن يصونه على نفقته الخاصة.",
     "collocations": ["provided always that", "proviso", "on condition that"],
     "cat": "اللغة القانونية"},

    {"en": "due", "ipa": "/djuː/", "syllables": "DYOO",
     "ar": "مستحَق / واجب الأداء",
     "def_ar": "ما حلّ موعد أدائه: amount due = المبلغ المستحق، due date = تاريخ الاستحقاق. أيضاً: due care = العناية الواجبة.",
     "ex_en": "The Employer shall pay the amount due within the period stated in the Contract.",
     "ex_ar": "يسدد صاحبُ العمل المبلغَ المستحق خلال المدة المحددة في العقد.",
     "collocations": ["amount due", "due date", "due diligence", "fall due"],
     "cat": "اللغة القانونية"},

    # ══ 11. كلمات بمعانٍ قانونية خاصة (False Friends) ═══════════════════════════
    {"en": "Consideration", "ipa": "/kənˌsɪdəˈreɪʃən/", "syllables": "kun-sid-uh-RAY-shun",
     "ar": "المُقابِل / العِوض",
     "def_ar": "ليست «الاهتمام»! بل العِوض المتبادَل الذي يجعل العقد مُلزِماً في القانون الإنجليزي (مال أو عمل أو وعد). لا عقد دون consideration.",
     "ex_en": "In consideration of the payments to be made by the Employer, the Contractor undertakes to execute the Works.",
     "ex_ar": "مقابلَ المدفوعات التي سيؤديها صاحبُ العمل، يتعهد المقاول بتنفيذ الأعمال.",
     "collocations": ["in consideration of", "good and valuable consideration", "for nominal consideration"],
     "cat": "كلمات بمعانٍ خاصة",
     "tip": "فخّ كلاسيكي: consideration هنا = العِوض، لا «المراعاة» ولا «الاهتمام»."},

    {"en": "Execute", "ipa": "/ˈeksɪkjuːt/", "syllables": "EK-si-kyoot",
     "ar": "يُبرِم (يوقّع) / ينفّذ",
     "def_ar": "لها معنيان: (1) execute the Contract = يُبرِم/يوقّع العقد؛ (2) execute the Works = ينفّذ الأعمال. والسياق يحسم. (وليست «يُعدِم»!).",
     "ex_en": "This Agreement is executed by the duly authorised representatives of the Parties.",
     "ex_ar": "تُبرَم هذه الاتفاقية بواسطة ممثلي الطرفين المفوَّضين حسب الأصول.",
     "collocations": ["duly executed", "execute and deliver", "execution of the Works"],
     "cat": "كلمات بمعانٍ خاصة",
     "tip": "executed a deed = أبرم/وقّع محرراً. لا تخلطها بالإعدام رغم تطابق الكلمة!"},

    {"en": "Discharge", "ipa": "/dɪsˈtʃɑːdʒ/", "syllables": "dis-CHARJ",
     "ar": "إبراء / وفاء (بالالتزام)",
     "def_ar": "انقضاء الالتزام بأدائه أو إبراء الذمة منه. discharge of obligations = الوفاء بالالتزامات؛ والاسم في الفيديك = إقرار المقاول بأنه استوفى كامل مستحقاته.",
     "ex_en": "Upon payment of the amount due, the Employer shall be discharged from all further liability under the Contract.",
     "ex_ar": "بسداد المبلغ المستحق، تبرأ ذمة صاحب العمل من أي مسؤولية أخرى بموجب العقد.",
     "collocations": ["discharge of obligations", "full and final discharge", "discharge a debt"],
     "cat": "كلمات بمعانٍ خاصة"},

    {"en": "Instrument", "ipa": "/ˈɪnstrəmənt/", "syllables": "IN-stru-munt",
     "ar": "سَنَد / مُحرَّر (قانوني)",
     "def_ar": "وثيقة قانونية رسمية مكتوبة (كفالة، ضمان، سند). ليست «آلة موسيقية»! a negotiable instrument = سند قابل للتداول.",
     "ex_en": "The Performance Security shall be in the form of the instrument annexed to the Particular Conditions.",
     "ex_ar": "يكون ضمان حسن التنفيذ بصيغة السند المرفق بالشروط الخاصة.",
     "collocations": ["legal instrument", "negotiable instrument", "instrument of guarantee"],
     "cat": "كلمات بمعانٍ خاصة"},

    {"en": "Save / Save as", "ipa": "/seɪv/", "syllables": "SAYV",
     "ar": "إلّا / باستثناء",
     "def_ar": "في اللغة القانونية save تعني except (إلّا). save as otherwise provided = إلّا فيما نُص على خلافه. (ليست «يحفظ» ولا «يُنقذ»).",
     "ex_en": "Save as otherwise expressly stated, all notices shall be given in writing.",
     "ex_ar": "فيما عدا ما نُص عليه صراحةً خلافَ ذلك، تُوجَّه جميع الإشعارات كتابةً.",
     "collocations": ["save as provided", "save to the extent that", "save and except"],
     "cat": "كلمات بمعانٍ خاصة",
     "tip": "إذا رأيت Save في صدر بند، اقرأها «باستثناء» وسيستقيم المعنى فوراً."},

    {"en": "Construction (interpretation)", "ipa": "/kənˈstrʌkʃən/", "syllables": "kun-STRUK-shun",
     "ar": "تفسير (النص)",
     "def_ar": "بجانب «الإنشاء»، لها معنى قانوني = تفسير النصوص. rules of construction = قواعد التفسير، وليست قواعد البناء!",
     "ex_en": "In the construction of this Contract, the headings shall not affect its interpretation.",
     "ex_ar": "في تفسير هذا العقد، لا تؤثر العناوين في معناه.",
     "collocations": ["rules of construction", "construction of the Contract", "construed as"],
     "cat": "كلمات بمعانٍ خاصة",
     "tip": "construe (فعل) = يفسّر. construed in accordance with English law = يُفسَّر وفق القانون الإنجليزي."},

    {"en": "Material", "ipa": "/məˈtɪəriəl/", "syllables": "muh-TEER-ee-ul",
     "ar": "جوهري / ذو أثر معتبَر",
     "def_ar": "صفةٌ قانونية = مؤثِّر وجوهري، لا مجرد «مادة». material breach = إخلال جوهري يبرّر الإنهاء؛ material change = تغيير جوهري.",
     "ex_en": "A material breach which is not remedied within the cure period shall entitle the innocent Party to terminate.",
     "ex_ar": "الإخلال الجوهري الذي لا يُصلَح خلال مهلة العلاج يخوّل الطرفَ المتضرر حقَّ الإنهاء.",
     "collocations": ["material breach", "material adverse effect", "in all material respects"],
     "cat": "كلمات بمعانٍ خاصة"},

    {"en": "Forthwith", "ipa": "/ˌfɔːθˈwɪθ/", "syllables": "forth-WITH",
     "ar": "فوراً / دون إبطاء",
     "def_ar": "أقوى من «promptly»: تعني حالاً دون أي تأخير. كثيرة الورود في موجبات الإشعار والإصلاح العاجل.",
     "ex_en": "The Contractor shall forthwith give notice to the Engineer of any such error found in the documents.",
     "ex_ar": "يُخطر المقاولُ المهندسَ فوراً بأي خطأ من هذا القبيل يُكتشف في المستندات.",
     "collocations": ["forthwith upon", "shall forthwith", "remedy forthwith"],
     "cat": "كلمات بمعانٍ خاصة",
     "tip": "‏th مرتان: forth-WITH — الأولى مهموسة /θ/ والثانية مجهورة /ð/. تدرّب عليها."},

    # ══ 12. البنود النمطية (Boilerplate) ═══════════════════════════════════════
    {"en": "Entire Agreement", "ipa": "/ɪnˈtaɪər əˈɡriːmənt/", "syllables": "in-TY-ur uh-GREE-munt",
     "ar": "بند الاتفاق الكامل",
     "def_ar": "بند يقرّر أن العقد المكتوب يمثّل كامل الاتفاق ويُلغي أي وعود أو مفاوضات سابقة. يحمي من الاحتجاج بتفاهمات شفهية.",
     "ex_en": "This Contract constitutes the entire agreement between the Parties and supersedes all prior negotiations and representations.",
     "ex_ar": "يمثّل هذا العقد كاملَ الاتفاق بين الطرفين ويَجُبّ كل ما سبقه من مفاوضات وإفادات.",
     "collocations": ["supersedes all prior agreements", "no reliance", "merger clause"],
     "cat": "البنود النمطية"},

    {"en": "Severability", "ipa": "/sɪˌverəˈbɪlɪti/", "syllables": "si-ver-uh-BIL-i-tee",
     "ar": "قابلية الفصل / استقلال البنود",
     "def_ar": "بند يقضي بأن بطلان أحد البنود لا يُبطل بقية العقد، بل يُفصل الباطل ويبقى الباقي نافذاً.",
     "ex_en": "If any provision is held to be invalid or unenforceable, the remaining provisions shall continue in full force and effect.",
     "ex_ar": "إذا قُضي ببطلان أي حكم أو عدم قابليته للتنفيذ، تظل بقية الأحكام نافذةً بكامل قوتها.",
     "collocations": ["invalid or unenforceable", "remaining provisions", "shall be severed"],
     "cat": "البنود النمطية"},

    {"en": "Waiver", "ipa": "/ˈweɪvər/", "syllables": "WAY-vur",
     "ar": "تنازل / إسقاط (حق)",
     "def_ar": "التخلي الطوعي عن حق. وبند «no waiver» يمنع اعتبار التساهل مرةً تنازلاً دائماً عن الحق.",
     "ex_en": "No waiver of any breach shall be deemed a waiver of any subsequent breach.",
     "ex_ar": "لا يُعتبر التنازل عن أي إخلال تنازلاً عن أي إخلال لاحق.",
     "collocations": ["waive a right", "no waiver", "waiver in writing"],
     "cat": "البنود النمطية",
     "tip": "waive (يتنازل) ≠ wave (يلوّح). كلاهما /weɪv/ لكن المعنى القانوني هو الأول."},

    {"en": "Novation", "ipa": "/nəʊˈveɪʃən/", "syllables": "noh-VAY-shun",
     "ar": "الإحلال / تجديد الالتزام",
     "def_ar": "استبدال طرفٍ بطرفٍ جديد في العقد باتفاق الجميع، بحيث يحلّ الجديد محل القديم في الحقوق والالتزامات. تختلف عن الـassignment التي تنقل الحقوق فقط.",
     "ex_en": "The rights and obligations of the original Contractor were transferred to the new entity by way of novation.",
     "ex_ar": "نُقلت حقوق المقاول الأصلي والتزاماته إلى الكيان الجديد عن طريق الإحلال.",
     "collocations": ["deed of novation", "novate the contract", "assignment vs novation"],
     "cat": "البنود النمطية",
     "tip": "فرّق: Assignment = نقل الحقوق فقط | Novation = نقل الحقوق والالتزامات بطرفٍ جديد."},

    {"en": "Time is of the essence", "ipa": "/taɪm ɪz əv ði ˈesəns/", "syllables": "TIME iz ov thee ES-uns",
     "ar": "الوقت عنصر جوهري",
     "def_ar": "عبارة تجعل المواعيد شرطاً جوهرياً، فيُجيز الإخلال بها الإنهاءَ لا مجرد التعويض. غيابها يجعل التأخير اليسير غير مُبرِّر للإنهاء غالباً.",
     "ex_en": "Time shall be of the essence in respect of the Contractor's obligations to achieve the Milestone Dates.",
     "ex_ar": "يكون الوقت عنصراً جوهرياً فيما يتعلق بالتزامات المقاول ببلوغ تواريخ المراحل.",
     "collocations": ["time at large", "milestone dates", "of the essence"],
     "cat": "البنود النمطية"},

    {"en": "Best / Reasonable endeavours", "ipa": "/ˈriːzənəbl ɪnˈdevəz/", "syllables": "REE-zun-uh-bul in-DEV-urz",
     "ar": "بذل أقصى / معقول الجهود",
     "def_ar": "معياران للالتزام بالسعي: best endeavours التزام مشدَّد (قد يكلّف الطرف ولو على حسابه)، وreasonable endeavours أخف (الجهد المعقول تجارياً). الفرق بينهما محل نزاعات كثيرة.",
     "ex_en": "The Contractor shall use reasonable endeavours to mitigate the effects of any delay.",
     "ex_ar": "يبذل المقاول جهوداً معقولة للتخفيف من آثار أي تأخير.",
     "collocations": ["best endeavours", "all reasonable endeavours", "commercially reasonable efforts"],
     "cat": "البنود النمطية",
     "tip": "endeavour بريطانية (الأمريكية endeavor). النبر in-DEV-ur، والـ-our تُنطق /ə/ خفيفة."},

    {"en": "Estoppel", "ipa": "/ɪˈstɒpəl/", "syllables": "i-STOP-ul",
     "ar": "الإغلاق / المنع الحُكمي",
     "def_ar": "مبدأ يمنع الطرف من التمسّك بموقفٍ يناقض تصرفاً سابقاً منه اعتمد عليه الطرف الآخر. أي: لا يجوز لك أن «تنقض ما بنى عليه غيرُك».",
     "ex_en": "The Employer is estopped from denying the validity of the variation it previously approved in writing.",
     "ex_ar": "يُمنع صاحبُ العمل من إنكار صحة التغيير الذي سبق أن أقرّه كتابةً.",
     "collocations": ["promissory estoppel", "estopped from", "waiver and estoppel"],
     "cat": "البنود النمطية",
     "tip": "حرف t مضعّف صوتياً والنبر على STOP: i-STOP-ul."},

    {"en": "Lien", "ipa": "/liːn/", "syllables": "LEEN",
     "ar": "حق الحبس / الامتياز",
     "def_ar": "حق في حبس مال الغير (أو مطالبة بأولوية) ضماناً لدين. تشترط العقود غالباً تسليم الأعمال خاليةً من أي lien.",
     "ex_en": "The Contractor shall ensure that the Works are free from any lien, charge or encumbrance.",
     "ex_ar": "يضمن المقاول أن تكون الأعمال خاليةً من أي حق حبس أو رهن أو عبء.",
     "collocations": ["free from liens", "charge or encumbrance", "mechanic's lien"],
     "cat": "البنود النمطية",
     "tip": "تُنطق «لِين» بياء طويلة /liːn/ — حرف i لا يُنطق كـ«اي»."},

    {"en": "Condition vs Warranty", "ipa": "/kənˈdɪʃən, ˈwɒrənti/", "syllables": "kun-DI-shun / WOR-un-tee",
     "ar": "شرط جوهري مقابل تعهّد ثانوي",
     "def_ar": "في القانون الإنجليزي: condition بندٌ جوهري إخلالُه يجيز الإنهاء والتعويض؛ warranty تعهّدٌ ثانوي إخلالُه يجيز التعويض فقط لا الإنهاء. تصنيف البند يحدد العلاج.",
     "ex_en": "Breach of a condition entitles the innocent Party to terminate, whereas breach of a warranty sounds only in damages.",
     "ex_ar": "إخلال الشرط الجوهري يخوّل الطرف المتضرر الإنهاءَ، بينما إخلال التعهّد الثانوي لا يرتّب سوى التعويض.",
     "collocations": ["condition precedent", "breach of warranty", "innominate term"],
     "cat": "البنود النمطية",
     "tip": "‏warranty (تعهّد تعاقدي) تختلف عن guarantee (كفالة/ضمان من طرف ثالث)."},
]

# ─────────────────────────────────────────────────────────────────────────────
# تحديات النطق الخاصة بالمتحدثين بالعربية
# ─────────────────────────────────────────────────────────────────────────────

PRONUNCIATION_CHALLENGES: list[dict] = [
    {
        "title": "صوت P مقابل B",
        "ar": "لا يوجد صوت /p/ في العربية فيستبدله العرب بـ/b/. الفرق: /p/ مهموس بدفعة هواء قوية، /b/ مجهور. ضع ورقة أمام فمك — يجب أن تهتز بقوة مع P.",
        "pairs": [("Party", "حفلة/طرف"), ("Payment", "دفعة"), ("Performance", "أداء"),
                  ("Provision", "حُكم/بند"), ("Price", "سعر"), ("Period", "فترة")],
        "drill": "The Party shall provide the Performance Security before the Payment Period begins.",
    },
    {
        "title": "صوت V مقابل F",
        "ar": "‏/v/ مثل /f/ لكن بذبذبة في الأوتار الصوتية. أطبق أسنانك العليا على شفتك السفلى وأصدر صوتاً مجهوراً. ضع يدك على حنجرتك — يجب أن تشعر بالاهتزاز.",
        "pairs": [("Variation", "تغيير"), ("Value", "قيمة"), ("Provide", "يقدّم"),
                  ("Approval", "موافقة"), ("Valid", "ساري"), ("Waive", "يتنازل")],
        "drill": "The Variation shall be valued and approved, provided the value is verified.",
    },
    {
        "title": "النبر (Word Stress) يغيّر المعنى",
        "ar": "في الإنجليزية النبر صوتيٌّ مميِّز للمعنى. CON-tract (اسم: عقد) ≠ con-TRACT (فعل: ينكمش). أخطاء النبر أكثر ما يجعل نطق العرب «ثقيلاً».",
        "pairs": [("CONtract (عقد)", "conTRACT (ينكمش)"), ("PERmit (تصريح)", "perMIT (يسمح)"),
                  ("REcord (سجل)", "reCORD (يسجّل)"), ("OBject (شيء)", "obJECT (يعترض)"),
                  ("PREsent (حاضر)", "preSENT (يقدّم)"), ("SUBject (موضوع)", "subJECT (يُخضع)")],
        "drill": "Under this CONtract, the Contractor must obtain a PERmit before he is perMITted to proceed.",
    },
    {
        "title": "الثاء والذال: /θ/ و /ð/",
        "ar": "ميزة لك كعربي! /θ/ = ثاء (third, breach of faith) و /ð/ = ذال (the, therefore, thereof). لا تستبدلهما بـ s/z أو t/d كما يفعل غير العرب.",
        "pairs": [("third party (طرف ثالث)", "/θ/"), ("thereof (منه)", "/ð/"),
                  ("therein (فيه)", "/ð/"), ("method (طريقة)", "/θ/"),
                  ("within (خلال)", "/ð/"), ("monthly (شهري)", "/θ/")],
        "drill": "The third party shall be notified monthly of the methods and the terms thereof.",
    },
    {
        "title": "التقاء السواكن (Consonant Clusters)",
        "ar": "العربية لا تبدأ الكلمة بساكنَين فيُقحم العرب همزة أو كسرة: «إسبيسيفيكيشن». تدرّب على البدء بالعنقود مباشرة دون حركة قبله.",
        "pairs": [("Specification", "مواصفات — لا تقل iS-pecification"), ("Structure", "هيكل"),
                  ("Subcontractor", "مقاول باطن"), ("Instruction", "تعليمات"),
                  ("Strict", "صارم"), ("Scope", "نطاق")],
        "drill": "Strict instructions: the structure shall comply with the specification and the scope.",
    },
    {
        "title": "الحروف الصامتة (Silent Letters)",
        "ar": "حروف تُكتب ولا تُنطق — احفظها سماعياً لا إملائياً.",
        "pairs": [("debt → /det/", "دَين — حرف b صامت"), ("receipt → /rɪˈsiːt/", "إيصال — p صامتة"),
                  ("indict → /ɪnˈdaɪt/", "يتّهم — c صامتة"), ("subtle → /ˈsʌtəl/", "دقيق — b صامتة"),
                  ("hours → /aʊəz/", "ساعات — h صامتة"), ("foreign → /ˈfɒrɪn/", "أجنبي — g صامتة")],
        "drill": "The receipt of the debt shall be acknowledged within twenty-four hours.",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# الدروس المنهجية
# ─────────────────────────────────────────────────────────────────────────────

LESSONS: list[dict] = [
    {
        "id": "L01",
        "title": "مدخل: لماذا لغة العقود مختلفة؟",
        "level": "تأسيسي",
        "objectives": ["فهم خصائص الإنجليزية القانونية", "التعرف على بنية الجملة التعاقدية", "كسر حاجز الرهبة من النصوص الطويلة"],
        "content": """
### لماذا تبدو لغة العقود صعبة؟

الإنجليزية القانونية (Legal English) ليست لغة ثانية فحسب — حتى المتحدث الأصلي يجدها صعبة! لأنها تتميز بـ:

1. **جُمل طويلة جداً** — جملة واحدة قد تمتد 100 كلمة، لأنها تحاول سدّ كل ثغرة.
2. **مفردات لاتينية وفرنسية قديمة** — `force majeure`، `mutatis mutandis`، `bona fide`.
3. **كلمات عادية بمعانٍ خاصة** — `Plant` لا تعني نباتاً بل **التجهيزات الآلية**! و`Consideration` لا تعني اهتماماً بل **المقابل/العِوض**.
4. **التكرار المتعمَّد** — `terms and conditions`، `null and void`، `indemnify and hold harmless` — أزواج مترادفة للتوكيد القانوني.

### المفتاح الذهبي لقراءة أي جملة تعاقدية 🔑

كل جملة تعاقدية مهما طالت تتكون من:

> **مَن** (الفاعل القانوني) + **shall/may** (طبيعة الالتزام) + **ماذا** (الفعل) + **متى/كيف/بأي شرط** (القيود)

**مثال — جرّب تفكيكها:**

> *The Contractor **shall**, within 28 days after the Commencement Date, **submit** to the Engineer a detailed programme, **unless** otherwise stated in the Particular Conditions.*

| السؤال | الجواب |
|---|---|
| مَن؟ | The Contractor — المقاول |
| ما طبيعة الالتزام؟ | shall — التزام واجب |
| ماذا يفعل؟ | submit a detailed programme — يقدّم برنامجاً زمنياً |
| متى؟ | within 28 days after the Commencement Date |
| الاستثناء؟ | unless otherwise stated... — ما لم يُنص على غير ذلك |

✅ **القاعدة**: ابحث دائماً عن الفاعل وshall/may أولاً، ثم ضع أقواساً ذهنية حول العبارات الاعتراضية.
""",
        "quiz": [
            {"q": "كلمة Plant في عقود الفيديك تعني:", "options": ["نبات", "مصنع", "التجهيزات الآلية الدائمة", "موقع العمل"], "answer": 2,
             "explain": "Plant في الفيديك = الأجهزة والمعدات التي تصبح جزءاً دائماً من الأعمال."},
            {"q": "عند قراءة جملة تعاقدية طويلة، ما أول شيء تبحث عنه؟", "options": ["التواريخ", "الفاعل + shall/may", "أرقام البنود", "الأسماء الكبيرة"], "answer": 1,
             "explain": "الفاعل + الفعل الناقل للالتزام هما هيكل الجملة؛ كل الباقي قيود وتفاصيل."},
        ],
    },
    {
        "id": "L02",
        "title": "‏Shall / May / Must / Will — قلب لغة العقود",
        "level": "تأسيسي",
        "objectives": ["التمييز الدقيق بين أفعال الإلزام", "فهم الأثر القانوني لكل صيغة", "قراءة الالتزامات والحقوق بثقة"],
        "content": """
### أربع كلمات تحكم كل عقد

| الكلمة | المعنى القانوني | الترجمة | الأثر |
|---|---|---|---|
| **shall** | التزام واجب | يلتزم / يجب عليه | الإخلال به = إخلال بالعقد |
| **shall not** | حظر | يُحظر عليه / لا يجوز له | فعله = إخلال بالعقد |
| **may** | حق / صلاحية تقديرية | يجوز له | له الخيار، ولا يُلام إن لم يفعل |
| **may not** | منع الجواز | لا يجوز له | سلب الصلاحية |
| **must** | اشتراط/متطلب | يتعيّن | شرط لصحة شيء (غالباً في المتطلبات الفنية) |
| **will** | إخبار مستقبلي | سوف | لا ينشئ التزاماً غالباً (يصف وقائع متوقعة) |

### أمثلة حقيقية بأسلوب FIDIC

1. > *The Contractor **shall** provide the Performance Security within 28 days.*
   - **التزام**: على المقاول تقديم الضمان. إن لم يفعل → إخلال يخوّل صاحب العمل الإنهاء.

2. > *The Engineer **may** instruct a Variation at any time.*
   - **صلاحية**: للمهندس أن يأمر بتغيير — وله ألا يفعل. لا أحد يستطيع إجباره.

3. > *The Employer **will** make the Site available on the Commencement Date.*
   - **إخبار**: صياغة أضعف من shall — في النزاعات يُحتجّ بأنها وعد إخباري لا التزام صارم. (لهذا تستخدم العقود الجيدة shall دائماً للالتزامات.)

### ⚠️ فخ شهير
`shall` في الإنجليزية العامة الحديثة شبه ميتة (نقول will)، لكنها في العقود **حية وملزمة**. لا تترجمها أبداً بـ«سوف» — ترجمتها الصحيحة: **«يلتزم بـ» أو «يجب»**.

### صيغ مركّبة احفظها كقوالب
- **shall be entitled to** = يستحق / يحق له
- **shall be deemed to** = يُعتبر حكماً
- **shall not be liable for** = لا يكون مسؤولاً عن
- **may, at its sole discretion** = يجوز له وفق تقديره المطلق
""",
        "quiz": [
            {"q": "«The Engineer may issue instructions» تعني أن المهندس:", "options": ["ملزم بإصدار التعليمات", "له صلاحية إصدارها دون إلزام", "ممنوع من إصدارها", "سيصدرها مستقبلاً حتماً"], "answer": 1,
             "explain": "may = صلاحية تقديرية: له أن يفعل وله ألا يفعل."},
            {"q": "الترجمة الصحيحة لـ«The Contractor shall remedy the defect»:", "options": ["سوف يصلح المقاول العيب", "يجوز للمقاول إصلاح العيب", "يلتزم المقاول بإصلاح العيب", "ربما يصلح المقاول العيب"], "answer": 2,
             "explain": "shall في العقود = التزام واجب، وليست مستقبلاً بسيطاً."},
            {"q": "أي صيغة تنشئ حقاً للمقاول؟", "options": ["The Contractor shall...", "The Contractor shall be entitled to...", "The Contractor will...", "The Contractor must..."], "answer": 1,
             "explain": "shall be entitled to = يستحق — صيغة تقرير الحقوق."},
        ],
    },
    {
        "id": "L03",
        "title": "عائلات Here- / There- / Where- الغامضة",
        "level": "تأسيسي",
        "objectives": ["فك شفرة hereinafter وthereof وwhereby", "قراءة الديباجات والتعريفات", "التوقف عن الارتباك أمام هذه الكلمات"],
        "content": """
### القاعدة السحرية 🪄

هذه الكلمات العتيقة كلها تتبع نمطاً واحداً بسيطاً:

- **here-** = *this* (هذا المستند/العقد نفسه)
- **there-** = *that / it* (الشيء المذكور قبل قليل)
- **where-** = *which* (الذي/التي — للربط)

ثم أضف حرف الجر وافهم:

| الكلمة | فكّكها | المعنى |
|---|---|---|
| **herein** | in + this | في هذا العقد |
| **hereby** | by + this | بموجب هذا (العقد/الإشعار) |
| **hereto** | to + this | إلى هذا العقد (attached hereto = المرفق به) |
| **hereinafter** | in this + after | فيما بعد في هذا المستند |
| **hereunder** | under + this | بموجب هذا العقد |
| **thereof** | of + that | منه / الخاص بالمذكور |
| **therein** | in + that | في المذكور |
| **thereto** | to + that | إلى المذكور |
| **thereunder** | under + that | بموجب المذكور |
| **whereby** | by + which | الذي بموجبه |
| **whereof** | of + which | الذي عنه (in witness whereof = وإشهاداً على ذلك) |

### تطبيق عملي

> *This Agreement and the Schedules attached **hereto** constitute the entire agreement. Any amendment **thereof** shall be in writing.*

- **hereto** = to this Agreement → «الملاحق المرفقة **بهذه الاتفاقية**»
- **thereof** = of the agreement just mentioned → «أي تعديل **لها**»

> ***IN WITNESS WHEREOF**, the Parties have executed this Agreement.*

- عبارة الختم التقليدية = «**وإشهاداً على ما تقدَّم**، وقّع الطرفان هذه الاتفاقية». (executed هنا = وقَّع، وليس أعدم! 😄)

### 💡 خدعة القراءة السريعة
عند مصادفة كلمة there-: ارجع للخلف وابحث عن آخر اسم رئيسي — هو المقصود. `the Contract or any part thereof` = العقد أو أي جزء **من العقد**.
""",
        "quiz": [
            {"q": "«the Works or any Section thereof» — كلمة thereof تعود على:", "options": ["العقد", "الأعمال (the Works)", "المهندس", "الموقع"], "answer": 1,
             "explain": "there- تعود على آخر اسم رئيسي مذكور = the Works → أي قسم من الأعمال."},
            {"q": "«The Contractor hereby waives...» تعني:", "options": ["سيتنازل لاحقاً", "يتنازل بموجب هذا المستند", "تنازل في عقد سابق", "يرفض التنازل"], "answer": 1,
             "explain": "hereby = by this document — التنازل يقع بهذا النص نفسه فور توقيعه."},
            {"q": "ما معنى IN WITNESS WHEREOF؟", "options": ["في حضور الشهود", "وإشهاداً على ما تقدّم", "بشهادة المحكمة", "للعلم والإحاطة"], "answer": 1,
             "explain": "عبارة ختامية تقليدية تسبق التوقيعات = إثباتاً وإشهاداً على ما سبق."},
        ],
    },
    {
        "id": "L04",
        "title": "المبني للمجهول والاسمية — أسلوب العقود",
        "level": "متوسط",
        "objectives": ["فهم سبب كثرة المبني للمجهول", "تحويل الأفعال الاسمية إلى أفعال بسيطة ذهنياً", "تسريع القراءة 倍"],
        "content": """
### لماذا يكثر المبني للمجهول؟

تقول العقود: *“The Works **shall be executed** in accordance with the Contract”* بدلاً من *“The Contractor shall execute the Works”*. لماذا؟

1. **التركيز على الفعل لا الفاعل** — المهم أن تُنفَّذ الأعمال.
2. **الحياد والعمومية** — أحياناً الفاعل غير محدد أو متعدد.
3. ⚠️ **وأحياناً غموض مقصود** — *“payment shall be made”* — مَن يدفع؟ إن لم يُحدَّد فهذه ثغرة!

**مهارتك**: عند كل مبنيٍّ للمجهول اسأل: *by whom?* — مَن الفاعل الحقيقي؟ إن لم تجد جواباً واضحاً في البند فقد وجدت نقطة ضعف تفاوضية.

### الاسمية (Nominalization) — وحش العقود الثاني

تحويل الفعل البسيط إلى اسم ثقيل + فعل باهت:

| بدلاً من | تقول العقود | فكّكها ذهنياً إلى |
|---|---|---|
| terminate | **effect termination of** | أنهى |
| pay | **make payment of** | دفع |
| inspect | **carry out an inspection of** | فحص |
| decide | **make a determination of** | قرر |
| notify | **give notification to** | أخطر |
| fail | **commit a failure / be in default** | أخفق |

### تمرين التفكيك الذهني

> *“Upon the occurrence of a failure by the Contractor in the performance of its obligations, the issuance of a notice shall be effected by the Employer.”*

فكّكها: **If the Contractor fails to perform, the Employer shall issue a notice.**
«إذا أخفق المقاول في أداء التزاماته، أصدر صاحبُ العمل إشعاراً.»

✅ **القاعدة**: كل اسم منتهٍ بـ -tion / -ment / -ance / -ure يخفي فعلاً. اسأل: ما الفعل؟ مَن فاعله؟
""",
        "quiz": [
            {"q": "«Payment shall be made within 56 days» — ما السؤال النقدي الذي يجب أن تسأله؟", "options": ["كم المبلغ؟", "بأي عملة؟", "مَن الملزَم بالدفع؟ (by whom?)", "لماذا 56 يوماً؟"], "answer": 2,
             "explain": "المبني للمجهول يخفي الفاعل — إن لم يحدد البندُ الدافعَ فهذه ثغرة صياغة."},
            {"q": "فكّك: «The Engineer shall make a determination of the claim»", "options": ["The Engineer shall determine the claim", "The claim determines the Engineer", "The Engineer shall delay the claim", "The claim shall be ignored"], "answer": 0,
             "explain": "make a determination of = determine — الاسمية تخفي الفعل البسيط."},
        ],
    },
    {
        "id": "L05",
        "title": "هيكل عقد الفيديك — خريطتك للكتاب الأحمر",
        "level": "متوسط",
        "objectives": ["معرفة البنود العشرين وترتيبها المنطقي", "الوصول لأي حكم خلال ثوانٍ", "فهم منطق Sub-Clause والترقيم"],
        "content": """
### الكتاب الأحمر FIDIC Red Book 2017 — البنود العشرون

| # | البند | المحتوى |
|---|---|---|
| 1 | General Provisions | التعريفات والتفسير والأولويات |
| 2 | The Employer | التزامات صاحب العمل (الموقع، التمويل) |
| 3 | The Engineer | صلاحيات المهندس وتعليماته وتقديراته |
| 4 | The Contractor | الالتزامات العامة للمقاول (الأطول!) |
| 5 | Subcontracting | مقاولو الباطن |
| 6 | Staff and Labour | العمالة وساعات العمل |
| 7 | Plant, Materials and Workmanship | الجودة والفحص والرفض |
| 8 | Commencement, Delays and Suspension | المباشرة والتأخير والتعليق ⭐ |
| 9 | Tests on Completion | اختبارات الإكمال |
| 10 | Taking Over | التسلّم ⭐ |
| 11 | Defects after Taking Over | العيوب بعد التسلّم |
| 12 | Measurement and Valuation | القياس والتقييم |
| 13 | Variations and Adjustments | التغييرات ⭐ |
| 14 | Contract Price and Payment | الدفع ⭐ |
| 15 | Termination by Employer | إنهاء صاحب العمل |
| 16 | Suspension and Termination by Contractor | تعليق وإنهاء المقاول |
| 17 | Care of the Works and Indemnities | العهدة والتعويضات |
| 18 | Exceptional Events | الأحداث الاستثنائية (القوة القاهرة) |
| 19 | Insurance | التأمين |
| 20 | Claims, Disputes and Arbitration | المطالبات والمنازعات ⭐⭐ |

### منطق الترقيم
- **Clause 8** = البند الثامن كاملاً
- **Sub-Clause 8.4** = البند الفرعي الرابع من الثامن (إشعار التأخير المحتمل... إلخ)
- **Sub-Clause 8.4(a)** = الفقرة (أ) منه

### خريطة «أين أجد؟» السريعة 🗺️
- تأخّر المشروع؟ → **8.4/8.5** (EOT) ثم **20.2** (إجراء المطالبة)
- أمر تغييري؟ → **13** ثم التقييم في **12**
- ما قبضت فلوسك؟ → **14.7/14.8** (الدفع وفوائد التأخير) و**16.1** (حقك في التعليق)
- عيوب بعد التسلّم؟ → **11**
- حدث استثنائي؟ → **18** + إشعار **20**

💡 **عادة المحترفين**: عند قراءة أي بند، اقرأ معه دائماً التعريفات (1.1) الخاصة بمصطلحاته الكبيرة — فالكلمة بحرف كبير (Capitalized) معرَّفة تعريفاً ملزماً.
""",
        "quiz": [
            {"q": "أين تجد أحكام تمديد مدة الإنجاز (EOT) في الكتاب الأحمر 2017؟", "options": ["البند 4", "البند 8", "البند 14", "البند 20"], "answer": 1,
             "explain": "البند 8: Commencement, Delays and Suspension — وتحديداً 8.5."},
            {"q": "الكلمة المكتوبة بحرف استهلالي كبير في الفيديك (مثل Works) تعني:", "options": ["كلمة مهمة فقط", "مصطلح معرَّف تعريفاً ملزماً في 1.1", "خطأ مطبعي", "اسم علم"], "answer": 1,
             "explain": "الحرف الكبير = مصطلح معرَّف في بند التعريفات، بمعناه الدقيق الملزم."},
            {"q": "مطالبات المقاول وإجراءاتها الزمنية تجدها في:", "options": ["البند 20", "البند 13", "البند 9", "البند 2"], "answer": 0,
             "explain": "Clause 20: Claims, Disputes and Arbitration — أهم بند يحفظه مدير المشروع."},
        ],
    },
    {
        "id": "L06",
        "title": "لغة الإشعارات والمطالبات — أخطر 28 يوماً",
        "level": "متقدم",
        "objectives": ["صياغة وفهم إشعارات المطالبة", "إدراك شروط الإسقاط الزمني", "حفظ القوالب اللغوية الجاهزة"],
        "content": """
### لماذا هذا الدرس قد يساوي ملايين؟

البند 20.2.1 في فيديك 2017 يقول بصيغة مبسطة:

> *The claiming Party shall give a Notice to the Engineer **no later than 28 days** after the claiming Party became aware, or should have become aware, of the event. **If the claiming Party fails to give a Notice of Claim within this period... the claiming Party shall not be entitled** to any additional payment or EOT.*

**اللغة هنا «شرط إسقاط» (time-bar / condition precedent)**: فوّت 28 يوماً = خسرت حقك كاملاً، مهما كان قوياً.

### مفردات الإشعار الحرجة

| العبارة | المعنى | خطورتها |
|---|---|---|
| **became aware, or should have become aware** | علم أو كان يجب أن يعلم | العبرة بالعلم الحكمي لا الفعلي — لا ينفع «ما انتبهنا» |
| **shall not be entitled** | يسقط استحقاقه | صياغة الإسقاط الصريح |
| **condition precedent** | شرط واقف/مُسبق | الإشعار شرطٌ لنشوء الحق نفسه |
| **time-barred** | مسقَط بفوات المدة | وصف المطالبة المتأخرة |
| **contemporary records** | السجلات المعاصرة | سجلات تُعدّ وقت الحدث — عماد الإثبات |
| **fully detailed Claim** | المطالبة المفصلة الكاملة | تُقدَّم خلال 84 يوماً (فيديك 2017) |

### القالب الذهبي لإشعار مطالبة (احفظه!)

> *Pursuant to Sub-Clause 20.2.1 of the Conditions of Contract, we hereby give Notice of Claim in respect of [the event], which occurred on [date] and of which we became aware on [date]. The event has caused / is likely to cause delay to the Time for Completion and/or additional Cost. Detailed particulars will follow in accordance with Sub-Clause 20.2.4. This Notice is given without prejudice to any other rights or remedies available to us under the Contract or at law.*

لاحظ البنية: **السند النظامي → الإعلان → الوصف → الأثر → الحفظ العام للحقوق**.

### عبارات حفظ الحقوق (Reservation of Rights)
- *without prejudice to our other rights and remedies* — دون إخلال بحقوقنا الأخرى
- *we reserve all our rights under the Contract and at law* — نحتفظ بكامل حقوقنا
- *nothing herein shall be construed as a waiver* — لا يُفسَّر أي مما ورد هنا تنازلاً
""",
        "quiz": [
            {"q": "ما أثر فوات مهلة 28 يوماً لإشعار المطالبة في فيديك 2017؟", "options": ["غرامة مالية فقط", "سقوط الحق في التمديد والدفعة الإضافية", "تمديد المهلة تلقائياً", "إحالة فورية للتحكيم"], "answer": 1,
             "explain": "البند 20.2.1 شرطُ إسقاطٍ صريح: shall not be entitled — يسقط الحق كله."},
            {"q": "«should have become aware» تعني أن العبرة بـ:", "options": ["العلم الفعلي فقط", "العلم الحكمي: ما كان يجب أن يعلمه", "إقرار الطرف الآخر", "تاريخ التوقيع"], "answer": 1,
             "explain": "معيار موضوعي: متى كان ينبغي لمقاول يقظ أن يعلم؟ لا ينفع التذرّع بعدم الانتباه."},
            {"q": "عبارة «without prejudice to our other rights» غرضها:", "options": ["التنازل عن الحقوق", "حفظ بقية الحقوق من السقوط الضمني", "إنهاء العقد", "طلب التحكيم"], "answer": 1,
             "explain": "عبارة حفظ حقوق: ممارسةُ حقٍّ لا تعني التنازل عن غيره."},
        ],
    },
    {
        "id": "L07",
        "title": "قراءة بند فيديك كامل — تشريح حي",
        "level": "متقدم",
        "objectives": ["تطبيق كل المهارات على نص كامل", "بناء عادة التفكيك المنهجي", "الاستغناء عن الترجمة"],
        "content": """
### النص (بأسلوب Sub-Clause 8.5 — EOT)

> *The Contractor shall be entitled subject to Sub-Clause 20.2 [Claims for Payment and/or EOT] to Extension of Time if and to the extent that completion for the purposes of Sub-Clause 10.1 [Taking Over of the Works and Sections] is or will be delayed by any of the following causes: (a) a Variation; (b) a cause of delay giving an entitlement to EOT under a Sub-Clause of these Conditions; (c) exceptionally adverse climatic conditions; ...*

### التشريح خطوة بخطوة 🔬

**الخطوة 1 — الهيكل:** مَن؟ `The Contractor`. الصيغة؟ `shall be entitled to` = **حق** (لا التزام).

**الخطوة 2 — القيود قبل الحق:**
- `subject to Sub-Clause 20.2` → الحق **مشروط** بالتقيد بإجراءات المطالبة (الإشعار خلال 28 يوماً!). الحق هنا مقيد بإجراء هناك.

**الخطوة 3 — مفتاح دقيق جداً:** `if and to the extent that`
- ليس «إذا» فقط، بل «إذا وبقدر ما» — التمديد **بمقدار** التأخير الفعلي على الإكمال، لا أكثر. لو تأخر نشاطٌ غير حرج 30 يوماً ولم يتأخر الإكمال، فلا تمديد.

**الخطوة 4 — المعيار:** `is or will be delayed` — التأخير الواقع **أو المتوقع**: يمكن المطالبة استباقياً قبل وقوع التأخير فعلاً.

**الخطوة 5 — الأسباب (a), (b), (c):** قائمة حصرية اقرأها سبباً سبباً. لاحظ `exceptionally adverse climatic conditions` — ليست أي أحوال جوية سيئة، بل **استثنائية** الشدّة (قياساً بالبيانات المناخية المعتادة للموقع).

### الترجمة الاحترافية الكاملة

> «يستحق المقاول، مع مراعاة البند الفرعي 20.2، تمديداً لمدة الإنجاز إذا تأخّر الإكمالُ لأغراض البند الفرعي 10.1 أو كان سيتأخر، وبقدر ذلك التأخر، بسبب أيٍّ من الأسباب الآتية: (أ) تغيير؛ (ب) سببِ تأخيرٍ يمنح استحقاقاً للتمديد بموجب بندٍ من هذه الشروط؛ (ج) أحوالٍ مناخية معاكسة على نحو استثنائي؛ ...»

### 🏆 اختبر نفسك قبل الكويز
أعد قراءة النص الإنجليزي وحده الآن. هل تحتاج الترجمة؟ إن كان «لا» — فأنت على الطريق الصحيح.
""",
        "quiz": [
            {"q": "«if and to the extent that» تعني أن التمديد يُمنح:", "options": ["كاملاً عند أي تأخير", "بقدر تأثر الإكمال فعلاً فقط", "حسب تقدير المقاول", "مضاعفاً"], "answer": 1,
             "explain": "وبقدر ما — لو لم يتأثر الإكمال (تأخير غير حرج) فلا تمديد."},
            {"q": "«is or will be delayed» تتيح المطالبة:", "options": ["بعد وقوع التأخير فقط", "قبل وقوع التأخير المتوقع أيضاً", "بعد التسلّم فقط", "خلال التحكيم فقط"], "answer": 1,
             "explain": "التأخير الواقع أو المتوقع — مطالبة استباقية مشروعة."},
            {"q": "حق التمديد في 8.5 مشروط بـ:", "options": ["موافقة صاحب العمل المسبقة", "التقيد بإجراءات المطالبة في 20.2", "دفع رسوم", "تقرير خبير"], "answer": 1,
             "explain": "subject to Sub-Clause 20.2 — بدون الإشعار في مهلته يسقط الحق."},
        ],
    },
    {
        "id": "L08",
        "title": "لغة الدفع والمستخلصات",
        "level": "متقدم",
        "objectives": ["إتقان دورة الدفع الكاملة بمفرداتها", "قراءة بنود الدفع وفوائد التأخير", "فهم الاحتجاز والاسترداد"],
        "content": """
### دورة الدفع في الفيديك — بالمصطلحات

1. **Statement** (الكشف/المستخلص): يقدّمه المقاول شهرياً مع المستندات المؤيدة (supporting documents).
2. **Interim Payment Certificate — IPC**: يصدرها المهندس خلال 28 يوماً محدداً **the amount which he fairly considers to be due** (المبلغ الذي يراه بإنصاف مستحقاً).
3. **Payment**: يسدد صاحب العمل خلال 56 يوماً من تسلّم الكشف.
4. عند التأخر: **financing charges** (أعباء تمويل) مركّبة شهرياً، **without formal notice or certification** — دون حاجة لإشعار رسمي!

### مفردات الخصوم والاستردادات

| المصطلح | المعنى |
|---|---|
| **deduction** | خصم/استقطاع |
| **retention (money)** | المحتجزات (5-10٪) |
| **release of retention** | ردّ المحتجزات (نصف عند التسلّم ونصف بعد فترة العيوب) |
| **repayment of advance** | استرداد الدفعة المقدمة (خصماً نسبياً) |
| **set-off / contra charge** | المقاصة — خصم مستحقات متقابلة |
| **withhold** | يحجب/يمتنع عن صرف |

### صياغات احفظها كقوالب

> *The Employer shall pay to the Contractor the amount certified in each Interim Payment Certificate within 56 days after the Engineer receives the Statement and supporting documents.*

> *If the Contractor does not receive payment in accordance with Sub-Clause 14.7, the Contractor shall be entitled to receive financing charges compounded monthly on the amount unpaid during the period of delay.*

> *The Employer may withhold the amount of any contra charges properly due from the Contractor, **provided that** details are given in a Notice with supporting particulars.*

### ⚠️ فخّان لغويان
1. **certified ≠ paid**: صدور الشهادة لا يعني قبض المال — لكل منهما مهلة وأحكام.
2. **fairly considers**: تقدير المهندس يجب أن يكون منصفاً — وهي عبارة تفتح باب الطعن إذا تعسّف.
""",
        "quiz": [
            {"q": "‏financing charges في الفيديك تستحق:", "options": ["بإشعار رسمي وشهادة", "تلقائياً دون إشعار أو شهادة", "بحكم قضائي", "بموافقة صاحب العمل"], "answer": 1,
             "explain": "النص صريح: without formal notice or certification — تلقائياً بمجرد التأخر."},
            {"q": "‏set-off تعني:", "options": ["بدء الأعمال", "المقاصة بين مستحقات متقابلة", "إيقاف الأعمال", "تسوية ودية"], "answer": 1,
             "explain": "خصم ما يستحقه طرف من مستحقات الطرف الآخر المقابلة."},
        ],
    },
    {
        "id": "L09",
        "title": "لغة الإنهاء والمنازعات — قراءة بنود المعارك",
        "level": "متقدم",
        "objectives": ["قراءة بنود الإنهاء بدقة جراحية", "فهم سلّم تسوية المنازعات", "إتقان مفردات التحكيم"],
        "content": """
### لغة الإنهاء — درجات الحرارة

| الصيغة | المعنى | الحدّة |
|---|---|---|
| **Notice to Correct** | إشعار بتصحيح التقصير خلال مهلة | 🌡️ إنذار |
| **notice of intention to terminate** | إشعار بنيّة الإنهاء (14 يوماً عادة) | 🌡️🌡️ تهديد رسمي |
| **notice of termination** | إشعار الإنهاء النافذ | 🌡️🌡️🌡️ القطيعة |
| **termination for convenience** | إنهاء للملاءمة (دون خطأ المقاول) | حق صاحب العمل بتعويض عادل |
| **with immediate effect** | بأثر فوري (للإعسار والفساد) | ⚡ |

> *...the Employer may **by giving 14 days' notice** to the Contractor, **terminate the Contract**. However, in the case of sub-paragraph (f) or (g), the Employer may by notice terminate the Contract **with immediate effect**.*

لاحظ: المهلة 14 يوماً قاعدة، والفوري استثناء لحالات الإفلاس والرشوة.

### سلّم المنازعات في فيديك 2017 🪜

1. **Claim** → تقدير المهندس (**Agreement or Determination — 3.7**)
2. عدم الرضا؟ → **NOD** ‏(Notice of Dissatisfaction) خلال **28 يوماً**
3. الإحالة إلى **DAAB** → قرار خلال **84 يوماً** — مُلزم فوراً (binding) وإن لم يكن نهائياً
4. NOD ضد قرار المجلس خلال **28 يوماً** → محاولة **تسوية ودية** (28 يوماً)
5. **Arbitration** — تحكيم دولي (قواعد ICC غالباً) — **final and binding**

### مفردات التحكيم الأساسية
- **arbitral tribunal** = هيئة التحكيم | **arbitrator** = المحكَّم
- **seat of arbitration** = مقرّ التحكيم (يحدد القانون الإجرائي!)
- **award** = حكم التحكيم | **enforce an award** = تنفيذ الحكم
- **interim/conservatory measures** = تدابير مؤقتة/تحفظية
- **costs follow the event** = الخاسر يتحمل الأتعاب

### 💡 عبارة يخطئ فيها الجميع
**“binding” ≠ “final and binding”**: قرار الـDAAB مُلزم فوراً (يجب تنفيذه) لكنه غير نهائي (يقبل التحكيم). حكم التحكيم نهائي وملزم معاً.
""",
        "quiz": [
            {"q": "متى يجوز الإنهاء بأثر فوري (with immediate effect)؟", "options": ["أي تأخير", "الإعسار والرشوة ونحوها", "خلاف على مستخلص", "رفض تغيير"], "answer": 1,
             "explain": "القاعدة إشعار 14 يوماً؛ والفوري استثناء لحالات قصوى كالإفلاس والفساد."},
            {"q": "قرار الـDAAB الذي لم يُعترض عليه بـNOD خلال 28 يوماً يصبح:", "options": ["لاغياً", "نهائياً وملزماً", "استشارياً", "معلَّقاً"], "answer": 1,
             "explain": "بفوات مهلة إشعار عدم الرضا يتحول القرار من ملزم إلى نهائي وملزم."},
            {"q": "‏seat of arbitration تحدد:", "options": ["مكان الجلسات فقط", "القانون الإجرائي الحاكم للتحكيم", "لغة التحكيم", "عدد المحكمين"], "answer": 1,
             "explain": "المقرّ مفهوم قانوني يحدد قانون التحكيم والمحاكم المشرفة — وقد تُعقد الجلسات في غيره."},
        ],
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# معمل القراءة: بنود بأسلوب FIDIC مع مسرد تفاعلي
# ─────────────────────────────────────────────────────────────────────────────

READING_PASSAGES: list[dict] = [
    {
        "id": "R01",
        "title": "بند ضمان حسن التنفيذ (بأسلوب Sub-Clause 4.2)",
        "difficulty": "⭐⭐ متوسط",
        "text": """The Contractor shall obtain, at his cost, a Performance Security for proper performance, in the amount stated in the Contract Data and denominated in the currency of the Contract. The Contractor shall deliver the Performance Security to the Employer within 28 days after receiving the Letter of Acceptance, and shall send a copy to the Engineer. The Performance Security shall be issued by a bank or financial institution approved by the Employer, and shall be valid until the Contractor has executed and completed the Works and remedied any defects. The Employer shall not make a claim under the Performance Security, except for amounts to which the Employer is entitled under the Contract.""",
        "translation": "يستصدر المقاول، على نفقته، ضمانَ حسن تنفيذٍ للأداء السليم بالمبلغ المحدد في بيانات العقد وبعملة العقد. ويسلّم المقاولُ ضمانَ حسن التنفيذ إلى صاحب العمل خلال 28 يوماً من تسلّمه خطابَ القبول، ويرسل نسخةً إلى المهندس. ويصدر الضمانُ من بنكٍ أو مؤسسةٍ مالية يوافق عليها صاحبُ العمل، ويظل سارياً حتى ينفّذ المقاولُ الأعمالَ ويكملها ويصلح أيَّ عيوب. ولا يطالب صاحبُ العمل بموجب ضمان حسن التنفيذ إلا بالمبالغ التي يستحقها بموجب العقد.",
        "glossary": {
            "obtain": "يستصدر / يحصل على",
            "at his cost": "على نفقته الخاصة",
            "denominated in": "مقوَّم بـ (عملة)",
            "deliver": "يسلّم",
            "Letter of Acceptance": "خطاب القبول/الترسية",
            "issued by": "صادر من",
            "approved by": "معتمَد من",
            "valid until": "ساري المفعول حتى",
            "remedied": "أصلح / عالج",
            "make a claim under": "يطالب بموجب (الضمان)",
            "entitled": "مستحِق",
        },
        "questions": [
            {"q": "خلال كم يوماً يجب تسليم الضمان؟ ومن أي تاريخ؟", "options": ["14 يوماً من التوقيع", "28 يوماً من تسلّم خطاب القبول", "56 يوماً من المباشرة", "7 أيام من أول مستخلص"], "answer": 1},
            {"q": "متى يجوز لصاحب العمل المطالبة بموجب الضمان؟", "options": ["متى شاء", "فقط بالمبالغ المستحقة له بموجب العقد", "بعد التحكيم فقط", "لا يجوز مطلقاً"], "answer": 1},
        ],
    },
    {
        "id": "R02",
        "title": "بند غرامات التأخير (بأسلوب Sub-Clause 8.8)",
        "difficulty": "⭐⭐ متوسط",
        "text": """If the Contractor fails to comply with the Time for Completion, the Contractor shall, subject to the notice requirements of Sub-Clause 20.2, pay Delay Damages to the Employer for this default. These Delay Damages shall be the amount stated in the Contract Data, which shall be paid for every day which shall elapse between the relevant Time for Completion and the relevant Date of Completion of the Works. However, the total amount due under this Sub-Clause shall not exceed the maximum amount of Delay Damages (if any) stated in the Contract Data. These Delay Damages shall be the only damages due from the Contractor for such default, other than in the event of termination prior to completion of the Works.""",
        "translation": "إذا أخفق المقاول في التقيد بمدة الإنجاز، دفع المقاولُ — مع مراعاة متطلبات الإشعار في البند الفرعي 20.2 — تعويضاتِ تأخيرٍ إلى صاحب العمل عن هذا التقصير. وتكون تعويضات التأخير بالمبلغ المحدد في بيانات العقد، وتُدفع عن كل يومٍ ينقضي بين مدة الإنجاز المعنية وتاريخ إكمال الأعمال المعني. غير أن إجمالي المبلغ المستحق بموجب هذا البند الفرعي لا يتجاوز الحدَّ الأقصى لتعويضات التأخير (إن وُجد) المحددَ في بيانات العقد. وتكون تعويضات التأخير هذه هي التعويضات الوحيدة المستحقة على المقاول عن هذا التقصير، إلا في حالة الإنهاء قبل إكمال الأعمال.",
        "glossary": {
            "fails to comply with": "يخفق في التقيد بـ",
            "Delay Damages": "تعويضات/غرامات التأخير",
            "default": "تقصير",
            "elapse": "ينقضي (الوقت)",
            "shall not exceed": "لا يتجاوز",
            "maximum amount": "الحد الأقصى (السقف)",
            "the only damages due": "التعويضات الوحيدة المستحقة",
            "other than": "باستثناء / إلا",
            "prior to": "قبل",
        },
        "questions": [
            {"q": "ما سقف غرامات التأخير؟", "options": ["لا سقف لها", "الحد الأقصى المحدد في بيانات العقد", "10٪ دائماً", "قيمة العقد كاملة"], "answer": 1},
            {"q": "عبارة «the only damages due» تعني أن غرامة التأخير:", "options": ["تضاف لها تعويضات أخرى عن التأخير", "هي التعويض الحصري عن التأخير (عدا حالة الإنهاء)", "اختيارية", "رمزية"], "answer": 1},
        ],
    },
    {
        "id": "R03",
        "title": "بند الأحداث الاستثنائية (بأسلوب Clause 18)",
        "difficulty": "⭐⭐⭐ متقدم",
        "text": """"Exceptional Event" means an event or circumstance which: (i) is beyond a Party's control; (ii) the Party could not reasonably have provided against before entering into the Contract; (iii) having arisen, such Party could not reasonably have avoided or overcome; and (iv) is not substantially attributable to the other Party. If a Party is or will be prevented from performing any of its obligations under the Contract by an Exceptional Event, then it shall give a Notice to the other Party of such an Exceptional Event, and shall specify the obligations, the performance of which is or will be prevented. The Notice shall be given within 14 days after the Party became aware, or should have become aware, of the Exceptional Event. The affected Party shall be excused performance of the prevented obligations from the date such performance is prevented by the Exceptional Event.""",
        "translation": "«الحدث الاستثنائي» يعني حدثاً أو ظرفاً: (1) خارجاً عن سيطرة الطرف؛ و(2) لم يكن بوسع الطرف، على نحوٍ معقول، الاحتياط له قبل إبرام العقد؛ و(3) لم يكن بوسعه، عند وقوعه، تجنُّبه أو التغلب عليه على نحوٍ معقول؛ و(4) لا يُعزى جوهرياً إلى الطرف الآخر. فإذا مُنع طرفٌ أو كان سيُمنع من أداء أيٍّ من التزاماته بموجب العقد بسبب حدثٍ استثنائي، وجّه إشعاراً إلى الطرف الآخر بذلك الحدث الاستثنائي محدداً الالتزاماتِ الممنوعَ أو المتوقعَ منعُ أدائها. ويوجَّه الإشعار خلال 14 يوماً من علم الطرف بالحدث الاستثنائي أو من التاريخ الذي كان يجب أن يعلم به فيه. ويُعفى الطرفُ المتأثر من أداء الالتزامات الممنوعة اعتباراً من تاريخ منع الأداء بالحدث الاستثنائي.",
        "glossary": {
            "beyond a Party's control": "خارج عن سيطرة الطرف",
            "provided against": "احتاط له",
            "having arisen": "عند وقوعه",
            "avoided or overcome": "تجنّبه أو التغلب عليه",
            "substantially attributable to": "يُعزى جوهرياً إلى",
            "prevented from performing": "ممنوع من الأداء",
            "specify": "يحدد",
            "should have become aware": "كان يجب أن يعلم",
            "excused performance": "مُعفى من الأداء",
        },
        "questions": [
            {"q": "كم شرطاً يجب توافرها معاً ليُعتبر الحدث استثنائياً؟", "options": ["شرطان", "ثلاثة", "أربعة", "خمسة"], "answer": 2},
            {"q": "مهلة الإشعار بالحدث الاستثنائي:", "options": ["28 يوماً", "14 يوماً من العلم أو وجوب العلم", "7 أيام من الوقوع", "بلا مهلة"], "answer": 1},
            {"q": "أثر الحدث الاستثنائي على الالتزامات الممنوعة:", "options": ["إلغاؤها نهائياً", "الإعفاء من أدائها مدة المنع", "مضاعفتها", "تحويلها للطرف الآخر"], "answer": 1},
        ],
    },
    {
        "id": "R04",
        "title": "ديباجة اتفاقية عقد (Contract Agreement)",
        "difficulty": "⭐ تأسيسي",
        "text": """THIS AGREEMENT is made on the 15th day of January 2026 BETWEEN Al-Rawaf Development Company of Riyadh, Kingdom of Saudi Arabia (hereinafter called "the Employer") of the one part, AND Gulf Construction Ltd of Dammam, Kingdom of Saudi Arabia (hereinafter called "the Contractor") of the other part. WHEREAS the Employer desires that the Works known as the Northern Logistics Park should be executed by the Contractor, and has accepted a Tender by the Contractor for the execution and completion of these Works and the remedying of any defects therein, NOW THEREFORE the Employer and the Contractor agree as follows: In this Agreement words and expressions shall have the same meanings as are respectively assigned to them in the Conditions of Contract hereinafter referred to. IN WITNESS WHEREOF the parties hereto have caused this Agreement to be executed the day and year first before written.""",
        "translation": "حُررت هذه الاتفاقية في اليوم الخامس عشر من يناير 2026 بين شركة الرواف للتطوير، الرياض، المملكة العربية السعودية (ويشار إليها فيما بعد بـ«صاحب العمل») طرفاً أول، وشركة الخليج للإنشاءات المحدودة، الدمام، المملكة العربية السعودية (ويشار إليها فيما بعد بـ«المقاول») طرفاً ثانياً. وحيث إنّ صاحب العمل يرغب في أن ينفّذ المقاولُ الأعمالَ المعروفة بـ«المجمع اللوجستي الشمالي»، وقد قَبِل عطاءً من المقاول لتنفيذ هذه الأعمال وإكمالها وإصلاح أي عيوب فيها، فقد اتفق صاحبُ العمل والمقاول، بناءً على ما تقدم، على ما يلي: تكون للكلمات والعبارات في هذه الاتفاقية المعاني نفسها المخصصة لها في شروط العقد المشار إليها فيما بعد. وإشهاداً على ما تقدّم، أبرم الطرفان هذه الاتفاقية في اليوم والسنة المذكورَين أول هذا المحرر.",
        "glossary": {
            "THIS AGREEMENT is made": "حُررت هذه الاتفاقية",
            "hereinafter called": "ويشار إليه فيما بعد بـ",
            "of the one part": "طرفاً أول",
            "WHEREAS": "حيث إنّ",
            "desires": "يرغب",
            "remedying of any defects therein": "إصلاح أي عيوب فيها",
            "NOW THEREFORE": "وبناءً على ما تقدّم",
            "respectively assigned": "المخصصة لكلٍّ منها",
            "IN WITNESS WHEREOF": "وإشهاداً على ما تقدّم",
            "parties hereto": "طرفا هذه الاتفاقية",
            "executed": "أبرم / وقّع",
        },
        "questions": [
            {"q": "كلمة executed في ختام الديباجة تعني:", "options": ["أعدم", "نفّذ الأعمال", "وقّع وأبرم", "ألغى"], "answer": 2},
            {"q": "فقرات WHEREAS في صدر العقد:", "options": ["التزامات ملزمة", "تمهيد يسرد الخلفية والغرض", "شروط الدفع", "بنود التحكيم"], "answer": 1},
        ],
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# محادثات مهنية (Spoken Contract English) — لتدريب الأذن واللسان
# ─────────────────────────────────────────────────────────────────────────────

DIALOGUES: list[dict] = [
    {
        "id": "D01",
        "title": "اجتماع متابعة في الموقع — تأخير ومطالبة بالتمديد",
        "scenario_ar": "اجتماع أسبوعي في الموقع بين المهندس الاستشاري ومدير مشروع المقاول لمناقشة تأخّرٍ أثّر على المسار الحرج ونيّة المقاول المطالبة بتمديد المدة.",
        "lines": [
            {"speaker": "Engineer", "en": "Good morning. Let's start with the programme. You're now two weeks behind on the foundation works. What's driving the delay?",
             "ar": "صباح الخير. لنبدأ بالبرنامج الزمني. أنتم الآن متأخرون أسبوعين في أعمال الأساسات. ما سبب التأخير؟"},
            {"speaker": "Contractor's PM", "en": "The delay is due to the late issue of the revised foundation drawings. We received them eleven days after the date in the programme.",
             "ar": "التأخير بسبب تأخّر إصدار مخططات الأساسات المعدّلة. استلمناها بعد أحد عشر يوماً من التاريخ المحدد في البرنامج."},
            {"speaker": "Engineer", "en": "Noted. But is this activity actually on the critical path? An EOT is only justified if completion is affected.",
             "ar": "أحطتُ علماً. لكن هل هذا النشاط فعلاً على المسار الحرج؟ التمديد لا يُبرَّر إلا إذا تأثّر الإنجاز."},
            {"speaker": "Contractor's PM", "en": "Yes. The foundations are a predecessor to the structural frame, so the delay flows straight through to the completion date.",
             "ar": "نعم. الأساسات نشاط سابق للهيكل الإنشائي، فالتأخير ينتقل مباشرةً إلى تاريخ الإنجاز."},
            {"speaker": "Engineer", "en": "Understood. Have you served a Notice of Claim yet? You're well aware the 28-day period is a condition precedent.",
             "ar": "مفهوم. هل قدّمتم إشعار مطالبة بعد؟ تعلمون جيداً أن مهلة الـ28 يوماً شرط واقف."},
            {"speaker": "Contractor's PM", "en": "We submitted the Notice of Claim last Sunday, within time. The fully detailed claim with particulars will follow within the 84 days.",
             "ar": "قدّمنا إشعار المطالبة الأحد الماضي، ضمن المهلة. وستتبعه المطالبة المفصّلة الكاملة بالمستندات المؤيِّدة خلال الـ84 يوماً."},
            {"speaker": "Engineer", "en": "Good. Make sure your contemporary records are watertight — daily logs, correspondence, the lot. I'll assess entitlement once I have the particulars.",
             "ar": "جيد. تأكّدوا من إحكام سجلاتكم المعاصرة — اليوميات والمراسلات وكل شيء. سأقدّر الاستحقاق حال وصول التفاصيل."},
            {"speaker": "Contractor's PM", "en": "Agreed. We're also reserving our rights on the associated prolongation costs, without prejudice to the time claim.",
             "ar": "متفقون. ونحتفظ أيضاً بحقوقنا في تكاليف الإطالة المرتبطة، دون إخلال بمطالبة الوقت."},
            {"speaker": "Engineer", "en": "Fair enough. Let's reconvene next week. In the meantime, please mitigate where you can and keep me posted.",
             "ar": "معقول. لنجتمع الأسبوع القادم. وفي غضون ذلك، خفّفوا الأثر قدر الإمكان وأبقوني على اطّلاع."},
        ],
        "glossary": {
            "behind on": "متأخر في",
            "What's driving the delay?": "ما سبب/محرّك التأخير؟",
            "late issue of the drawings": "تأخّر إصدار المخططات",
            "critical path": "المسار الحرج",
            "predecessor": "نشاط سابق (في الجدول)",
            "flows through to": "ينتقل أثره إلى",
            "Notice of Claim": "إشعار المطالبة",
            "condition precedent": "شرط واقف/مُسبق",
            "contemporary records": "السجلات المعاصرة",
            "reserving our rights": "نحتفظ بحقوقنا",
            "prolongation costs": "تكاليف الإطالة",
            "without prejudice to": "دون إخلال بـ",
            "mitigate": "يخفّف الأثر / يحدّ من الضرر",
        },
        "notes_ar": "لاحظ عبارة condition precedent — تُقال بنبرٍ على المقطعين con-DI-tion pre-CE-dent. وفي اجتماعات الموقع تُختصر كثير من العبارات: \"keep me posted\" = أبقني على اطلاع، \"the lot\" = كل شيء. الأسلوب مهني مباشر لكنه مهذّب: استخدم \"Noted\" و\"Fair enough\" و\"Agreed\" لإدارة النقاش.",
    },
    {
        "id": "D02",
        "title": "التفاوض على أمر تغييري وتقييمه",
        "scenario_ar": "نقاش بين المهندس ومدير عقود المقاول حول أمر تغييري لزيادة سُمك طبقة الأساس، وكيفية تقييمه استناداً إلى أسعار جدول الكميات.",
        "lines": [
            {"speaker": "Engineer", "en": "I'm instructing a Variation to increase the sub-base thickness from 200 to 300 millimetres across the yard.",
             "ar": "أُصدر أمر تغيير لزيادة سُمك طبقة الأساس من 200 إلى 300 مليمتر في كامل الساحة."},
            {"speaker": "Contractor's QS", "en": "Received. Shall we value it using the existing BOQ rate for sub-base, since it's the same item, just a greater quantity?",
             "ar": "استلمنا. هل نقيّمه بسعر جدول الكميات الحالي لطبقة الأساس، ما دام البند نفسه بكمية أكبر؟"},
            {"speaker": "Engineer", "en": "That's my view too. The work is of similar character and executed under similar conditions, so the contract rate applies.",
             "ar": "هذا رأيي أيضاً. العمل ذو طبيعة مماثلة ويُنفَّذ بظروف مماثلة، فينطبق سعر العقد."},
            {"speaker": "Contractor's QS", "en": "Agreed in principle. However, the extra haulage pushes us beyond the rate's assumptions. We'd claim a rate adjustment for the additional cartage.",
             "ar": "متفقون مبدئياً. غير أن النقل الإضافي يتجاوز افتراضات السعر. سنطالب بتعديل السعر مقابل النقل الإضافي."},
            {"speaker": "Engineer", "en": "Substantiate it and I'll consider a new rate for that element. For anything with no applicable rate, we'll fall back on Dayworks.",
             "ar": "أثبتوا ذلك وسأنظر في سعرٍ جديد لذلك العنصر. وما لا ينطبق عليه سعر، نلجأ فيه إلى أعمال المياومة."},
            {"speaker": "Contractor's QS", "en": "Understood. We'll submit the build-up of the new rate with our cost records, and price the rest at BOQ rates.",
             "ar": "مفهوم. سنقدّم تفصيل بناء السعر الجديد مع سجلات تكاليفنا، ونُسعّر الباقي بأسعار جدول الكميات."},
            {"speaker": "Engineer", "en": "Good. Proceed with the Variation now; we shouldn't hold up the works while we finalise the valuation.",
             "ar": "جيد. باشروا التغيير الآن؛ يجب ألا نعطّل الأعمال ريثما نُنهي التقييم."},
            {"speaker": "Contractor's QS", "en": "We'll proceed and keep the commercial side open. I'll send the valuation for your determination by Thursday.",
             "ar": "سنباشر ونُبقي الجانب التجاري مفتوحاً. سأرسل التقييم لتقديركم بحلول الخميس."},
        ],
        "glossary": {
            "instructing a Variation": "إصدار أمر تغييري",
            "sub-base": "طبقة الأساس (تحت السطحية)",
            "value it using the existing rate": "تقييمه بالسعر الحالي",
            "BOQ rate": "سعر جدول الكميات",
            "similar character / conditions": "طبيعة/ظروف مماثلة",
            "rate adjustment": "تعديل السعر",
            "haulage / cartage": "النقل (للمواد)",
            "substantiate": "يُثبت بالأدلة",
            "Dayworks": "أعمال المياومة (بالتكلفة الفعلية)",
            "build-up of the rate": "تفصيل بناء السعر",
            "hold up the works": "يعطّل الأعمال",
            "determination": "تقدير/قرار (المهندس)",
        },
        "notes_ar": "هذا حوارٌ تجاري نموذجي بين كمّيي الطرفين (QS = Quantity Surveyor). القاعدة المهنية: \"proceed and keep the commercial side open\" أي نفّذ العمل ولا تجعل الخلاف على السعر يوقفه. انتبه لنطق Variation بحرف V (لا F) والنبر vair-ee-AY-shun.",
    },
    {
        "id": "D03",
        "title": "مطالبة مرفوضة والخطوة التالية — إشعار عدم الرضا والإحالة للمجلس",
        "scenario_ar": "بعد رفض المهندس لمطالبة المقاول، يناقش الطرفان الخطوات التالية: حفظ الحقوق، وإشعار عدم الرضا، وإحالة النزاع إلى مجلس فضّ المنازعات (DAAB).",
        "lines": [
            {"speaker": "Contractor's PM", "en": "We've received your determination rejecting our claim in full. With respect, we don't accept the reasoning.",
             "ar": "استلمنا تقديركم برفض مطالبتنا بالكامل. ومع احترامنا، لا نقبل التسبيب."},
            {"speaker": "Engineer", "en": "I appreciate that. My determination stands, but of course it's not the end of the road for you.",
             "ar": "أقدّر ذلك. تقديري قائم، لكنه بالطبع ليس نهاية المطاف بالنسبة لكم."},
            {"speaker": "Contractor's PM", "en": "Indeed. We'll be issuing a Notice of Dissatisfaction within the 28-day window to preserve our position.",
             "ar": "بالفعل. سنُصدر إشعار عدم رضا خلال مهلة الـ28 يوماً للحفاظ على موقفنا."},
            {"speaker": "Engineer", "en": "That's your right under the Contract. After the NOD, the next step is to refer the Dispute to the DAAB.",
             "ar": "هذا حقكم بموجب العقد. بعد إشعار عدم الرضا، الخطوة التالية إحالة النزاع إلى مجلس فضّ المنازعات."},
            {"speaker": "Contractor's PM", "en": "Correct. We'd prefer to resolve this amicably first, but we won't let the time-bar run against us.",
             "ar": "صحيح. نفضّل حلّ الأمر ودياً أولاً، لكننا لن ندع مهلة السقوط تجري ضدّنا."},
            {"speaker": "Engineer", "en": "Sensible. The DAAB's decision will be binding on both Parties even if either side later gives a further Notice of Dissatisfaction.",
             "ar": "تصرّف حكيم. قرار المجلس سيكون ملزماً للطرفين حتى لو قدّم أحدهما لاحقاً إشعار عدم رضا آخر."},
            {"speaker": "Contractor's PM", "en": "Understood. All of this is without prejudice to our right to proceed to arbitration if the matter isn't finally settled.",
             "ar": "مفهوم. كل هذا دون إخلال بحقنا في اللجوء إلى التحكيم إذا لم تُحسم المسألة نهائياً."},
            {"speaker": "Engineer", "en": "Agreed. Let's keep the lines of communication open and try to narrow the issues before it escalates.",
             "ar": "متفقون. لنُبقِ قنوات التواصل مفتوحة ونحاول تضييق نقاط الخلاف قبل تصعيدها."},
        ],
        "glossary": {
            "determination": "تقدير/قرار (المهندس)",
            "rejecting our claim in full": "رفض مطالبتنا بالكامل",
            "with respect": "مع احترامنا (تمهيد مهذّب للاعتراض)",
            "my determination stands": "تقديري قائم/نافذ",
            "not the end of the road": "ليس نهاية المطاف",
            "Notice of Dissatisfaction (NOD)": "إشعار عدم الرضا",
            "preserve our position": "نحفظ موقفنا",
            "refer the Dispute to the DAAB": "إحالة النزاع إلى مجلس فضّ المنازعات",
            "amicably": "ودّياً",
            "time-bar": "مهلة السقوط الزمني",
            "binding on both Parties": "مُلزم للطرفين",
            "without prejudice to": "دون إخلال بـ",
            "proceed to arbitration": "اللجوء إلى التحكيم",
            "narrow the issues": "تضييق نقاط الخلاف",
        },
        "notes_ar": "هذه محادثة \"معركة\" لكنها مهذّبة جداً — هكذا يتفاوض المحترفون. لاحظ \"With respect\" و\"I appreciate that\": عبارات تلطيف تسبق الاعتراض. ومصطلح time-bar حاسم: تأخّرُ إشعارٍ يوماً واحداً قد يُسقط الحق. تدرّب على نطق dissatisfaction: dis-sat-is-FAK-shun.",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# الإملاء السمعي (Dictation) — اسمع واكتب لتدريب الأذن على الإنجليزية التعاقدية
# مرتّبة تصاعدياً في الطول والصعوبة
# ─────────────────────────────────────────────────────────────────────────────

DICTATION: list[dict] = [
    {"level": "سهل", "text": "The Contractor shall execute the Works.",
     "ar": "ينفّذ المقاولُ الأعمال."},
    {"level": "سهل", "text": "The Engineer may issue instructions.",
     "ar": "يجوز للمهندس إصدار التعليمات."},
    {"level": "سهل", "text": "Each Party shall keep the documents confidential.",
     "ar": "يحافظ كل طرف على سرية المستندات."},
    {"level": "متوسط", "text": "The Contractor shall be entitled to an extension of time.",
     "ar": "يستحق المقاول تمديداً لمدة الإنجاز."},
    {"level": "متوسط", "text": "The Employer shall pay the amount certified within fifty-six days.",
     "ar": "يسدد صاحبُ العمل المبلغ المعتمد خلال ستة وخمسين يوماً."},
    {"level": "متوسط", "text": "The Contractor shall give a Notice of Claim to the Engineer.",
     "ar": "يوجّه المقاول إشعار مطالبة إلى المهندس."},
    {"level": "متوسط", "text": "Variations may be instructed at any time before the Taking-Over Certificate.",
     "ar": "يجوز إصدار أوامر التغيير في أي وقت قبل شهادة التسلّم."},
    {"level": "صعب", "text": "Subject to the provisions of the Contract, the Engineer shall make a fair determination.",
     "ar": "مع مراعاة أحكام العقد، يُصدر المهندس تقديراً منصفاً."},
    {"level": "صعب", "text": "Notwithstanding any other provision, the total liability shall not exceed the Contract Price.",
     "ar": "على الرغم من أي حكم آخر، لا تتجاوز المسؤولية الإجمالية قيمة العقد."},
    {"level": "صعب", "text": "The Contractor shall indemnify and hold harmless the Employer against all such claims.",
     "ar": "يعوّض المقاولُ صاحبَ العمل ويُبرئه من جميع تلك المطالبات."},
    {"level": "صعب", "text": "If no Notice of Dissatisfaction is given, the decision shall become final and binding.",
     "ar": "إذا لم يُقدَّم إشعار عدم رضا، أصبح القرار نهائياً وملزماً."},
    {"level": "صعب", "text": "The Performance Security shall be valid until the Contractor has remedied any defects.",
     "ar": "يظل ضمان حسن التنفيذ سارياً حتى يُصلح المقاول أي عيوب."},
]

CATEGORIES = sorted({v["cat"] for v in VOCAB})
