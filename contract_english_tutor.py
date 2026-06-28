"""
═══════════════════════════════════════════════════════════════════════════════
Contract English Tutor — مُدرّس الإنجليزية التعاقدية للمتحدثين بالعربية
═══════════════════════════════════════════════════════════════════════════════
هدف التطبيق: تأهيلك لقراءة عقود الفيديك (FIDIC) وغيرها بالإنجليزية مباشرةً
دون الحاجة إلى ترجمة — عبر أفضل تقنيات التعليم والحفظ والنطق:

  • التكرار المتباعد (Spaced Repetition — نظام Leitner) لترسيخ المفردات
  • الاستدعاء النشط (Active Recall) عبر البطاقات والاختبارات
  • المدخل المفهوم (Comprehensible Input) عبر نصوص فيديك متدرّجة مع مسرد تفاعلي
  • التلقين الصوتي (Audio + Shadowing) عبر نطق المتصفح Web Speech API
  • الأزواج الصغرى (Minimal Pairs) لإتقان P/B و V/F والنبر
  • التعلّم بالسياق (Chunking & Collocations) — كل مصطلح في جملة عقدية حقيقية

التشغيل:  streamlit run contract_english_tutor.py
المتطلبات: streamlit  (بقية المكوّنات من مكتبة بايثون القياسية)
═══════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import json
import html
import random
from datetime import date, datetime
from pathlib import Path

import streamlit as st

import contract_english_data as data

# ─────────────────────────────────────────────────────────────────────────────
# إعداد الصفحة
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="مُدرّس الإنجليزية التعاقدية",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded",
)

PROGRESS_FILE = Path(__file__).parent / ".tutor_progress.json"

# ترتيب صناديق Leitner (بالأيام) — كلما أتقنت بطاقة انتقلت لصندوق أبطأ
LEITNER_INTERVALS = {1: 0, 2: 1, 3: 3, 4: 7, 5: 16}
MAX_BOX = 5

# ─────────────────────────────────────────────────────────────────────────────
# CSS — تخطيط RTL وبطاقات أنيقة
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
      html, body, [class*="css"] { font-family: "Segoe UI", "Tajawal", sans-serif; }
      .main .block-container { direction: rtl; text-align: right; max-width: 1100px; }
      h1, h2, h3, h4, p, li, label, .stMarkdown { direction: rtl; text-align: right; }
      section[data-testid="stSidebar"] { direction: rtl; }

      /* بطاقات */
      .ce-card {
        background: #ffffff; border: 1px solid #e3e9f0; border-radius: 16px;
        padding: 20px 24px; margin: 12px 0; box-shadow: 0 2px 10px rgba(0,48,135,.06);
      }
      .ce-hero {
        background: linear-gradient(135deg,#003087 0%,#1452b8 100%);
        color:#fff; border-radius: 20px; padding: 26px 30px; margin-bottom: 8px;
      }
      .ce-hero h1 { color:#fff; margin:0 0 6px 0; }
      .ce-hero p  { color:#dce6ff; margin:0; }

      .term-en {
        direction: ltr; text-align: left; font-size: 30px; font-weight: 700;
        color:#003087; letter-spacing:.3px;
      }
      .term-ipa { direction: ltr; text-align: left; color:#1452b8; font-size: 19px; font-family: "Times New Roman", serif; }
      .term-syl { direction: ltr; text-align: left; color:#c0392b; font-size: 17px; font-weight:600; letter-spacing:1px; }
      .en-block { direction: ltr; text-align: left; }
      .chip {
        display:inline-block; background:#eef3fb; color:#003087; border:1px solid #d4e0f2;
        border-radius:999px; padding:3px 12px; margin:3px; font-size:13px; direction:ltr;
      }
      .stat-num { font-size: 34px; font-weight:800; color:#003087; line-height:1; }
      .stat-lbl { font-size: 13px; color:#5b6b80; }
      .pill-gold { background:#FFB81C; color:#3a2a00; border-radius:999px; padding:4px 14px; font-weight:700; display:inline-block; }
      .glossary-word {
        border-bottom: 2px dotted #1452b8; cursor: help; color:#003087; font-weight:600;
      }
      blockquote {
        border-right: 4px solid #FFB81C; border-left:none; background:#fffaf0;
        padding:10px 16px; border-radius:8px;
      }
      .reading-en {
        direction: ltr; text-align: left; font-size: 19px; line-height: 2.0;
        background:#fbfcfe; border:1px solid #e3e9f0; border-radius:14px; padding:20px 24px;
      }
      table { direction: rtl; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# نطق المتصفح (Web Speech API) — تلقين صوتي بدون أي خدمة خارجية
# ─────────────────────────────────────────────────────────────────────────────
def speak_widget(text: str, key: str, height: int = 56, show_shadow: bool = True) -> None:
    """يعرض أزرار نطق (عادي/بطيء/تكرار/تظليل) تستخدم أصوات المتصفح للإنجليزية."""
    safe = json.dumps(text)  # تأمين النص لإدراجه في JavaScript
    shadow_btn = (
        '<button class="b" onclick="shadow()">🎤 استمع ثم كرّر</button>'
        if show_shadow else ""
    )
    components_html = f"""
    <div dir="ltr" style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;font-family:Segoe UI,sans-serif;">
      <style>
        .b {{ background:#003087;color:#fff;border:none;border-radius:10px;
             padding:8px 14px;font-size:14px;cursor:pointer; }}
        .b:hover {{ background:#1452b8; }}
        .b.alt {{ background:#eef3fb;color:#003087;border:1px solid #cfe; }}
        select {{ border-radius:8px;padding:6px;border:1px solid #ccd6e6; }}
      </style>
      <button class="b" onclick="say(0.95)">🔊 استمع</button>
      <button class="b alt" onclick="say(0.6)">🐢 بطيء</button>
      <button class="b alt" onclick="rep()">🔁 كرّر ×3</button>
      {shadow_btn}
      <select id="voice_{key}" class="alt" title="اختر اللهجة"></select>
    </div>
    <script>
      const TXT_{key} = {safe};
      const synth = window.speechSynthesis;
      function fill_{key}() {{
        const sel = document.getElementById("voice_{key}");
        if (!sel) return;
        const voices = synth.getVoices().filter(v => v.lang && v.lang.toLowerCase().startsWith("en"));
        if (!voices.length) return;
        sel.innerHTML = "";
        voices.forEach((v, i) => {{
          const o = document.createElement("option");
          o.value = i; o.text = v.name.replace(/Microsoft|Google/gi,"").trim() + " — " + v.lang;
          if (/UK|GB|British/i.test(v.name+v.lang)) o.selected = true;
          sel.appendChild(o);
        }});
        sel._voices = voices;
      }}
      fill_{key}();
      if (synth.onvoiceschanged !== undefined) synth.onvoiceschanged = fill_{key};
      function pick_{key}() {{
        const sel = document.getElementById("voice_{key}");
        if (sel && sel._voices && sel._voices.length) return sel._voices[sel.value || 0];
        return null;
      }}
      function utter_{key}(rate) {{
        const u = new SpeechSynthesisUtterance(TXT_{key});
        const v = pick_{key}(); if (v) {{ u.voice = v; u.lang = v.lang; }} else {{ u.lang = "en-GB"; }}
        u.rate = rate; u.pitch = 1.0;
        return u;
      }}
      function say(rate) {{ synth.cancel(); synth.speak(utter_{key}(rate)); }}
      function rep() {{
        synth.cancel();
        for (let i=0;i<3;i++) {{ synth.speak(utter_{key}(0.85)); }}
      }}
      function shadow() {{
        synth.cancel();
        const u = utter_{key}(0.8);
        u.onend = () => {{
          // فترة صمت ليكرّر المتعلّم بصوته ثم يُعاد النطق مرجعاً
          setTimeout(() => synth.speak(utter_{key}(0.8)), 2200);
        }};
        synth.speak(u);
      }}
    </script>
    """
    st.components.v1.html(components_html, height=height)


# ─────────────────────────────────────────────────────────────────────────────
# حالة التقدم (Progress / SRS state)
# ─────────────────────────────────────────────────────────────────────────────
def _today() -> str:
    return date.today().isoformat()


def default_progress() -> dict:
    return {
        "srs": {},            # en -> {"box": int, "due": "YYYY-MM-DD", "seen": int, "correct": int}
        "lessons_done": [],   # قائمة معرّفات الدروس المكتملة
        "quiz_history": [],   # سجل نتائج الاختبارات
        "xp": 0,              # نقاط الخبرة
        "streak": 0,          # أيام متتالية
        "last_active": "",    # آخر يوم نشاط
        "reading_done": [],   # نصوص القراءة المكتملة
    }


def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        try:
            p = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
            base = default_progress()
            base.update(p)
            return base
        except Exception:
            pass
    return default_progress()


def save_progress() -> None:
    try:
        PROGRESS_FILE.write_text(
            json.dumps(st.session_state.progress, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass  # في البيئات للقراءة فقط، تبقى الحالة في الجلسة


def touch_streak() -> None:
    p = st.session_state.progress
    today = _today()
    if p["last_active"] == today:
        return
    if p["last_active"]:
        last = datetime.fromisoformat(p["last_active"]).date()
        gap = (date.today() - last).days
        p["streak"] = p["streak"] + 1 if gap == 1 else 1
    else:
        p["streak"] = 1
    p["last_active"] = today
    save_progress()


def add_xp(n: int) -> None:
    st.session_state.progress["xp"] += n


# ── محرّك Leitner ────────────────────────────────────────────────────────────
def srs_entry(en: str) -> dict:
    srs = st.session_state.progress["srs"]
    if en not in srs:
        srs[en] = {"box": 1, "due": _today(), "seen": 0, "correct": 0}
    return srs[en]


def srs_review(en: str, remembered: bool) -> None:
    e = srs_entry(en)
    e["seen"] += 1
    if remembered:
        e["correct"] += 1
        e["box"] = min(MAX_BOX, e["box"] + 1)
        add_xp(5)
    else:
        e["box"] = 1
        add_xp(1)
    interval = LEITNER_INTERVALS[e["box"]]
    e["due"] = (date.today().fromordinal(date.today().toordinal() + interval)).isoformat()
    save_progress()


def due_cards() -> list[dict]:
    today = _today()
    out = []
    for v in data.VOCAB:
        e = st.session_state.progress["srs"].get(v["en"])
        if e is None or e["due"] <= today:
            out.append(v)
    return out


def mastered_count() -> int:
    return sum(1 for e in st.session_state.progress["srs"].values() if e["box"] >= 4)


# ─────────────────────────────────────────────────────────────────────────────
# تهيئة الجلسة
# ─────────────────────────────────────────────────────────────────────────────
if "progress" not in st.session_state:
    st.session_state.progress = load_progress()
if "card_idx" not in st.session_state:
    st.session_state.card_idx = 0
if "card_revealed" not in st.session_state:
    st.session_state.card_revealed = False

touch_streak()
P = st.session_state.progress


# ─────────────────────────────────────────────────────────────────────────────
# مكوّنات مساعدة للعرض
# ─────────────────────────────────────────────────────────────────────────────
def render_term_card(v: dict, key: str, with_audio: bool = True) -> None:
    st.markdown(
        f"""
        <div class="ce-card">
          <div class="term-en">{html.escape(v['en'])}</div>
          <div class="term-ipa">{html.escape(v['ipa'])}</div>
          <div class="term-syl">🗣️ {html.escape(v['syllables'])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if with_audio:
        speak_widget(v["en"], key=f"term_{key}", show_shadow=False)


def render_term_back(v: dict) -> None:
    st.markdown(f"### {v['ar']}")
    st.write(v["def_ar"])
    st.markdown(
        f"""<div class="ce-card en-block">
        <b>مثال:</b><br><span style="font-size:17px">“{html.escape(v['ex_en'])}”</span>
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown(f"**الترجمة:** {v['ex_ar']}")
    speak_widget(v["ex_en"], key=f"ex_{abs(hash(v['en']))%99999}")
    if v.get("collocations"):
        chips = " ".join(f'<span class="chip">{html.escape(c)}</span>' for c in v["collocations"])
        st.markdown(f"**متلازمات لفظية:**<br>{chips}", unsafe_allow_html=True)
    if v.get("tip"):
        st.info(f"💡 **نصيحة نطق/استخدام:** {v['tip']}")


def mcq(prefix: str, q: dict, idx: int) -> bool | None:
    """يعرض سؤال اختيار من متعدد ويعيد True/False بعد التحقق، أو None قبله."""
    key = f"{prefix}_{idx}"
    choice = st.radio(
        f"**{idx+1}. {q['q']}**",
        options=list(range(len(q["options"]))),
        format_func=lambda i: q["options"][i],
        index=None,
        key=f"radio_{key}",
    )
    if st.button("تحقّق ✅", key=f"check_{key}"):
        if choice is None:
            st.warning("اختر إجابة أولاً.")
            return None
        if choice == q["answer"]:
            st.success("إجابة صحيحة! " + q.get("explain", ""))
            return True
        st.error(
            f"غير صحيحة. الصواب: **{q['options'][q['answer']]}**\n\n{q.get('explain','')}"
        )
        return False
    return None


# ─────────────────────────────────────────────────────────────────────────────
# الشريط الجانبي — التنقّل
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📜 الإنجليزية التعاقدية")
    st.caption("مُدرّسك لقراءة الفيديك دون ترجمة")
    st.markdown(
        f"""<div style="display:flex;gap:14px;margin:10px 0;">
        <div><div class="stat-num">{P['xp']}</div><div class="stat-lbl">نقطة خبرة</div></div>
        <div><div class="stat-num">🔥 {P['streak']}</div><div class="stat-lbl">أيام متتالية</div></div>
        </div>""",
        unsafe_allow_html=True,
    )
    page = st.radio(
        "التنقّل",
        [
            "🏠 الرئيسية",
            "📚 الدروس",
            "🗂️ البطاقات والحفظ",
            "🔊 النطق واللهجة",
            "📖 معمل القراءة",
            "💬 المحادثات",
            "✍️ الإملاء السمعي",
            "📝 الاختبارات",
            "🔎 المعجم",
            "📈 تقدّمي",
        ],
        label_visibility="collapsed",
    )
    st.divider()
    n_due = len(due_cards())
    st.markdown(f"**بطاقات مستحقة اليوم:** {n_due}")
    st.markdown(f"**مصطلحات متقَنة:** {mastered_count()} / {len(data.VOCAB)}")
    st.caption("💡 ذاكر يومياً 10 دقائق — الاستمرارية أهم من الكثافة.")


# ═════════════════════════════════════════════════════════════════════════════
# الصفحات
# ═════════════════════════════════════════════════════════════════════════════

# ── 🏠 الرئيسية ──────────────────────────────────────────────────────────────
if page == "🏠 الرئيسية":
    st.markdown(
        """
        <div class="ce-hero">
          <h1>📜 مُدرّس الإنجليزية التعاقدية</h1>
          <p>تعلّم لغة العقود الإنجليزية (FIDIC وغيرها) بطريقة احترافية حتى تقرأها مباشرةً دون ترجمة.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    total_terms = len(data.VOCAB)
    seen_terms = len(P["srs"])
    c1.markdown(f'<div class="ce-card"><div class="stat-num">{total_terms}</div><div class="stat-lbl">مصطلح تعاقدي</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="ce-card"><div class="stat-num">{len(data.LESSONS)}</div><div class="stat-lbl">درس منهجي</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="ce-card"><div class="stat-num">{mastered_count()}</div><div class="stat-lbl">مصطلح متقَن</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="ce-card"><div class="stat-num">{seen_terms}</div><div class="stat-lbl">مصطلح قيد التعلّم</div></div>', unsafe_allow_html=True)

    progress_ratio = mastered_count() / total_terms if total_terms else 0
    st.markdown("#### مستوى إتقانك العام")
    st.progress(progress_ratio, text=f"{int(progress_ratio*100)}% من المصطلحات أُتقنت")

    st.markdown("### 🎯 خطة اليوم")
    plan_col1, plan_col2 = st.columns(2)
    with plan_col1:
        st.markdown(
            f"""<div class="ce-card">
            <b>1) راجع بطاقات اليوم</b><br>
            لديك <span class="pill-gold">{len(due_cards())}</span> بطاقة مستحقة للمراجعة بنظام التكرار المتباعد.<br><br>
            <b>2) أكمل درساً</b><br>
            تقدّمك في الدروس: {len(P['lessons_done'])} / {len(data.LESSONS)}.
            </div>""",
            unsafe_allow_html=True,
        )
    with plan_col2:
        st.markdown(
            """<div class="ce-card">
            <b>3) درّب أذنك ولسانك</b><br>
            اقرأ بنداً في «معمل القراءة» واستمع إليه، ثم كرّره (Shadowing).<br><br>
            <b>4) اختبر نفسك</b><br>
            خُض اختباراً قصيراً لتثبيت ما تعلّمته (Active Recall).
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("### 🧠 المنهجية التعليمية المستخدمة")
    st.markdown(
        """
        | التقنية | كيف يطبّقها التطبيق |
        |---|---|
        | **التكرار المتباعد (SRS)** | بطاقات بنظام Leitner تُعيد عرض المصطلح قبيل نسيانه تماماً |
        | **الاستدعاء النشط** | تكشف الإجابة بنفسك ثم تقيّم تذكّرك؛ اختبارات بعد كل درس |
        | **المدخل المفهوم (i+1)** | نصوص فيديك متدرّجة الصعوبة مع مسرد عند الطلب |
        | **التلقين الصوتي + الـShadowing** | نطق المتصفح يسمعك الكلمة والجملة، وتكرّرها خلفه |
        | **الأزواج الصغرى** | تدريبات P/B و V/F والنبر الخاصة بالمتحدث العربي |
        | **التعلّم بالسياق** | كل مصطلح داخل جملة عقدية حقيقية مع متلازماته اللفظية |
        """
    )
    st.success("ابدأ الآن من القائمة الجانبية — أنصحك بالترتيب: الدروس ← البطاقات ← معمل القراءة.")

# ── 📚 الدروس ────────────────────────────────────────────────────────────────
elif page == "📚 الدروس":
    st.header("📚 الدروس المنهجية")
    st.caption("منهج متدرّج من الأساس إلى قراءة بنود الفيديك الكاملة.")

    titles = [f"{l['id']} — {l['title']}  ({l['level']})" for l in data.LESSONS]
    # علّم المكتمل
    titles = [
        ("✅ " if data.LESSONS[i]["id"] in P["lessons_done"] else "") + t
        for i, t in enumerate(titles)
    ]
    sel = st.selectbox("اختر الدرس:", range(len(data.LESSONS)), format_func=lambda i: titles[i])
    lesson = data.LESSONS[sel]

    st.markdown(f"## {lesson['title']}")
    st.markdown(f"<span class='pill-gold'>{lesson['level']}</span>", unsafe_allow_html=True)
    with st.expander("🎯 أهداف الدرس", expanded=True):
        for o in lesson["objectives"]:
            st.markdown(f"- {o}")

    st.markdown(lesson["content"])

    st.divider()
    st.markdown("### 📝 تحقّق من فهمك")
    score = 0
    answered = 0
    for i, q in enumerate(lesson["quiz"]):
        res = mcq(f"lesson_{lesson['id']}", q, i)
        if res is not None:
            answered += 1
            score += 1 if res else 0
        st.divider()

    if st.button("✅ أنهيتُ هذا الدرس", type="primary"):
        if lesson["id"] not in P["lessons_done"]:
            P["lessons_done"].append(lesson["id"])
            add_xp(20)
            save_progress()
            st.balloons()
            st.success("أُحسنت! تم تسجيل إكمال الدرس (+20 نقطة خبرة).")
        else:
            st.info("سبق أن أكملت هذا الدرس.")

# ── 🗂️ البطاقات والحفظ ──────────────────────────────────────────────────────
elif page == "🗂️ البطاقات والحفظ":
    st.header("🗂️ البطاقات التعليمية — التكرار المتباعد")
    st.caption("نظام Leitner: تذكّرتها ⇦ تتباعد. نسيتها ⇦ تعود قريباً. هكذا يثبت الحفظ بأقل جهد.")

    mode = st.radio(
        "ماذا تراجع؟",
        ["المستحقّة اليوم (موصى به)", "كل المصطلحات", "حسب التصنيف"],
        horizontal=True,
    )
    if mode == "حسب التصنيف":
        cat = st.selectbox("التصنيف:", data.CATEGORIES)
        deck = [v for v in data.VOCAB if v["cat"] == cat]
    elif mode == "كل المصطلحات":
        deck = list(data.VOCAB)
    else:
        deck = due_cards()

    if not deck:
        st.success("🎉 لا توجد بطاقات مستحقة الآن — راجعت كل شيء! عُد لاحقاً أو اختر «كل المصطلحات».")
    else:
        if st.session_state.card_idx >= len(deck):
            st.session_state.card_idx = 0
        v = deck[st.session_state.card_idx]

        st.progress(
            (st.session_state.card_idx + 1) / len(deck),
            text=f"بطاقة {st.session_state.card_idx + 1} من {len(deck)}",
        )

        render_term_card(v, key=f"flash_{st.session_state.card_idx}")

        if not st.session_state.card_revealed:
            if st.button("🔄 اكشف المعنى", type="primary", use_container_width=True):
                st.session_state.card_revealed = True
                st.rerun()
            st.caption("جرّب أن تستحضر المعنى والنطق من ذاكرتك أولاً، ثم اكشف.")
        else:
            render_term_back(v)
            st.divider()
            st.markdown("**هل تذكّرت المعنى والنطق؟**")
            col_y, col_n = st.columns(2)
            if col_y.button("✅ نعم، تذكّرت", use_container_width=True):
                srs_review(v["en"], True)
                st.session_state.card_revealed = False
                st.session_state.card_idx += 1
                st.rerun()
            if col_n.button("❌ لا، أعدها قريباً", use_container_width=True):
                srs_review(v["en"], False)
                st.session_state.card_revealed = False
                st.session_state.card_idx += 1
                st.rerun()

# ── 🔊 النطق واللهجة ─────────────────────────────────────────────────────────
elif page == "🔊 النطق واللهجة":
    st.header("🔊 مختبر النطق واللهجة")
    st.caption("درّب لسانك على أصوات الإنجليزية الصعبة على العرب، بنطقٍ من المتصفح وتدريبات الأزواج الصغرى.")

    tab1, tab2 = st.tabs(["🎯 تحديات نطق العربي", "📣 نطق المصطلحات"])

    with tab1:
        st.info("ضع سمّاعتك، واضغط «استمع» ثم كرّر بصوتك. الزر «استمع ثم كرّر» يترك لك فجوة صمت للترديد.")
        for i, ch in enumerate(data.PRONUNCIATION_CHALLENGES):
            with st.expander(f"{i+1}. {ch['title']}", expanded=(i == 0)):
                st.markdown(ch["ar"])
                st.markdown("**أمثلة:**")
                for w, meaning in ch["pairs"]:
                    cc1, cc2 = st.columns([3, 2])
                    with cc1:
                        st.markdown(f'<div class="en-block"><b style="font-size:18px">{html.escape(w)}</b></div>', unsafe_allow_html=True)
                        # انطق الكلمة الإنجليزية الأولى فقط (قبل أي شرح بين قوسين)
                        spoken = w.split("(")[0].split("→")[0].strip()
                        speak_widget(spoken, key=f"ch{i}_{abs(hash(w))%99999}", show_shadow=False, height=48)
                    with cc2:
                        st.caption(meaning)
                st.markdown("---")
                st.markdown("**جملة التدريب (Drill):**")
                st.markdown(f'<div class="reading-en">{html.escape(ch["drill"])}</div>', unsafe_allow_html=True)
                speak_widget(ch["drill"], key=f"drill_{i}")

    with tab2:
        st.write("اختر تصنيفاً واستمع إلى نطق كل مصطلح مع تقطيع مقاطعه ونبره.")
        cat = st.selectbox("التصنيف:", data.CATEGORIES, key="pron_cat")
        for v in [x for x in data.VOCAB if x["cat"] == cat]:
            st.markdown(
                f"""<div class="ce-card">
                <span class="term-en" style="font-size:22px">{html.escape(v['en'])}</span>
                &nbsp;<span class="term-ipa">{html.escape(v['ipa'])}</span><br>
                <span class="term-syl">🗣️ {html.escape(v['syllables'])}</span> &nbsp; — &nbsp; {html.escape(v['ar'])}
                </div>""",
                unsafe_allow_html=True,
            )
            speak_widget(v["en"], key=f"pron_{abs(hash(v['en']))%99999}", show_shadow=False, height=48)
            if v.get("tip"):
                st.caption("💡 " + v["tip"])

# ── 📖 معمل القراءة ──────────────────────────────────────────────────────────
elif page == "📖 معمل القراءة":
    st.header("📖 معمل القراءة — بنود بأسلوب الفيديك")
    st.caption("اقرأ النص الإنجليزي أولاً وحاول فهمه دون ترجمة. استعن بالمسرد عند الحاجة فقط، ثم اكشف الترجمة لتتحقّق.")

    titles = [f"{r['id']} — {r['title']}  {r['difficulty']}" for r in data.READING_PASSAGES]
    sel = st.selectbox("اختر النص:", range(len(data.READING_PASSAGES)), format_func=lambda i: titles[i])
    r = data.READING_PASSAGES[sel]

    st.markdown(f"### {r['title']}")
    st.markdown(f"<span class='pill-gold'>{r['difficulty']}</span>", unsafe_allow_html=True)

    st.markdown(f'<div class="reading-en">{html.escape(r["text"])}</div>', unsafe_allow_html=True)
    speak_widget(r["text"], key=f"read_{r['id']}")

    cols = st.columns(2)
    with cols[0]:
        with st.expander("📔 المسرد التفاعلي (انقر لكشف معاني الكلمات الصعبة)"):
            for term, meaning in r["glossary"].items():
                gc1, gc2 = st.columns([2, 3])
                gc1.markdown(f'<div class="en-block"><b>{html.escape(term)}</b></div>', unsafe_allow_html=True)
                gc2.markdown(meaning)
    with cols[1]:
        with st.expander("🌐 الترجمة الكاملة (لا تكشفها إلا بعد محاولتك)"):
            st.markdown(r["translation"])

    st.divider()
    st.markdown("### 📝 أسئلة الاستيعاب")
    for i, q in enumerate(r["questions"]):
        mcq(f"read_{r['id']}", q, i)
        st.divider()

    if st.button("✅ أنهيتُ هذا النص", type="primary"):
        if r["id"] not in P["reading_done"]:
            P["reading_done"].append(r["id"])
            add_xp(15)
            save_progress()
            st.success("ممتاز! (+15 نقطة خبرة). كل نص تقرؤه بلا ترجمة يقرّبك من الاستقلال التام.")

# ── 💬 المحادثات ─────────────────────────────────────────────────────────────
elif page == "💬 المحادثات":
    st.header("💬 محادثات مهنية — لغة العقود المنطوقة")
    st.caption("درّب أذنك على الإنجليزية التعاقدية كما تُقال في اجتماعات الموقع والمفاوضات.")

    dialogues = getattr(data, "DIALOGUES", [])
    if not dialogues:
        st.info("لا توجد محادثات متاحة حالياً.")
    else:
        titles = [f"{d['id']} — {d['title']}" for d in dialogues]
        sel = st.selectbox("اختر المحادثة:", range(len(dialogues)), format_func=lambda i: titles[i])
        d = dialogues[sel]

        st.markdown(f"### {d['title']}")
        st.info("🎬 " + d["scenario_ar"])

        show_ar = st.toggle("إظهار الترجمة العربية تحت كل سطر", value=False)
        st.caption("جرّب أولاً الاستماع والفهم دون ترجمة، ثم فعّل الترجمة للتحقق.")

        for j, line in enumerate(d["lines"]):
            st.markdown(
                f'<div class="ce-card en-block" style="padding:14px 18px">'
                f'<b style="color:#1452b8">{html.escape(line["speaker"])}:</b> '
                f'<span style="font-size:17px">{html.escape(line["en"])}</span></div>',
                unsafe_allow_html=True,
            )
            speak_widget(line["en"], key=f"dlg_{d['id']}_{j}", show_shadow=False, height=48)
            if show_ar:
                st.markdown(f"<div style='color:#5b6b80'>↳ {line['ar']}</div>", unsafe_allow_html=True)

        with st.expander("📔 مسرد المحادثة"):
            for term, meaning in d["glossary"].items():
                gc1, gc2 = st.columns([2, 3])
                gc1.markdown(f'<div class="en-block"><b>{html.escape(term)}</b></div>', unsafe_allow_html=True)
                gc2.markdown(meaning)
        if d.get("notes_ar"):
            st.success("🗒️ " + d["notes_ar"])

# ── ✍️ الإملاء السمعي ────────────────────────────────────────────────────────
elif page == "✍️ الإملاء السمعي":
    import difflib
    import re as _re

    st.header("✍️ الإملاء السمعي — درّب أذنك")
    st.caption("استمع إلى الجملة (بلا نص)، اكتب ما سمعته، ثم تحقّق. أقوى تمرين لربط الصوت بالكلمة المكتوبة.")

    def _norm(s: str) -> list[str]:
        s = s.lower().replace("-", " ")
        s = _re.sub(r"[^a-z0-9\s]", " ", s)
        return s.split()

    levels = ["الكل"] + sorted({d["level"] for d in data.DICTATION}, key=lambda x: ["سهل", "متوسط", "صعب"].index(x))
    lvl = st.selectbox("المستوى:", levels)
    pool = [d for d in data.DICTATION if lvl == "الكل" or d["level"] == lvl]

    if "dict_item" not in st.session_state or st.session_state.get("dict_lvl") != lvl:
        st.session_state.dict_item = random.choice(pool)
        st.session_state.dict_lvl = lvl
    if st.button("🎲 عبارة جديدة"):
        st.session_state.dict_item = random.choice(pool)
        st.session_state.pop("dict_answer", None)

    item = st.session_state.dict_item
    st.markdown(f"<span class='pill-gold'>{item['level']}</span>", unsafe_allow_html=True)
    st.markdown("**1) استمع (يمكنك الإبطاء والتكرار):**")
    speak_widget(item["text"], key=f"dict_{abs(hash(item['text']))%99999}", show_shadow=False)

    answer = st.text_input("2) اكتب ما سمعته بالإنجليزية:", key="dict_answer", placeholder="type what you hear...")
    cda, cdb = st.columns(2)
    check = cda.button("تحقّق ✅", type="primary")
    reveal = cdb.button("👁️ اكشف النص")

    if check and answer.strip():
        target_words = _norm(item["text"])
        user_words = _norm(answer)
        sm = difflib.SequenceMatcher(a=user_words, b=target_words)
        # أعد بناء النص الهدف مع تلوين الكلمات الصحيحة/المفقودة
        rendered = []
        correct = 0
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                for w in target_words[j1:j2]:
                    rendered.append(f'<span style="color:#1a8a3a;font-weight:600">{w}</span>')
                correct += (j2 - j1)
            elif tag in ("replace", "delete", "insert"):
                for w in target_words[j1:j2]:
                    rendered.append(f'<span style="color:#c0392b;text-decoration:underline">{w}</span>')
        pct = int(correct / max(1, len(target_words)) * 100)
        st.markdown(f"### دقّتك: {pct}%  ({correct}/{len(target_words)} كلمة)")
        st.markdown(
            '<div class="reading-en">' + " ".join(rendered) + "</div>",
            unsafe_allow_html=True,
        )
        st.caption("🟢 أخضر = أصبتها · 🔴 أحمر = فاتتك أو أخطأتها")
        st.markdown(f"**الترجمة:** {item['ar']}")
        add_xp(max(1, pct // 20))
        P["quiz_history"].append({"date": _today(), "type": "dictation", "score": correct, "total": len(target_words)})
        save_progress()
        if pct == 100:
            st.success("مطابقة تامة! 🎯")
            st.balloons()
    elif check:
        st.warning("اكتب ما سمعته أولاً.")

    if reveal:
        st.info(f"**النص:** {item['text']}")
        st.markdown(f"**الترجمة:** {item['ar']}")

# ── 📝 الاختبارات ────────────────────────────────────────────────────────────
elif page == "📝 الاختبارات":
    st.header("📝 الاختبارات — ثبّت ما تعلّمت")
    quiz_type = st.radio(
        "نوع الاختبار:",
        ["مطابقة المصطلح ↔ المعنى", "النطق: أي تقطيع صحيح؟", "أسئلة الدروس المجمّعة"],
        horizontal=False,
    )

    if "quiz_pool" not in st.session_state or st.button("🔁 أسئلة جديدة"):
        st.session_state.quiz_pool = random.sample(data.VOCAB, k=min(6, len(data.VOCAB)))
        st.session_state.quiz_submitted = False

    if quiz_type == "مطابقة المصطلح ↔ المعنى":
        st.caption("اختر المعنى العربي الصحيح لكل مصطلح إنجليزي.")
        pool = st.session_state.quiz_pool
        score = 0
        with st.form("match_form"):
            answers = {}
            for i, v in enumerate(pool):
                distractors = random.sample([x for x in data.VOCAB if x["en"] != v["en"]], 3)
                opts = distractors + [v]
                random.shuffle(opts)
                labels = [o["ar"] for o in opts]
                st.markdown(f'<div class="en-block"><b style="font-size:18px">{i+1}. {html.escape(v["en"])}</b></div>', unsafe_allow_html=True)
                answers[i] = (st.radio("المعنى:", labels, index=None, key=f"m_{i}", label_visibility="collapsed"), v["ar"])
            submitted = st.form_submit_button("صحّح الاختبار", type="primary")
        if submitted:
            for i, (chosen, correct) in answers.items():
                if chosen == correct:
                    score += 1
                    st.success(f"{i+1}. ✅ {pool[i]['en']} = {correct}")
                else:
                    st.error(f"{i+1}. ❌ {pool[i]['en']} → الصواب: {correct}")
            pct = int(score / len(pool) * 100)
            add_xp(score * 3)
            P["quiz_history"].append({"date": _today(), "type": "match", "score": score, "total": len(pool)})
            save_progress()
            st.markdown(f"## النتيجة: {score}/{len(pool)} ({pct}%)")
            if pct >= 80:
                st.balloons()

    elif quiz_type == "النطق: أي تقطيع صحيح؟":
        st.caption("اختر التقطيع المقطعي الصحيح مع موضع النبر (الحرف الكبير = المقطع المنبور).")
        pool = st.session_state.quiz_pool
        score = 0
        with st.form("syl_form"):
            answers = {}
            for i, v in enumerate(pool):
                others = random.sample([x["syllables"] for x in data.VOCAB if x["syllables"] != v["syllables"]], 3)
                opts = others + [v["syllables"]]
                random.shuffle(opts)
                st.markdown(f'<div class="en-block"><b style="font-size:18px">{i+1}. {html.escape(v["en"])}</b> <span class="term-ipa">{html.escape(v["ipa"])}</span></div>', unsafe_allow_html=True)
                speak_widget(v["en"], key=f"qsyl_{i}", show_shadow=False, height=46)
                answers[i] = (st.radio("التقطيع:", opts, index=None, key=f"s_{i}", label_visibility="collapsed"), v["syllables"])
            submitted = st.form_submit_button("صحّح الاختبار", type="primary")
        if submitted:
            for i, (chosen, correct) in answers.items():
                if chosen == correct:
                    score += 1
                    st.success(f"{i+1}. ✅ {correct}")
                else:
                    st.error(f"{i+1}. ❌ الصواب: {correct}")
            add_xp(score * 3)
            P["quiz_history"].append({"date": _today(), "type": "syllables", "score": score, "total": len(pool)})
            save_progress()
            st.markdown(f"## النتيجة: {score}/{len(pool)}")

    else:
        st.caption("أسئلة مختارة عشوائياً من جميع الدروس.")
        all_q = []
        for l in data.LESSONS:
            for q in l["quiz"]:
                all_q.append((l["title"], q))
        if "lesson_quiz_pool" not in st.session_state or st.button("🔁 جدّد أسئلة الدروس"):
            st.session_state.lesson_quiz_pool = random.sample(all_q, k=min(6, len(all_q)))
        for i, (ltitle, q) in enumerate(st.session_state.lesson_quiz_pool):
            st.caption(f"من درس: {ltitle}")
            mcq("agg", q, i)
            st.divider()

# ── 🔎 المعجم ────────────────────────────────────────────────────────────────
elif page == "🔎 المعجم":
    st.header("🔎 معجم المصطلحات التعاقدية")
    st.caption(f"{len(data.VOCAB)} مصطلحاً مع النطق والتعريف والمثال — ابحث بالعربي أو الإنجليزي.")

    colf1, colf2 = st.columns([3, 2])
    query = colf1.text_input("🔍 بحث:", placeholder="مثال: claim أو مطالبة أو notice")
    cat_filter = colf2.selectbox("التصنيف:", ["كل التصنيفات"] + data.CATEGORIES)

    results = []
    for v in data.VOCAB:
        if cat_filter != "كل التصنيفات" and v["cat"] != cat_filter:
            continue
        if query:
            blob = " ".join([v["en"], v["ar"], v["def_ar"], v["cat"]]).lower()
            if query.lower() not in blob:
                continue
        results.append(v)

    st.markdown(f"**النتائج: {len(results)}**")
    for v in results:
        with st.expander(f"{v['en']}  —  {v['ar']}   ·   {v['cat']}"):
            render_term_card(v, key=f"dict_{abs(hash(v['en']))%99999}")
            render_term_back(v)

# ── 📈 تقدّمي ────────────────────────────────────────────────────────────────
elif page == "📈 تقدّمي":
    st.header("📈 تقدّمي")

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="ce-card"><div class="stat-num">{P["xp"]}</div><div class="stat-lbl">نقطة خبرة</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="ce-card"><div class="stat-num">🔥 {P["streak"]}</div><div class="stat-lbl">أيام متتالية</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="ce-card"><div class="stat-num">{len(P["lessons_done"])}/{len(data.LESSONS)}</div><div class="stat-lbl">دروس مكتملة</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="ce-card"><div class="stat-num">{mastered_count()}/{len(data.VOCAB)}</div><div class="stat-lbl">مصطلحات متقَنة</div></div>', unsafe_allow_html=True)

    st.markdown("### توزيع المصطلحات على صناديق التكرار المتباعد")
    box_counts = {b: 0 for b in range(1, MAX_BOX + 1)}
    for e in P["srs"].values():
        box_counts[e["box"]] = box_counts.get(e["box"], 0) + 1
    box_labels = {1: "صندوق 1 (يومي)", 2: "صندوق 2 (كل يوم)", 3: "صندوق 3 (كل 3 أيام)", 4: "صندوق 4 (أسبوعي)", 5: "صندوق 5 (متقَن)"}
    for b in range(1, MAX_BOX + 1):
        st.markdown(f"**{box_labels[b]}** — {box_counts[b]} مصطلح")
        st.progress(box_counts[b] / max(1, len(data.VOCAB)))

    st.markdown("### سجلّ الاختبارات الأخيرة")
    if P["quiz_history"]:
        for h in reversed(P["quiz_history"][-10:]):
            st.markdown(f"- {h['date']} · {h['type']} · {h['score']}/{h['total']}")
    else:
        st.caption("لم تخض اختبارات بعد.")

    st.divider()
    st.markdown("### 💾 حفظ تقدّمك / نقله بين الأجهزة")
    st.caption("في البيئات السحابية قد يُعاد ضبط التخزين؛ نزّل تقدّمك واحتفظ به، وارفعه لاحقاً للمتابعة.")
    colx1, colx2 = st.columns(2)
    with colx1:
        st.download_button(
            "⬇️ تنزيل ملف التقدّم (JSON)",
            data=json.dumps(P, ensure_ascii=False, indent=2),
            file_name="contract_english_progress.json",
            mime="application/json",
        )
    with colx2:
        up = st.file_uploader("⬆️ رفع ملف تقدّم سابق", type=["json"])
        if up is not None:
            try:
                loaded = json.loads(up.read().decode("utf-8"))
                base = default_progress()
                base.update(loaded)
                st.session_state.progress = base
                save_progress()
                st.success("تم استيراد التقدّم. أعد تحميل الصفحة.")
            except Exception as e:
                st.error(f"ملف غير صالح: {e}")

    st.divider()
    if st.button("🗑️ تصفير كل التقدّم", type="secondary"):
        st.session_state.progress = default_progress()
        save_progress()
        st.warning("تم تصفير التقدّم.")
