"""
TenderLens Pro | By Eng. Ahmed Almaamari
Naval Blue #003087 | Gold #FFB81C
─────────────────────────────────────────────────────────────────────────────
Hardened Edition — OpenAI Direct Integration
─────────────────────────────────────────────────────────────────────────────
Modules:
  1. Tender Analysis Engine       2. Proposal Compliance Review
  3. BOQ Quantities Extractor     4. Smart Clause Tracker
  5. Milestone & Deadline Tracker 6. Go / No-Go Decision Dashboard
  7. Multi-Tender Comparison      8. Reference-Based Document Generator
"""

import streamlit as st
import pdfplumber
import io
import os
import json
import re
import time
import math
import html as _html
import logging
from datetime import datetime
from pathlib import Path
import pandas as pd

try:
    import tiktoken
except Exception:
    tiktoken = None

try:
    from openai import OpenAI, APIError, RateLimitError, APITimeoutError, AuthenticationError
except ImportError:
    raise ImportError("openai>=1.40 required. Run: pip install --upgrade openai")

# ─────────────────────────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("TenderLens")

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
# Stable default configuration for Streamlit Cloud.
# GPT-5.x models remain selectable manually, but the default uses the most stable
# Chat Completions model to avoid fallback latency when an account lacks GPT-5 access.
DEFAULT_MODEL = "gpt-4o"
FALLBACK_MODEL = "gpt-4o-mini"
AVAILABLE_MODELS = ["gpt-4o", "gpt-4o-mini", "gpt-5.5", "gpt-5.4", "gpt-5.4-mini"]
DEFAULT_REASONING_EFFORT = "xhigh"
MAX_FILE_SIZE_MB = 50
MAX_TOKENS_PER_REQ = 8192
API_TIMEOUT = 120.0
API_MAX_RETRIES = 3

# Conservative token budgets to protect Streamlit Cloud and OpenAI rate limits.
# These are intentionally lower than model context limits because organization TPM/RPM
# limits can be hit before the model context window is hit.
MAX_INPUT_TOKENS_PER_FILE = 12_000
MAX_SYNTHESIS_INPUT_TOKENS = 45_000
MAX_REVIEW_CONTEXT_TOKENS = 60_000
MAX_FEEDBACK_CONTEXT_TOKENS = 50_000
MAX_CHAT_CONTEXT_TOKENS = 35_000
MAX_DOCGEN_CONTEXT_TOKENS = 35_000
# Tender analysis uses one focused pass when total extracted context fits this budget.
# If the uploaded tender set is larger, the app automatically uses staged extraction
# to avoid losing owner requirements or triggering OpenAI request-size/rate-limit errors.
MAX_SINGLE_PASS_TENDER_TOKENS = 48_000
TENDER_ANALYSIS_SLEEP_SECONDS = 1.5
CSV_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TenderLens Pro | By Eng. Ahmed Almaamari",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS — Navy Blue + Gold Design System
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif !important; }
section[data-testid="stSidebar"] { background: #001a54 !important; border-right: 3px solid #FFB81C; }
section[data-testid="stSidebar"] * { color: #E8EDF7 !important; }
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stFileUploader label,
section[data-testid="stSidebar"] .stTextInput label {
    color: #FFB81C !important; font-weight: 700 !important; font-size: 0.82rem !important;
    text-transform: uppercase; letter-spacing: 0.5px;
}
section[data-testid="stSidebar"] hr { border-color: #FFB81C44 !important; }
.masthead {
    background: linear-gradient(135deg, #003087 0%, #001a54 100%);
    border-bottom: 4px solid #FFB81C; border-radius: 10px;
    padding: 22px 32px; margin-bottom: 28px;
    display: flex; align-items: center; justify-content: space-between;
}
.masthead-title { color: #FFB81C; font-size: 1.9rem; font-weight: 800; margin: 0; line-height: 1.1; }
.masthead-sub { color: #93A5C8; font-size: 0.82rem; margin: 4px 0 0; }
.masthead-badge {
    background: #FFB81C22; border: 1px solid #FFB81C55; color: #FFB81C;
    border-radius: 20px; padding: 5px 14px; font-size: 0.72rem;
    font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase;
}
.card { background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 5px solid #003087;
    border-radius: 8px; padding: 20px 24px; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,.05); }
.card-gold { border-left-color: #FFB81C; }
.card-red  { border-left-color: #E53E3E; }
.card-green{ border-left-color: #38A169; }
.card h4 { color: #003087; font-size: 0.78rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.7px; margin: 0 0 10px; }
.card-gold h4 { color: #92400E; }
.card-red  h4 { color: #C53030; }
.card-green h4 { color: #276749; }
.card p, .card li { color: #2D3748; font-size: 0.88rem; line-height: 1.7; margin: 0; }
.chips { margin: 4px 0 12px; }
.chip { display: inline-block; background: #EBF4FF; color: #003087; border: 1px solid #BEE3F8;
    border-radius: 20px; padding: 3px 12px; font-size: 0.75rem; font-weight: 600; margin: 2px 4px 2px 0; }
.chip-gold { background:#FFFBEB; color:#92400E; border-color:#FDE68A; }
.chip-red  { background:#FFF5F5; color:#C53030; border-color:#FEB2B2; }
.chip-green{ background:#F0FFF4; color:#276749; border-color:#9AE6B4; }
.chip-gray { background:#F7FAFC; color:#4A5568; border-color:#CBD5E0; }
.score-ring { width: 110px; height: 110px; border-radius: 50%; display: flex;
    flex-direction: column; align-items: center; justify-content: center;
    margin: 0 auto 10px; font-weight: 800; }
.score-high  { background:#F0FFF4; border: 6px solid #38A169; color:#276749; }
.score-mid   { background:#FFFBEB; border: 6px solid #D69E2E; color:#92400E; }
.score-low   { background:#FFF5F5; border: 6px solid #E53E3E; color:#C53030; }
.score-num   { font-size: 1.8rem; line-height: 1; }
.score-label { font-size: 0.62rem; color:#718096; font-weight:500; margin-top:2px; }
div[data-testid="stProgress"] > div > div { background: linear-gradient(90deg, #003087, #0050D0) !important; }
.stTabs [data-baseweb="tab-list"] { gap: 6px; background: transparent; border-bottom: 2px solid #E2E8F0; padding-bottom: 0; }
.stTabs [data-baseweb="tab"] { background: #F0F4F8; border-radius: 6px 6px 0 0; padding: 8px 18px;
    font-size: 0.83rem; font-weight: 600; color: #4A5568; border: 1px solid #E2E8F0; border-bottom: none; }
.stTabs [aria-selected="true"] { background: #003087 !important; color: #FFB81C !important; }
.stButton > button { background: #003087; color: #FFB81C; border: 2px solid #003087; border-radius: 7px;
    font-weight: 700; font-size: 0.88rem; padding: 10px 20px; transition: all .15s; }
.stButton > button:hover { background: #FFB81C; color: #003087; border-color: #FFB81C; }
.stDownloadButton > button { background: transparent; color: #003087; border: 2px solid #003087;
    border-radius: 7px; font-weight: 600; font-size: 0.82rem; }
.stDownloadButton > button:hover { background: #003087; color: #FFB81C; }
div[data-testid="stAlert"] { border-radius: 7px; font-size: 0.87rem; }
.chat-user { background: #003087; color: #fff; padding: 10px 16px; border-radius: 18px 18px 4px 18px;
    font-size: 0.86rem; margin: 6px 0 2px auto; max-width: 80%; width: fit-content; margin-left: auto; }
.chat-bot { background: #F7FAFC; color: #1A202C; border: 1px solid #E2E8F0;
    padding: 10px 16px; border-radius: 18px 18px 18px 4px; font-size: 0.86rem;
    margin: 2px 0 6px 0; max-width: 80%; white-space: pre-wrap; line-height: 1.65; }
.chat-lbl { font-size: 0.68rem; color:#718096; font-weight:600; margin-bottom:2px; }
.file-item { background: #F7FAFC; border: 1px solid #E2E8F0; border-left: 3px solid #FFB81C;
    border-radius: 5px; padding: 8px 14px; margin-bottom: 6px; font-size: 0.82rem;
    color: #2D3748; font-weight: 500; }
.api-status-ok  { background:#F0FDF4; border:1px solid #86EFAC; color:#166534;
    padding:8px 12px; border-radius:6px; font-size:0.78rem; font-weight:600; }
.api-status-bad { background:#FEF2F2; border:1px solid #FCA5A5; color:#991B1B;
    padding:8px 12px; border-radius:6px; font-size:0.78rem; font-weight:600; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SAFETY UTILITIES
# ─────────────────────────────────────────────────────────────────────────────
def safe_html(text) -> str:
    """تهريب آمن للنصوص قبل إدراجها في HTML."""
    if text is None:
        return ""
    return _html.escape(str(text))


def safe_truncate(text: str, max_chars: int) -> str:
    """قطع النص دون كسر الكلمات العربية."""
    if not text or len(text) <= max_chars:
        return text or ""
    cut = text[:max_chars]
    for sep in ["\n\n", ". ", "۔ ", "؟ ", "? ", "\n"]:
        idx = cut.rfind(sep)
        if idx > max_chars * 0.7:
            return cut[: idx + len(sep)] + " […]"
    return cut + " […]"


def _get_token_encoder(model: str | None = None):
    """
    Return a tiktoken encoder when available.
    Falls back safely because some future model names may not be known by tiktoken yet.
    """
    if tiktoken is None:
        return None
    model = model or DEFAULT_MODEL
    try:
        return tiktoken.encoding_for_model(model)
    except Exception:
        for enc_name in ("o200k_base", "cl100k_base"):
            try:
                return tiktoken.get_encoding(enc_name)
            except Exception:
                continue
    return None


def count_tokens(text: str, model: str | None = None) -> int:
    """
    Count tokens for OpenAI requests.
    If tiktoken is not installed, use a conservative Arabic-safe approximation.
    """
    text = text or ""
    enc = _get_token_encoder(model)
    if enc is not None:
        try:
            return len(enc.encode(text))
        except Exception:
            pass
    # Conservative fallback: Arabic and mixed tender text often tokenizes denser than English.
    return max(1, math.ceil(len(text) / 2.7))


def truncate_to_token_budget(text: str, max_tokens: int, model: str | None = None) -> str:
    """Truncate text by token budget rather than by raw characters."""
    text = text or ""
    if max_tokens <= 0:
        return ""

    enc = _get_token_encoder(model)
    if enc is not None:
        try:
            toks = enc.encode(text)
            if len(toks) <= max_tokens:
                return text
            return enc.decode(toks[:max_tokens]) + " […]"
        except Exception:
            pass

    # Fallback char budget when tiktoken is not installed.
    approx_chars = int(max_tokens * 2.7)
    return safe_truncate(text, approx_chars)


def build_context_bundle(
    texts: dict,
    label: str,
    max_total_tokens: int,
    per_file_tokens: int = MAX_INPUT_TOKENS_PER_FILE,
    model: str | None = None,
) -> str:
    """
    Build a multi-file context under a hard token budget.
    This prevents Request too large / TPM spikes when users upload many RFP files.
    """
    if not texts:
        return ""

    model = model or st.session_state.get("openai_model", DEFAULT_MODEL)
    parts: list[str] = []
    used = 0
    header_reserve = 120

    for name, txt in texts.items():
        remaining = max_total_tokens - used - header_reserve
        if remaining <= 500:
            parts.append("\n[تم إيقاف إضافة ملفات أخرى لأن ميزانية الرموز المحددة امتلأت.]\n")
            break

        chunk_budget = max(500, min(per_file_tokens, remaining))
        body = truncate_to_token_budget(txt or "", chunk_budget, model=model)
        part = f"=== {label}: {name} ===\n{body}"
        used += count_tokens(part, model=model)
        parts.append(part)

    return "\n\n".join(parts)


def sanitize_csv_cell(value):
    """Prevent CSV Formula Injection when opening exports in Excel."""
    if isinstance(value, str) and value and value[0] in CSV_FORMULA_PREFIXES:
        return "'" + value
    return value


def sanitize_dataframe_for_csv(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of DataFrame with formula-like cells safely escaped for CSV."""
    if df is None or df.empty:
        return df
    safe_df = df.copy()
    for col in safe_df.columns:
        safe_df[col] = safe_df[col].map(sanitize_csv_cell)
    return safe_df


def release_heavy_state_keys(*keys: str) -> None:
    """Delete heavy session_state entries safely to reduce Streamlit Cloud RAM pressure."""
    for key in keys:
        try:
            if key in st.session_state:
                del st.session_state[key]
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# PDF RTL / ARABIC HELPERS — ReportLab-safe text handling
# ─────────────────────────────────────────────────────────────────────────────
def _contains_arabic(text: str) -> bool:
    """Return True if text contains Arabic Unicode ranges."""
    return bool(re.search(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]", str(text or "")))


@st.cache_resource(show_spinner=False)
def get_pdf_font_names() -> tuple[str, str]:
    """
    Register a Unicode font for ReportLab when available.
    - Prefer bundled fonts/DejaVuSans.ttf when present.
    - Fallback to common Linux DejaVu paths on Streamlit Cloud.
    - Fallback to Helvetica only if no Unicode font exists.
    """
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfbase.pdfmetrics import registerFontFamily

        # Production rule: prefer a bundled font committed to the repository.
        # Place your licensed Arabic/Unicode font under ./fonts/ to avoid cloud-host roulette.
        regular_candidates = [
            Path("fonts/TenderLensArabic-Regular.ttf"),
            Path("fonts/DejaVuSans.ttf"),
            Path("fonts/Arial.ttf"),
            Path("fonts/arial.ttf"),
            Path("fonts/SakkalMajalla.ttf"),
            Path("DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/local/share/fonts/DejaVuSans.ttf"),
        ]
        bold_candidates = [
            Path("fonts/TenderLensArabic-Bold.ttf"),
            Path("fonts/DejaVuSans-Bold.ttf"),
            Path("fonts/Arial-Bold.ttf"),
            Path("fonts/arialbd.ttf"),
            Path("fonts/SakkalMajallaBold.ttf"),
            Path("DejaVuSans-Bold.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            Path("/usr/local/share/fonts/DejaVuSans-Bold.ttf"),
        ]

        regular_path = next((p for p in regular_candidates if p.exists()), None)
        bold_path = next((p for p in bold_candidates if p.exists()), None) or regular_path
        if not regular_path:
            log.warning(
                "No bundled Arabic/Unicode PDF font found. "
                "Add fonts/DejaVuSans.ttf and fonts/DejaVuSans-Bold.ttf, "
                "or your licensed Arabic font, to guarantee Arabic PDF rendering."
            )
            return "Helvetica", "Helvetica-Bold"

        try:
            pdfmetrics.getFont("TLPArabic")
        except Exception:
            pdfmetrics.registerFont(TTFont("TLPArabic", str(regular_path)))

        try:
            pdfmetrics.getFont("TLPArabic-Bold")
        except Exception:
            pdfmetrics.registerFont(TTFont("TLPArabic-Bold", str(bold_path)))

        try:
            registerFontFamily(
                "TLPArabic",
                normal="TLPArabic",
                bold="TLPArabic-Bold",
                italic="TLPArabic",
                boldItalic="TLPArabic-Bold",
            )
        except Exception:
            pass

        return "TLPArabic", "TLPArabic-Bold"
    except Exception as e:
        log.warning(f"Arabic PDF font registration skipped: {e}")
        return "Helvetica", "Helvetica-Bold"


def prepare_pdf_text(text) -> str:
    """
    Prepare Arabic/RTL text for ReportLab Paragraph while preserving simple
    ReportLab markup tags such as <b>, <font>, <br/>.
    """
    s = "" if text is None else str(text)
    if not _contains_arabic(s):
        return s
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display

        parts = re.split(r"(<[^>]+>)", s)
        shaped_parts = []
        for part in parts:
            if not part:
                continue
            if part.startswith("<") and part.endswith(">"):
                shaped_parts.append(part)
            elif _contains_arabic(part):
                shaped_parts.append(get_display(arabic_reshaper.reshape(part)))
            else:
                shaped_parts.append(part)
        return "".join(shaped_parts)
    except Exception as e:
        log.warning(f"Arabic PDF shaping skipped: {e}")
        return s


def pdf_font_alias(font: str | None, regular_font: str, bold_font: str) -> str:
    """Map legacy Helvetica font requests to registered Unicode fonts."""
    if not font:
        return regular_font
    if font in {"Helvetica-Bold", "Times-Bold", "Courier-Bold"}:
        return bold_font
    if font in {"Helvetica", "Times-Roman", "Courier"}:
        return regular_font
    return font


def validate_uploaded_file(uploaded_file, max_mb: int = MAX_FILE_SIZE_MB) -> tuple[bool, str]:
    """تحقق من صلاحية الملف المرفوع."""
    if uploaded_file is None:
        return False, "No file"
    size_mb = uploaded_file.size / (1024 * 1024)
    if size_mb > max_mb:
        return False, f"الملف كبير جداً: {size_mb:.1f}MB (الحد الأقصى {max_mb}MB)"
    return True, "OK"


# ─────────────────────────────────────────────────────────────────────────────
# OPENAI CLIENT — DIRECT INTEGRATION (replaces Replit)
# Streamlit Cloud safe: avoids OpenAI/httpx "proxies" incompatibility
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def _build_openai_client(api_key: str) -> OpenAI:
    """
    بناء عميل OpenAI مع كاش الموارد.

    ملاحظة تشغيلية:
    تمرير http_client صراحة يمنع انهيار بعض بيئات Streamlit Cloud عند اجتماع
    إصدارات OpenAI قديمة نسبياً مع httpx>=0.28، حيث يظهر الخطأ:
    Client.__init__() got an unexpected keyword argument 'proxies'.
    """
    import httpx

    http_client = httpx.Client(
        timeout=httpx.Timeout(API_TIMEOUT, connect=30.0),
        follow_redirects=True,
    )

    return OpenAI(
        api_key=api_key,
        http_client=http_client,
        max_retries=API_MAX_RETRIES,
    )


def get_openai_client():
    """
    جلب عميل OpenAI من إعدادات المستخدم.
    الأولوية:
      1. مفتاح من session_state (يدخله المستخدم)
      2. st.secrets["OPENAI_API_KEY"] (للنشر على Streamlit Cloud)
      3. متغير بيئة OPENAI_API_KEY (للتشغيل المحلي)
    """
    api_key = (st.session_state.get("user_api_key", "") or "").strip()

    if not api_key:
        try:
            api_key = (st.secrets.get("OPENAI_API_KEY", "") or "").strip()
        except Exception:
            api_key = ""

    if not api_key:
        api_key = (os.environ.get("OPENAI_API_KEY", "") or "").strip()

    if not api_key or not api_key.startswith("sk-"):
        return None

    try:
        return _build_openai_client(api_key)
    except Exception as e:
        log.exception(f"Client build failed: {e}")
        return None


def get_client():
    """واجهة موحَّدة لجلب العميل (للحفاظ على التوافق مع باقي الكود)."""
    return get_openai_client()


def test_api_connection() -> tuple[bool, str]:
    """اختبار سريع لصحة المفتاح والاتصال باستخدام نفس مسار الاستدعاء المعتمد."""
    client = get_openai_client()
    if not client:
        return False, "لم يتم تكوين عميل OpenAI. تحقق من المفتاح أو من إعدادات Streamlit Secrets."
    try:
        model_name = st.session_state.get("openai_model", DEFAULT_MODEL)
        content = call_ai(
            client,
            "You are a connectivity test. Reply with OK only.",
            "Reply with OK only.",
            model=model_name,
            max_tokens=40,
            temperature=0,
        )
        if not content or content.startswith("[AI Error") or content.startswith("[AI Auth"):
            return False, content or "تم الاتصال لكن الاستجابة فارغة."
        return True, f"✅ الاتصال ناجح ({model_name}) — {content[:40]}"
    except AuthenticationError:
        return False, "❌ المفتاح غير صالح أو لا يملك صلاحية."
    except APITimeoutError:
        return False, "❌ انتهت مهلة الاتصال."
    except RateLimitError:
        return False, "⚠️ تم تجاوز حد المعدل أو الرصيد غير كافٍ."
    except APIError as e:
        return False, f"❌ خطأ API: {str(e)[:180]}"
    except Exception as e:
        return False, f"❌ فشل غير متوقع: {type(e).__name__}: {str(e)[:180]}"


# ─────────────────────────────────────────────────────────────────────────────
# AI CALLS — UNIFIED & HARDENED
# ─────────────────────────────────────────────────────────────────────────────
def _is_responses_model(model: str) -> bool:
    """Use Responses API only for GPT-5.x models when explicitly selected."""
    return str(model or "").startswith("gpt-5")


def _extract_responses_text(resp) -> str:
    """استخراج النص من Responses API مع دعم عدة أشكال للإخراج."""
    output_text = getattr(resp, "output_text", None)
    if output_text:
        return str(output_text).strip()

    parts = []
    for item in getattr(resp, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            txt = getattr(content, "text", None)
            if txt:
                parts.append(str(txt))
    return "\n".join(parts).strip()


def _call_responses_api(client, system: str, user: str, model: str, max_tokens: int) -> str:
    """استدعاء Responses API مع GPT-5.5 Extended reasoning."""
    # OpenAI يستخدم Model ID = gpt-5.5، أما مفهوم Extended هنا فيُطبّق عبر reasoning effort = xhigh.
    resp = client.responses.create(
        model=model,
        instructions=system,
        input=user,
        reasoning={"effort": DEFAULT_REASONING_EFFORT},
        max_output_tokens=max_tokens,
    )
    return _extract_responses_text(resp)


def _call_chat_completions_api(client, system: str, user: str, model: str, temperature: float, max_tokens: int) -> str:
    """استدعاء Chat Completions للنماذج القديمة/الاحتياطية فقط."""
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return (resp.choices[0].message.content or "").strip()


def call_ai(
    client,
    system: str,
    user: str,
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = MAX_TOKENS_PER_REQ,
) -> str:
    """
    استدعاء AI موحَّد مع معالجة شاملة للأخطاء وإعادة المحاولة.
    يستخدم النموذج الافتراضي المستقر، ويدعم GPT-5.x اختيارياً عبر Responses API.
    """
    if client is None:
        return "[AI Error: لا يوجد عميل OpenAI. أدخل مفتاح API في الشريط الجانبي.]"

    model = model or st.session_state.get("openai_model", DEFAULT_MODEL)

    last_err = None
    for attempt in range(API_MAX_RETRIES):
        try:
            if _is_responses_model(model) and hasattr(client, "responses"):
                content = _call_responses_api(client, system, user, model, max_tokens)
            else:
                content = _call_chat_completions_api(client, system, user, model, temperature, max_tokens)

            if not content:
                return "[AI Error: تم الاتصال بالنموذج لكن الاستجابة النصية فارغة.]"
            return content

        except RateLimitError as e:
            last_err = e
            if is_request_too_large_error(str(e)):
                return (
                    "[AI Error: الطلب أكبر من حدود نموذج/حساب OpenAI الحالي. "
                    "تم منع إعادة المحاولة غير المفيدة. الحل: استخدم التحليل المرحلي أو قلل عدد/حجم الملفات.]"
                )
            wait = 2 ** attempt
            log.warning(f"Rate limit hit, waiting {wait}s")
            time.sleep(wait)

        except APITimeoutError as e:
            last_err = e
            time.sleep(2)

        except AuthenticationError as e:
            return f"[AI Auth Error: المفتاح غير صالح. {str(e)[:80]}]"

        except APIError as e:
            last_err = e
            msg = str(e).lower()
            if is_request_too_large_error(str(e)):
                return (
                    "[AI Error: الطلب أكبر من حدود نموذج/حساب OpenAI الحالي. "
                    "تم منع إعادة المحاولة غير المفيدة. الحل: قلل حجم الملفات أو استخدم التحليل المرحلي.]"
                )
            if ("model" in msg or "unsupported" in msg or "not found" in msg) and attempt == 0:
                model = FALLBACK_MODEL
                log.warning(f"Falling back to {FALLBACK_MODEL}")
                continue
            break

        except Exception as e:
            last_err = e
            msg = str(e).lower()
            if ("responses" in msg or "unexpected keyword" in msg or "model" in msg) and attempt == 0:
                model = FALLBACK_MODEL
                log.warning(f"Falling back to {FALLBACK_MODEL} after unexpected error: {e}")
                continue
            log.error(f"Unexpected AI error: {e}")
            break

    return f"[AI Error بعد {API_MAX_RETRIES} محاولات: {str(last_err)[:120]}]"


def call_ai_json(client, system: str, user: str, **kwargs) -> dict | list:
    """
    استدعاء AI مع إجبار النموذج على إرجاع JSON صالح.
    """
    if client is None:
        return {}

    sys_with_json = system.rstrip() + (
        "\n\nIMPORTANT: Reply ONLY with valid JSON. "
        "No markdown fences, no prose, no explanation."
    )

    raw = call_ai(client, sys_with_json, user, **kwargs)

    if raw.startswith("[AI Error") or raw.startswith("[AI Auth"):
        return {}

    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m_obj = re.search(r"\{.*\}", raw, re.DOTALL)
        m_arr = re.search(r"\[.*\]", raw, re.DOTALL)
        for m in (m_arr, m_obj):
            if m:
                try:
                    return json.loads(m.group(0))
                except json.JSONDecodeError:
                    continue
    return {}


def is_request_too_large_error(text: str) -> bool:
    """كشف خطأ OpenAI الخاص بكبر حجم الطلب حتى لا نعيد المحاولة بلا فائدة."""
    t = (text or "").lower()
    return "request too large" in t or "tokens per min" in t or "maximum context" in t


def build_compact_context_from_file(name: str, txt: str, max_chars: int = 18000, max_tokens: int | None = None) -> str:
    """تجهيز سياق محدود وآمن لكل ملف باستخدام ميزانية رموز لا أحرف فقط."""
    cleaned = re.sub(r"\n{3,}", "\n\n", txt or "")
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    token_budget = max_tokens or max(1500, min(MAX_INPUT_TOKENS_PER_FILE, int(max_chars / 2)))
    limited = truncate_to_token_budget(cleaned, token_budget)
    return f"\n\n{'='*50}\nالملف: {name}\n{'='*50}\n{limited}"


SINGLE_FILE_TENDER_PROMPT = """أنت مهندس مكتب فني أول وخبير تحليل وثائق مناقصات.

مهمتك الآن تحليل ملف واحد فقط من ملفات المناقصة لصالح مقدم العرض: شركة الرواف.
استخرج كل الحقائق والمتطلبات القابلة للاستخدام في تقرير العرض الفني النهائي.

أعد مخرجاً مركزاً ومنظماً، ولا يتجاوز 1100 كلمة، بالهيكل التالي:
# مصدر الملف
# معلومات المشروع المذكورة
# نطاق الأعمال
# متطلبات الجهة المالكة من مقدم العرض
# المتطلبات الفنية والرقمية
# المنهجيات والخطط المطلوبة
# الكوادر والموارد والمعدات
# الجودة والسلامة والبيئة
# المدد والمواعيد والضمانات
# الشروط التعاقدية والمالية المهمة
# المخاطر والفجوات والاستفسارات
# معلومات غير متوفرة داخل هذا الملف

لا تخترع أي معلومة. إذا لم تظهر المعلومة في الملف، اكتب: غير متوفرة في هذا الملف."""

TENDER_SYNTHESIS_PROMPT = """أنت مهندس مكتب فني أول وخبير عطاءات دولية متخصص في مشاريع البنية التحتية والتشييد.

مهمتك دمج ملخصات تحليل ملفات المناقصة في تقرير استخلاصي نهائي لصالح مقدم العرض: شركة الرواف.
اعتمد فقط على الملخصات المزودة لك، ولا تخترع أي معلومة.
عند غياب المعلومة اكتب: غير محددة في الوثائق المرفوعة.

المطلوب تقرير غزير ودقيق يركز على جميع متطلبات الجهة المالكة من مقدم العرض، وليس مجرد ملخص وصفي.

هيكل التقرير المطلوب:
# 📋 الملخص التنفيذي للمنافسة
# 1. بطاقة حقائق المشروع
# 2. نطاق العمل المستخلص
# 3. مصفوفة متطلبات الجهة المالكة من مقدم العرض
# 4. المتطلبات الفنية والكودية
# 5. المنهجيات والخطط المطلوبة في العرض الفني
# 6. الموارد والكوادر والمعدات المطلوبة
# 7. متطلبات الجودة والسلامة والبيئة
# 8. البرنامج الزمني والمواعيد والالتزامات الزمنية
# 9. جدول الكميات والأرقام المؤثرة
# 10. الشروط التعاقدية المؤثرة على العرض الفني
# 11. الفجوات والتعارضات ونقاط الاستفسار
# 12. توصيات إعداد العرض الفني لشركة الرواف

اذكر مصدر كل معلومة قدر الإمكان باسم الملف كما ورد في الملخصات."""


def analyze_tender_in_batches(client, tender_texts: dict) -> str:
    """
    Production tender analysis engine.

    Default behavior:
    - Use ONE focused comprehensive analysis pass when the uploaded tender context
      fits the configured token budget.

    Safety behavior:
    - If the tender set is too large for a reliable single request, switch to staged
      extraction per file, then synthesize. This is not the default path; it is a
      protection mechanism to avoid missing owner requirements or crashing with
      Request too large / Tokens per minute errors.
    """
    if not tender_texts:
        return "[AI Error: لا توجد ملفات لتحليلها.]"

    model = st.session_state.get("openai_model", DEFAULT_MODEL)
    raw_total_tokens = sum(count_tokens(txt or "", model=model) for txt in tender_texts.values())

    def _single_pass() -> str:
        # Build a compact but source-labeled context. The budget is intentionally firm:
        # a focused one-pass report is preferred, but not at the cost of API failure.
        per_file_budget = max(
            3_000,
            min(MAX_INPUT_TOKENS_PER_FILE, int(MAX_SINGLE_PASS_TENDER_TOKENS / max(len(tender_texts), 1))),
        )
        tender_context = build_context_bundle(
            tender_texts,
            label="Tender File",
            max_total_tokens=MAX_SINGLE_PASS_TENDER_TOKENS,
            per_file_tokens=per_file_budget,
            model=model,
        )
        user_msg = (
            "أنت الآن تحلل وثائق مناقصة لصالح مقدم العرض: شركة الرواف.\n"
            "أصدر تقريراً واحداً مركزاً وغزيراً ودقيقاً، مع استخراج كل ما تطلبه الجهة المالكة من مقدم العرض فنياً وإدارياً وتقديمياً.\n"
            "لا تفترض أي معلومة غير ظاهرة في النصوص. اربط كل متطلب باسم الملف قدر الإمكان.\n\n"
            "النصوص المرفوعة ضمن ميزانية آمنة للتحليل:\n\n"
            f"{tender_context}"
        )
        return call_ai(
            client,
            TENDER_ANALYSIS_PROMPT,
            user_msg,
            max_tokens=7_500,
            temperature=0.08,
        )

    def _staged_pass() -> str:
        per_file_summaries = []
        total = len(tender_texts)

        for i, (name, txt) in enumerate(tender_texts.items(), start=1):
            file_context = build_compact_context_from_file(
                name,
                txt,
                max_chars=18000,
                max_tokens=MAX_INPUT_TOKENS_PER_FILE,
            )
            file_prompt = (
                f"حلل الملف رقم {i} من {total} لصالح مقدم العرض: شركة الرواف.\n"
                f"اسم الملف: {name}\n"
                f"عدد الكلمات التقريبي: {word_count(txt):,}\n\n"
                "استخرج كل طلب فني أو إداري أو تقديمي تفرضه الجهة المالكة على مقدم العرض، "
                "مع تمييز المتطلبات الحرجة ومتطلبات المنهجيات والموارد والجودة والسلامة والبرنامج الزمني والوثائق.\n\n"
                f"النص المحدود الآمن للتحليل:\n{file_context}"
            )
            summary = call_ai(
                client,
                SINGLE_FILE_TENDER_PROMPT,
                file_prompt,
                max_tokens=3_200,
                temperature=0.08,
            )
            if summary.startswith("[AI Error"):
                per_file_summaries.append(f"# {name}\nتعذر تحليل هذا الملف: {summary}")
            else:
                per_file_summaries.append(f"# {name}\n{truncate_to_token_budget(summary, 2_200, model=model)}")

            # Production-grade throttle to reduce TPM/RPM pressure on dense tender sets.
            time.sleep(TENDER_ANALYSIS_SLEEP_SECONDS)

        merged_summaries = "\n\n".join(per_file_summaries)
        final_input = (
            "فيما يلي ملخصات تحليل الملفات منفردة. استخدمها لإصدار تقرير نهائي واحد لصالح شركة الرواف.\n"
            "المطلوب تقرير غزير ودقيق يحتوي على جميع متطلبات الجهة المالكة من مقدم العرض، "
            "خصوصاً المتطلبات الفنية، منهجيات التنفيذ، الكوادر، المعدات، الجودة، السلامة، البرنامج الزمني، "
            "الوثائق المطلوبة، متطلبات الامتثال، المخاطر، والفجوات.\n"
            "اعتمد فقط على الملخصات المزودة، واذكر اسم الملف كمصدر قدر الإمكان.\n\n"
            + truncate_to_token_budget(merged_summaries, MAX_SYNTHESIS_INPUT_TOKENS, model=model)
        )
        return call_ai(
            client,
            TENDER_SYNTHESIS_PROMPT,
            final_input,
            max_tokens=7_500,
            temperature=0.1,
        )

    # Prefer one focused pass when technically safe.
    if raw_total_tokens <= MAX_SINGLE_PASS_TENDER_TOKENS:
        result = _single_pass()
        if not is_request_too_large_error(result):
            return result
        log.warning("Single-pass tender analysis exceeded request limits; switching to staged safety mode.")

    # Staged mode is only used when the complete tender set is too large or the API rejects one-pass.
    return _staged_pass()



# ─────────────────────────────────────────────────────────────────────────────
# DOCUMENT EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────
def extract_text(file_bytes: bytes, filename: str = "") -> str:
    """استخراج نص من PDF أو DOCX."""
    if not file_bytes:
        return ""

    if filename.lower().endswith(".docx"):
        try:
            from docx import Document
            doc = Document(io.BytesIO(file_bytes))
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except Exception as e:
            log.error(f"DOCX read error {filename}: {e}")
            return ""

    pages = []
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                t = page.extract_text(layout=True)
                if t:
                    pages.append(t)
    except Exception as e:
        log.error(f"PDF read error {filename}: {e}")
        return ""
    return "\n\n".join(pages)


def word_count(text: str) -> int:
    return len((text or "").split())


def find_section(text: str, keywords: list, window: int = 3000) -> str:
    if not text:
        return ""
    lower = text.lower()
    for kw in keywords:
        idx = lower.find(kw.lower())
        if idx != -1:
            return text[max(0, idx - 150): idx + window].strip()
    return ""
    # ─────────────────────────────────────────────────────────────────────────────
# BOQ HELPERS
# ─────────────────────────────────────────────────────────────────────────────
_COL_ITEM = {"item", "item no", "item no.", "no", "no.", "ref", "رقم", "البند", "بند"}
_COL_DESC = {"description", "desc", "work description", "activity", "وصف", "الوصف",
             "بيان", "البيان", "الأعمال", "activity description"}
_COL_UNIT = {"unit", "uom", "units", "الوحدة", "وحدة"}
_COL_QTY  = {"qty", "quantity", "quantities", "الكمية", "كمية", "كميات"}

_SKIP_PATTERNS = re.compile(
    r'^\s*(total|sub.?total|grand|sum|carried|page|amount|المجموع|الإجمالي|مجموع)\b',
    re.IGNORECASE,
)


def _clean_cell(val) -> str:
    if val is None:
        return ""
    return re.sub(r'\s+', ' ', str(val)).strip()


def _is_numeric_qty(val: str) -> bool:
    cleaned = (val or "").replace(',', '').replace(' ', '')
    try:
        float(cleaned)
        return True
    except ValueError:
        return False


def _detect_col_indices(header_row: list) -> dict:
    mapping = {}
    for i, cell in enumerate(header_row):
        low = _clean_cell(cell).lower()
        if low in _COL_ITEM and "item" not in mapping:
            mapping["item"] = i
        elif low in _COL_DESC and "desc" not in mapping:
            mapping["desc"] = i
        elif low in _COL_UNIT and "unit" not in mapping:
            mapping["unit"] = i
        elif low in _COL_QTY and "qty" not in mapping:
            mapping["qty"] = i
    return mapping


def extract_boq_tables_auto(file_bytes: bytes) -> list[dict]:
    """استخراج جداول BOQ تلقائياً من PDF."""
    rows = []
    if not file_bytes:
        return rows
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                tables = page.extract_tables() or []
                for table in tables:
                    if not table or len(table) < 2:
                        continue
                    header_idx = 0
                    col_map = {}
                    for hi, hrow in enumerate(table[:4]):
                        col_map = _detect_col_indices(hrow)
                        if len(col_map) >= 2:
                            header_idx = hi
                            break
                    if len(col_map) < 2 and table[0] and len(table[0]) >= 4:
                        col_map = {"item": 0, "desc": 1, "unit": 2, "qty": 3}
                        header_idx = 0

                    for row in table[header_idx + 1:]:
                        if not row:
                            continue
                        desc_cell = _clean_cell(row[col_map.get("desc", 1)] if len(row) > col_map.get("desc", 1) else "")
                        if not desc_cell or _SKIP_PATTERNS.match(desc_cell):
                            continue
                        qty_raw = _clean_cell(row[col_map.get("qty", 3)] if len(row) > col_map.get("qty", 3) else "")
                        unit_raw = _clean_cell(row[col_map.get("unit", 2)] if len(row) > col_map.get("unit", 2) else "")
                        item_raw = _clean_cell(row[col_map.get("item", 0)] if len(row) > col_map.get("item", 0) else "")

                        if not qty_raw and not unit_raw:
                            continue

                        qty_val = qty_raw if qty_raw else "LS"
                        rows.append({
                            "item_no": item_raw,
                            "description": desc_cell,
                            "unit": unit_raw if unit_raw else "—",
                            "quantity": qty_val,
                            "source_page": page_num,
                        })
    except Exception as e:
        log.error(f"BOQ table extraction error: {e}")
    return rows


def extract_boq_ai(client, text: str) -> list[dict]:
    """استخراج بنود BOQ من نص غير منظم باستخدام AI."""
    if not text or not client:
        return []
    snippet = truncate_to_token_budget(text, MAX_INPUT_TOKENS_PER_FILE)
    raw = call_ai_json(
        client,
        BOQ_AI_PROMPT,
        f"استخرج بنود BOQ من هذا النص:\n\n{snippet}",
    )
    if not isinstance(raw, list):
        return []
    result = []
    for itm in raw:
        if not isinstance(itm, dict):
            continue
        result.append({
            "item_no": str(itm.get("item_no", "")),
            "description": str(itm.get("description", "")),
            "unit": str(itm.get("unit", "")),
            "quantity": str(itm.get("quantity", "")),
            "source_page": 0,
        })
    return result


def build_boq_dataframe(all_rows: list[dict]) -> pd.DataFrame:
    if not all_rows:
        return pd.DataFrame(columns=["#", "Item No.", "Description", "Unit", "Quantity",
                                     "Unit Rate", "Total Amount", "Notes"])
    df = pd.DataFrame(all_rows)
    df = df.rename(columns={
        "item_no": "Item No.",
        "description": "Description",
        "unit": "Unit",
        "quantity": "Quantity",
        "source_page": "PDF Page",
    })
    df["Unit Rate"] = ""
    df["Total Amount"] = ""
    df["Notes"] = ""
    df.insert(0, "#", range(1, len(df) + 1))
    return df


def df_to_excel_bytes(df: pd.DataFrame, project_name: str = "BOQ") -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="BOQ")
        wb, ws = writer.book, writer.sheets["BOQ"]

        hdr_fmt = wb.add_format({"bold": True, "font_color": "#FFB81C", "bg_color": "#003087",
                                  "border": 1, "align": "center", "valign": "vcenter", "font_size": 10})
        cell_fmt = wb.add_format({"border": 1, "valign": "vcenter", "font_size": 9, "text_wrap": True})
        price_fmt = wb.add_format({"border": 1, "valign": "vcenter", "font_size": 9,
                                    "bg_color": "#FFFBEB", "num_format": "#,##0.00"})
        qty_fmt = wb.add_format({"border": 1, "valign": "vcenter", "font_size": 9,
                                  "align": "center", "num_format": "#,##0.##"})
        item_fmt = wb.add_format({"bold": True, "border": 1, "valign": "vcenter",
                                   "font_size": 9, "align": "center", "font_color": "#003087"})

        for col_idx, col_name in enumerate(df.columns):
            ws.write(0, col_idx, col_name, hdr_fmt)

        col_widths = {"#": 4, "Item No.": 10, "Description": 55, "Unit": 8,
                      "Quantity": 12, "PDF Page": 8, "Unit Rate": 14,
                      "Total Amount": 16, "Notes": 22}
        for col_idx, col_name in enumerate(df.columns):
            ws.set_column(col_idx, col_idx, col_widths.get(col_name, 14))

        price_cols = {"Unit Rate", "Total Amount"}
        qty_cols = {"Quantity"}
        item_cols = {"#", "Item No.", "Unit"}
        for row_idx, row in df.iterrows():
            for col_idx, col_name in enumerate(df.columns):
                val = row[col_name]
                if col_name in price_cols:
                    ws.write(row_idx + 1, col_idx, val, price_fmt)
                elif col_name in qty_cols:
                    ws.write(row_idx + 1, col_idx, val, qty_fmt)
                elif col_name in item_cols:
                    ws.write(row_idx + 1, col_idx, val, item_fmt)
                else:
                    ws.write(row_idx + 1, col_idx, val, cell_fmt)

        ws.freeze_panes(1, 0)

        meta = wb.add_worksheet("Info")
        meta_fmt = wb.add_format({"font_size": 10, "bold": True, "font_color": "#003087"})
        meta.write(0, 0, "TenderLens Pro — BOQ Quantities Extract", meta_fmt)
        meta.write(1, 0, f"Project: {project_name}")
        meta.write(2, 0, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        meta.write(3, 0, "NOTE: Unit Rate and Total Amount columns are intentionally blank.")
        meta.write(4, 0, "Please fill in actual unit rates. Total = Quantity × Unit Rate.")
        meta.set_column(0, 0, 60)

    return output.getvalue()


def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Export CSV safely after neutralizing formula-like cells for Excel."""
    safe_df = sanitize_dataframe_for_csv(df)
    return safe_df.to_csv(index=False).encode("utf-8-sig")


# ─────────────────────────────────────────────────────────────────────────────
# CLAUSE TRACKER HELPERS
# ─────────────────────────────────────────────────────────────────────────────
CATEGORY_META = {
    "FIDIC_CLAUSE":        {"label": "FIDIC Sub-Clause",      "color": "#003087", "ar": "بنود فيديك"},
    "PAYMENT":             {"label": "Payment Terms",          "color": "#2563EB", "ar": "شروط الدفع"},
    "LIQUIDATED_DAMAGES":  {"label": "Liquidated Damages",     "color": "#DC2626", "ar": "الغرامات والتأخير"},
    "VARIATIONS":          {"label": "Variations / Change Orders", "color": "#D97706", "ar": "التعديلات والتغييرات"},
    "WARRANTIES":          {"label": "Warranties & DLP",       "color": "#059669", "ar": "الضمانات"},
}
RISK_COLORS = {"HIGH": "#DC2626", "MEDIUM": "#D97706", "LOW": "#059669"}


def ai_extract_clauses(client, text: str) -> list[dict]:
    if not text or not client:
        return []
    chunk = truncate_to_token_budget(text, MAX_INPUT_TOKENS_PER_FILE)
    raw = call_ai_json(client, CLAUSE_TRACKER_PROMPT, chunk)
    return raw if isinstance(raw, list) else []


def build_clause_df(all_items: list[dict]) -> pd.DataFrame:
    if not all_items:
        return pd.DataFrame(columns=[
            "#", "Category", "Clause Ref", "Title", "Extracted Text",
            "Risk Level", "Risk Notes", "Action Required", "Source File", "Notes"
        ])
    df = pd.DataFrame(all_items)
    rename_map = {
        "category": "Category", "clause_ref": "Clause Ref", "title": "Title",
        "extracted_text": "Extracted Text", "risk_level": "Risk Level",
        "risk_notes": "Risk Notes", "action_required": "Action Required",
        "source_file": "Source File",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    for col in ["Category", "Clause Ref", "Title", "Extracted Text",
                "Risk Level", "Risk Notes", "Action Required"]:
        if col not in df.columns:
            df[col] = ""
    if "Source File" not in df.columns:
        df["Source File"] = ""
    df["Notes"] = ""
    df.insert(0, "#", range(1, len(df) + 1))
    return df[["#", "Category", "Clause Ref", "Title", "Extracted Text",
               "Risk Level", "Risk Notes", "Action Required", "Source File", "Notes"]]


def df_to_clause_excel_bytes(df: pd.DataFrame, project_name: str = "Clauses") -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Clause Register")
        wb, ws = writer.book, writer.sheets["Clause Register"]

        hdr_fmt = wb.add_format({"bold": True, "bg_color": "#003087", "font_color": "#FFB81C",
                                  "border": 1, "valign": "vcenter", "align": "center", "font_size": 10})
        high_fmt = wb.add_format({"bg_color": "#FEE2E2", "border": 1, "text_wrap": True, "valign": "top", "font_size": 9})
        med_fmt  = wb.add_format({"bg_color": "#FEF3C7", "border": 1, "text_wrap": True, "valign": "top", "font_size": 9})
        low_fmt  = wb.add_format({"bg_color": "#D1FAE5", "border": 1, "text_wrap": True, "valign": "top", "font_size": 9})
        base_fmt = wb.add_format({"border": 1, "text_wrap": True, "valign": "top", "font_size": 9})
        notes_fmt = wb.add_format({"border": 1, "bg_color": "#F0F4FF", "text_wrap": True,
                                    "valign": "top", "font_size": 9, "italic": True})

        for col_idx, col_name in enumerate(df.columns):
            ws.write(0, col_idx, col_name, hdr_fmt)

        col_widths = {"#": 4, "Category": 22, "Clause Ref": 16, "Title": 24,
                      "Extracted Text": 55, "Risk Level": 10, "Risk Notes": 32,
                      "Action Required": 32, "Source File": 24, "Notes": 28}
        for col_idx, col_name in enumerate(df.columns):
            ws.set_column(col_idx, col_idx, col_widths.get(col_name, 18))

        for row_idx, row in df.iterrows():
            risk = str(row.get("Risk Level", "")).upper()
            row_fmt = high_fmt if risk == "HIGH" else med_fmt if risk == "MEDIUM" else low_fmt if risk == "LOW" else base_fmt
            for col_idx, col_name in enumerate(df.columns):
                val = str(row.iloc[col_idx]) if not pd.isna(row.iloc[col_idx]) else ""
                fmt = notes_fmt if col_name == "Notes" else row_fmt
                ws.write(row_idx + 1, col_idx, val, fmt)
            ws.set_row(row_idx + 1, 60)

        ws.freeze_panes(1, 0)
        ws.autofilter(0, 0, len(df), len(df.columns) - 1)

        lg = wb.add_worksheet("Legend")
        hf = wb.add_format({"bold": True, "bg_color": "#003087", "font_color": "#FFB81C", "font_size": 11})
        lf = wb.add_format({"font_size": 10})
        lg.write(0, 0, "TenderLens Pro — Smart Clause Tracker Register", hf)
        lg.write(1, 0, f"Project: {project_name}", lf)
        lg.write(2, 0, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", lf)
        lg.write(4, 0, "Risk Colour Key:", wb.add_format({"bold": True, "font_size": 10}))
        lg.write(5, 0, "🔴 HIGH",   wb.add_format({"bg_color": "#FEE2E2", "font_size": 10}))
        lg.write(6, 0, "🟡 MEDIUM", wb.add_format({"bg_color": "#FEF3C7", "font_size": 10}))
        lg.write(7, 0, "🟢 LOW",    wb.add_format({"bg_color": "#D1FAE5", "font_size": 10}))
        lg.set_column(0, 0, 60)

    return output.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# FEEDBACK REPORT HELPERS
# ─────────────────────────────────────────────────────────────────────────────
_FB_SECTION_MAP = {
    "EXECUTIVE_SUMMARY":  ("الملخص التنفيذي  |  Executive Summary",    (0, 48, 135),   "#EFF6FF"),
    "COMPLIANT_AREAS":    ("المجالات المستوفاة  |  Compliant Areas",   (21, 128, 61),  "#F0FDF4"),
    "CRITICAL_GAPS":      ("الثغرات الجوهرية  |  Critical Gaps",       (153, 27, 27),  "#FFF1F2"),
    "CORRECTIVE_ACTIONS": ("الإجراءات التصحيحية  |  Corrective Actions",(0, 48, 135),  "#FFFBEB"),
}


def _clean_emoji_word(text: str) -> str:
    return (text.replace("🔴", "[حرج]").replace("🟡", "[رئيسي]").replace("🟢", "[ثانوي]")
                .replace("✅", "[✓]").replace("❌", "[✗]").replace("⚠️", "[!]"))


def generate_feedback_docx(report_text: str, meta: dict) -> bytes:
    from docx import Document
    from docx.shared import Pt, RGBColor, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()
    for sec in doc.sections:
        sec.top_margin = Cm(2.5); sec.bottom_margin = Cm(2.5)
        sec.left_margin = Cm(2.8); sec.right_margin = Cm(2.8)

    NAVY = RGBColor(0, 48, 135)
    GOLD = RGBColor(255, 184, 28)
    GRAY = RGBColor(100, 116, 139)

    tp = doc.add_paragraph(); tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tr = tp.add_run("TenderLens Pro"); tr.bold = True; tr.font.size = Pt(24); tr.font.color.rgb = NAVY

    sp = doc.add_paragraph(); sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sr = sp.add_run("Technical Proposal — Formal Feedback Report")
    sr.bold = True; sr.font.size = Pt(13); sr.font.color.rgb = GOLD
    doc.add_paragraph("")

    tbl = doc.add_table(rows=len(meta), cols=2); tbl.style = "Table Grid"
    for i, (k, v) in enumerate(meta.items()):
        kc = tbl.rows[i].cells[0]; vc = tbl.rows[i].cells[1]
        kc.text = k; vc.text = str(v)
        for run in kc.paragraphs[0].runs:
            run.bold = True; run.font.color.rgb = NAVY; run.font.size = Pt(10)
        for run in vc.paragraphs[0].runs:
            run.font.size = Pt(10)
    doc.add_paragraph("")

    hr = doc.add_paragraph("─" * 72); hr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in hr.runs:
        run.font.color.rgb = RGBColor(203, 213, 225)
    doc.add_paragraph("")

    raw_secs = re.split(r'\n(?=# )', report_text.strip())
    for raw in raw_secs:
        if not raw.strip():
            continue
        lines = raw.strip().split("\n")
        heading_key = lines[0].replace("#", "").strip().upper()
        body = "\n".join(lines[1:]).strip()

        label = heading_key; rgb = (0, 48, 135)
        for key, (lbl, color_rgb, _bg) in _FB_SECTION_MAP.items():
            if key in heading_key:
                label, rgb = lbl, color_rgb
                break

        h_para = doc.add_paragraph()
        h_run = h_para.add_run(f"▌  {label}")
        h_run.bold = True; h_run.font.size = Pt(12); h_run.font.color.rgb = RGBColor(*rgb)

        spacer = doc.add_paragraph(); spacer.add_run("").font.size = Pt(2)

        for line in body.split("\n"):
            line_clean = _clean_emoji_word(line.strip())
            if not line_clean:
                doc.add_paragraph("").add_run("").font.size = Pt(4)
                continue
            stripped = line_clean.lstrip("-•* \t")
            is_num = len(line_clean) > 2 and line_clean[0].isdigit() and line_clean[1] in ".)"
            is_bull = line_clean[0] in ("-", "•", "*", "◦")
            if is_num:
                p = doc.add_paragraph(style="List Number")
            elif is_bull:
                p = doc.add_paragraph(style="List Bullet")
            else:
                p = doc.add_paragraph()
            r = p.add_run(stripped); r.font.size = Pt(10)
            if "[حرج]" in line_clean:
                r.font.color.rgb = RGBColor(153, 27, 27); r.bold = True
        doc.add_paragraph("")

    fp = doc.add_paragraph(); fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fr = fp.add_run(
        f"TenderLens Pro  ·  {meta.get('التاريخ', '')}  ·  "
        "CONFIDENTIAL — للمرسَل إليه فقط / For Addressee Only"
    )
    fr.font.size = Pt(9); fr.font.color.rgb = GRAY; fr.italic = True

    buf = io.BytesIO(); doc.save(buf); return buf.getvalue()


def generate_feedback_html(report_text: str, meta: dict) -> str:
    meta_rows = "".join(
        f"<tr><td style='padding:5px 14px;font-weight:700;color:#003087;"
        f"background:#EFF6FF;border:1px solid #CBD5E1;'>{safe_html(k)}</td>"
        f"<td style='padding:5px 14px;border:1px solid #CBD5E1;'>{safe_html(v)}</td></tr>"
        for k, v in meta.items()
    )

    def _esc(t: str) -> str:
        t = safe_html(t)
        return (t.replace("✅", '<span style="color:#16a34a">✅</span>')
                 .replace("❌", '<span style="color:#dc2626">❌</span>')
                 .replace("⚠️", '<span style="color:#d97706">⚠️</span>')
                 .replace("🔴", '<b style="color:#dc2626">🔴</b>')
                 .replace("🟡", '<b style="color:#d97706">🟡</b>')
                 .replace("🟢", '<b style="color:#16a34a">🟢</b>'))

    secs_html = ""
    for raw in re.split(r'\n(?=# )', report_text.strip()):
        if not raw.strip():
            continue
        lines = raw.strip().split("\n")
        hkey = lines[0].replace("#", "").strip().upper()
        body = "\n".join(lines[1:]).strip()

        label, h_color, bg = hkey, "#003087", "#F8FAFC"
        for key, (lbl, _rgb, bgc) in _FB_SECTION_MAP.items():
            if key in hkey:
                label = lbl
                h_color = f"#{_rgb[0]:02X}{_rgb[1]:02X}{_rgb[2]:02X}"
                bg = bgc
                break

        body_parts = []; in_list = False
        for line in body.split("\n"):
            l = line.strip()
            if not l:
                if in_list:
                    body_parts.append("</ol>"); in_list = False
                body_parts.append("<br>"); continue
            is_num = len(l) > 2 and l[0].isdigit() and l[1] in ".)"
            is_bull = l[0] in ("-", "•", "*")
            if is_num or is_bull:
                if not in_list:
                    body_parts.append('<ol style="margin:8px 0 0 0;line-height:2;direction:rtl;text-align:right;unicode-bidi:embed;padding-right:24px;padding-left:0;">'); in_list = True
                body_parts.append(f'<li style="direction:rtl;text-align:right;unicode-bidi:embed;">{_esc(l.lstrip("-•* 0123456789.)"))}</li>')
            else:
                if in_list:
                    body_parts.append("</ol>"); in_list = False
                body_parts.append(f'<p style="margin:6px 0;direction:rtl;text-align:right;unicode-bidi:embed;">{_esc(l)}</p>')
        if in_list:
            body_parts.append("</ol>")

        secs_html += f"""
<div style="margin-bottom:20px;border-radius:8px;overflow:hidden;border:1px solid {h_color}44;box-shadow:0 1px 4px rgba(0,0,0,.06);">
  <div style="background:{h_color};color:white;padding:11px 20px;font-size:14px;font-weight:700;letter-spacing:.3px;">{safe_html(label)}</div>
  <div style="background:{bg};padding:16px 22px;font-size:13px;line-height:1.85;color:#1e293b;">{"".join(body_parts)}</div>
</div>"""

    date_str = safe_html(meta.get("التاريخ", ""))
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="UTF-8">
<style>
body{{font-family:'Segoe UI',Arial,sans-serif;background:#F1F5F9;color:#1e293b;direction:rtl;margin:0;padding:20px 0;}}
.wrap{{max-width:860px;margin:0 auto;background:white;border-radius:12px;box-shadow:0 4px 24px rgba(0,48,135,.12);overflow:hidden;}}
.hdr{{background:linear-gradient(135deg,#003087 0%,#0052CC 100%);color:white;padding:32px 36px 24px;}}
.hdr h1{{margin:0 0 6px;font-size:26px;letter-spacing:.5px;}}
.hdr p{{margin:0;font-size:13px;color:#FFB81C;font-weight:700;}}
.meta{{border-collapse:collapse;width:100%;font-size:12px;}}
.body{{padding:28px 34px;direction:rtl;text-align:right;unicode-bidi:embed;}}
.body p,.body li{{direction:rtl;text-align:right;unicode-bidi:embed;}}
.foot{{text-align:center;padding:16px;font-size:11px;color:#94a3b8;border-top:1px solid #E2E8F0;background:#F8FAFC;}}
</style></head><body><div class="wrap">
<div class="hdr"><h1>🏛️ TenderLens Pro | By Eng. Ahmed Almaamari</h1>
<p>تقرير التغذية الراجعة الرسمي &nbsp;|&nbsp; Technical Proposal Formal Feedback Report</p></div>
<table class="meta">{meta_rows}</table>
<div class="body">{secs_html}</div>
<div class="foot">TenderLens Pro &nbsp;·&nbsp; {date_str} &nbsp;·&nbsp;
CONFIDENTIAL — للمرسَل إليه فقط / For Addressee Only</div></div></body></html>"""


# ─────────────────────────────────────────────────────────────────────────────
# MILESTONE TRACKER HELPERS
# ─────────────────────────────────────────────────────────────────────────────
_MILESTONE_CATS = {
    "Bid Submission":   {"icon": "🔴", "color": "#DC2626", "ar": "تقديم العطاء"},
    "Site Visit":       {"icon": "🏗️", "color": "#D97706", "ar": "زيارة الموقع"},
    "Clarification":    {"icon": "📝", "color": "#7C3AED", "ar": "الاستفسارات"},
    "Bid Bond":         {"icon": "🛡️", "color": "#0891B2", "ar": "ضمان العطاء"},
    "Performance Bond": {"icon": "📋", "color": "#0891B2", "ar": "كفالة الأداء"},
    "Contract Award":   {"icon": "🏆", "color": "#FFB81C", "ar": "إسناد العقد"},
    "Contract Duration":{"icon": "⏱️", "color": "#003087", "ar": "مدة العقد"},
    "Mobilization":     {"icon": "🚧", "color": "#059669", "ar": "فترة التعبئة"},
    "Completion":       {"icon": "✅", "color": "#16A34A", "ar": "تاريخ الإنجاز"},
    "DLP":              {"icon": "🔧", "color": "#6B7280", "ar": "فترة الضمان"},
    "Insurance":        {"icon": "📄", "color": "#6B7280", "ar": "التأمين"},
    "Other":            {"icon": "📌", "color": "#64748B", "ar": "أخرى"},
}


def ai_extract_milestones(client, text: str) -> list[dict]:
    if not text or not client:
        return []
    chunk = truncate_to_token_budget(text, MAX_INPUT_TOKENS_PER_FILE)
    raw = call_ai_json(client, MILESTONE_PROMPT, chunk)
    return raw if isinstance(raw, list) else []


def build_milestone_df(items: list[dict]) -> pd.DataFrame:
    if not items:
        return pd.DataFrame(columns=["#", "Category", "Milestone", "Date / Period", "Date (ISO)",
                                     "Time", "Source Clause", "Priority", "Notes", "Days Remaining"])
    df = pd.DataFrame(items)
    rename = {
        "category": "Category", "milestone": "Milestone", "date_text": "Date / Period",
        "date_iso": "Date (ISO)", "time_text": "Time", "source_clause": "Source Clause",
        "notes": "Notes", "priority": "Priority",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    for col in ["Category", "Milestone", "Date / Period", "Date (ISO)",
                "Time", "Source Clause", "Notes", "Priority"]:
        if col not in df.columns:
            df[col] = ""

    today = datetime.now().date()
    def _days(iso):
        try:
            if iso and len(str(iso)) >= 10:
                d = datetime.strptime(str(iso)[:10], "%Y-%m-%d").date()
                return (d - today).days
        except Exception:
            pass
        return None

    df["Days Remaining"] = df["Date (ISO)"].apply(_days)
    dated = df[df["Days Remaining"].notna()].sort_values("Date (ISO)")
    undated = df[df["Days Remaining"].isna()]
    df = pd.concat([dated, undated], ignore_index=True)
    df.insert(0, "#", range(1, len(df) + 1))
    return df


def df_to_milestone_excel(df: pd.DataFrame, project_name: str = "Milestones") -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        export_df = df.copy()
        export_df.to_excel(writer, index=False, sheet_name="Milestone Tracker")
        wb, ws = writer.book, writer.sheets["Milestone Tracker"]

        hdr_fmt = wb.add_format({"bold": True, "bg_color": "#003087", "font_color": "#FFB81C",
                                  "border": 1, "valign": "vcenter", "align": "center", "font_size": 10})
        high_fmt = wb.add_format({"bg_color": "#FEE2E2", "border": 1, "text_wrap": True, "valign": "top", "font_size": 9})
        med_fmt  = wb.add_format({"bg_color": "#FEF3C7", "border": 1, "text_wrap": True, "valign": "top", "font_size": 9})
        past_fmt = wb.add_format({"bg_color": "#F1F5F9", "font_color": "#94A3B8", "border": 1,
                                   "text_wrap": True, "valign": "top", "font_size": 9, "italic": True})
        base_fmt = wb.add_format({"border": 1, "text_wrap": True, "valign": "top", "font_size": 9})

        col_widths = {"#": 4, "Category": 18, "Milestone": 34, "Date / Period": 26,
                      "Date (ISO)": 14, "Time": 12, "Source Clause": 18,
                      "Priority": 10, "Notes": 38, "Days Remaining": 14}

        for ci, cn in enumerate(export_df.columns):
            ws.write(0, ci, cn, hdr_fmt)
            ws.set_column(ci, ci, col_widths.get(cn, 16))

        for ri, row in export_df.iterrows():
            days = row.get("Days Remaining")
            try:
                days_int = int(days) if days is not None and not pd.isna(days) else None
            except Exception:
                days_int = None

            if days_int is not None and days_int < 0:
                row_fmt = past_fmt
            elif days_int is not None and days_int <= 14:
                row_fmt = high_fmt
            elif days_int is not None and days_int <= 45:
                row_fmt = med_fmt
            else:
                row_fmt = base_fmt

            for ci, cn in enumerate(export_df.columns):
                val = row.iloc[ci]
                val = "" if pd.isna(val) else str(val) if cn != "Days Remaining" else (
                    f"{int(val)} days" if val is not None and not pd.isna(val) else "—"
                )
                ws.write(ri + 1, ci, val, row_fmt)

        ws.freeze_panes(1, 0)
        ws.autofilter(0, 0, len(export_df), len(export_df.columns) - 1)

        info = wb.add_worksheet("Info")
        hf = wb.add_format({"bold": True, "bg_color": "#003087", "font_color": "#FFB81C", "font_size": 11})
        lf = wb.add_format({"font_size": 10})
        info.write(0, 0, "TenderLens Pro — Milestone Tracker", hf)
        info.write(1, 0, f"Project: {project_name}", lf)
        info.write(2, 0, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", lf)
        info.write(3, 0, f"Total Milestones: {len(export_df)}", lf)
        info.set_column(0, 0, 60)

    return output.getvalue()


def generate_milestone_ics(df: pd.DataFrame, project_name: str = "Tender") -> bytes:
    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0",
        "PRODID:-//TenderLens Pro//Milestone Tracker//EN",
        "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
        f"X-WR-CALNAME:TenderLens — {project_name}",
        "X-WR-TIMEZONE:Asia/Riyadh",
    ]
    now_stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    for _, row in df.iterrows():
        iso = str(row.get("Date (ISO)", "")).strip()
        if not iso or len(iso) < 10:
            continue

        date_clean = iso[:10].replace("-", "")
        time_raw = str(row.get("Time", "")).strip()
        milestone = str(row.get("Milestone", "")).strip() or "Tender Milestone"
        category = str(row.get("Category", "")).strip()
        notes = str(row.get("Notes", "")).strip()
        priority = str(row.get("Priority", "")).strip().upper()
        source = str(row.get("Source Clause", "")).strip()
        date_text = str(row.get("Date / Period", "")).strip()

        dtstart = f"DTSTART;VALUE=DATE:{date_clean}"
        dtend = f"DTEND;VALUE=DATE:{date_clean}"
        if time_raw and ":" in time_raw:
            try:
                t_part = time_raw.strip().split()[0]
                hh, mm = t_part.split(":")[:2]
                dtstart = f"DTSTART:{date_clean}T{int(hh):02d}{int(mm):02d}00"
                dtend = f"DTEND:{date_clean}T{int(hh):02d}{int(mm):02d}00"
            except Exception:
                pass

        uid = f"{date_clean}-{hash(milestone) & 0xFFFFFF}@tenderlens"
        desc_parts = []
        if date_text: desc_parts.append(f"Date: {date_text}")
        if source: desc_parts.append(f"Source: {source}")
        if notes: desc_parts.append(f"Notes: {notes}")
        desc = "\\n".join(desc_parts)

        alarms = []
        if priority == "HIGH":
            for d in [7, 3, 1]:
                alarms.append(
                    f"BEGIN:VALARM\r\nTRIGGER:-P{d}D\r\nACTION:DISPLAY\r\n"
                    f"DESCRIPTION:Reminder: {milestone}\r\nEND:VALARM"
                )
        elif priority == "MEDIUM":
            alarms.append(
                f"BEGIN:VALARM\r\nTRIGGER:-P3D\r\nACTION:DISPLAY\r\n"
                f"DESCRIPTION:Reminder: {milestone}\r\nEND:VALARM"
            )

        event = [
            "BEGIN:VEVENT", f"UID:{uid}", f"DTSTAMP:{now_stamp}",
            dtstart, dtend,
            f"SUMMARY:[{category}] {milestone} — {project_name}",
            f"DESCRIPTION:{desc}", f"CATEGORIES:{category}",
            f"PRIORITY:{'1' if priority == 'HIGH' else '5' if priority == 'MEDIUM' else '9'}",
            "STATUS:CONFIRMED",
        ] + alarms + ["END:VEVENT"]
        lines.extend(event)

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines).encode("utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD & COMPARISON HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def compute_dashboard_data() -> dict:
    data: dict = {}
    data["has_tender"] = bool(st.session_state.get("tender_report", "").strip())
    data["tender_files"] = len(st.session_state.get("tender_texts", {}))

    review = st.session_state.get("review_report", "")
    data["has_review"] = bool(review.strip())
    score = None
    for pat in [r"نسبة الامتثال[^\d]{0,20}(\d{1,3})", r"(\d{1,3})\s*%", r"compliance[^\d]{0,20}(\d{1,3})"]:
        m = re.search(pat, review, re.IGNORECASE)
        if m:
            v = int(m.group(1))
            if 0 <= v <= 100:
                score = v
                break
    data["compliance_score"] = score
    data["review_files"] = (len(st.session_state.get("req_texts", {}))
                            + len(st.session_state.get("prop_texts", {})))

    boq_df = st.session_state.get("boq_df")
    data["has_boq"] = boq_df is not None and len(boq_df) > 0
    data["boq_items"] = len(boq_df) if data["has_boq"] else 0

    clause_df = st.session_state.get("clause_df")
    data["has_clauses"] = clause_df is not None and len(clause_df) > 0
    if data["has_clauses"] and "Risk Level" in clause_df.columns:
        data["n_high_clauses"] = int((clause_df["Risk Level"] == "HIGH").sum())
        data["n_total_clauses"] = len(clause_df)
    else:
        data["n_high_clauses"] = 0
        data["n_total_clauses"] = 0

    ms_df = st.session_state.get("milestone_df")
    data["has_milestones"] = ms_df is not None and len(ms_df) > 0
    data["n_total_milestones"] = 0
    data["n_urgent_milestones"] = 0
    data["n_past_milestones"] = 0
    data["days_to_next"] = None
    if data["has_milestones"]:
        data["n_total_milestones"] = len(ms_df)
        try:
            days_s = ms_df["Days Remaining"].dropna().astype(float)
            data["n_urgent_milestones"] = int((days_s <= 14).sum())
            data["n_past_milestones"] = int((days_s < 0).sum())
            future = days_s[days_s >= 0]
            data["days_to_next"] = int(future.min()) if len(future) > 0 else None
        except Exception:
            pass

    parts: list[float] = []
    if data["has_tender"]: parts.append(15.0)
    if data["has_review"] and score is not None:
        parts.append(score * 0.35)
    elif data["has_review"]:
        parts.append(15.0)
    if data["has_boq"] and data["boq_items"] > 0: parts.append(15.0)
    if data["has_clauses"]:
        cl_ok_pct = (data["n_total_clauses"] - data["n_high_clauses"]) / max(data["n_total_clauses"], 1)
        parts.append(cl_ok_pct * 20.0)
    if data["has_milestones"]:
        parts.append(max(0.0, 15.0 - data["n_urgent_milestones"] * 3))
    data["readiness_score"] = min(100, int(sum(parts))) if parts else 0
    return data


def build_tender_snapshot(name: str) -> dict:
    data = compute_dashboard_data()
    snapshot = {
        "name": name,
        "compliance_score": data["compliance_score"] if data["compliance_score"] is not None else 0,
        "readiness_score": data["readiness_score"],
        "n_high_clauses": data["n_high_clauses"],
        "n_total_clauses": data["n_total_clauses"],
        "n_urgent_milestones": data["n_urgent_milestones"],
        "n_total_milestones": data["n_total_milestones"],
        "days_to_next": data["days_to_next"],
        "boq_items": data["boq_items"],
        "has_boq": data["has_boq"], "has_clauses": data["has_clauses"],
        "has_milestones": data["has_milestones"], "has_review": data["has_review"],
        "has_tender": data["has_tender"],
    }
    snapshot["risk_score"] = min(100, snapshot["n_high_clauses"] * 12 + snapshot["n_urgent_milestones"] * 8)
    snapshot["clause_pressure"] = f"{snapshot['n_high_clauses']} HIGH / {snapshot['n_total_clauses']} total"
    snapshot["timeline_pressure"] = (
        f"{snapshot['n_urgent_milestones']} urgent" if snapshot["n_urgent_milestones"]
        else "No immediate deadline pressure"
    )
    snapshot["availability_score"] = max(0, 100 - snapshot["risk_score"])
    return snapshot


def compare_tender_snapshots(selected: list[dict]) -> dict:
    ordered = sorted(selected, key=lambda x: (x["readiness_score"], -x["risk_score"]), reverse=True)
    best = ordered[0] if ordered else {}
    second = ordered[1] if len(ordered) > 1 else {}
    if not best:
        return {"best": {}, "bullets": [], "matrix_rows": [],
                "verdict": "GO WITH CAUTION", "summary": "No data."}

    if best["readiness_score"] >= 75 and best["risk_score"] <= 24:
        verdict = "GO"
    elif best["readiness_score"] < 50 or best["risk_score"] >= 48:
        verdict = "NO-GO"
    else:
        verdict = "GO WITH CAUTION"

    bullets = [
        f"{best['name']} leads on readiness ({best['readiness_score']}/100) and lower risk pressure.",
        (f"{best['name']} has fewer urgent milestones and/or high-risk clauses than {second['name']}."
         if second else f"{best['name']} has the strongest combined score."),
        (f"Resource alignment is better because the next deadline is {best['days_to_next']} days away."
         if best["days_to_next"] is not None else
         "Resource alignment is better because no immediate timing pressure was detected."),
    ]
    if second:
        bullets[1] = f"{best['name']} beats {second['name']} on compliance/readiness and has a more manageable timeline."

    matrix_rows = []
    for item in ordered:
        matrix_rows.append([
            item["name"], f"{item['readiness_score']}/100", f"{item['compliance_score']}%",
            f"{item['n_high_clauses']} high / {item['n_total_clauses']} total",
            f"{item['n_urgent_milestones']} urgent / {item['n_total_milestones']} total",
            item["timeline_pressure"],
        ])

    summary = (f"Best Bet: {best['name']} — combines highest readiness, lowest execution pressure, "
               "and most favorable timing profile.")
    return {"best": best, "second": second, "verdict": verdict,
            "bullets": bullets[:3], "matrix_rows": matrix_rows, "summary": summary}


# ─────────────────────────────────────────────────────────────────────────────
# DOC GEN HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def generate_plan_docx(plan_type: str, plan_content: str, project_name: str,
                       structure: list, template_bytes: bytes | None = None) -> bytes:
    """
    Generate a Word document safely for production.

    Production behavior:
    - docxtpl is used only for short metadata placeholders.
    - Long AI-generated Markdown content is NOT injected into {{ content }} as raw text.
    - The long content is appended as real Word headings, paragraphs and lists using
      python-docx, so the output remains readable and professionally formatted.
    - No direct XML deletion/manipulation is used.

    Recommended metadata placeholders inside DOCX templates:
      {{ project_name }}, {{ plan_type }}, {{ generated_at }}, {{ outline }}

    If the template contains {{ content }}, it will be intentionally cleared and the
    formatted content will be appended safely at the end of the template.
    """
    from docx import Document
    from docx.shared import Pt

    def _parse_sections(text: str) -> list[dict]:
        out: list[dict] = []
        current: dict | None = None
        for line in (text or "").splitlines():
            if line.startswith("## "):
                if current:
                    out.append(current)
                current = {"heading": line.replace("## ", "", 1).strip(), "body": []}
            elif current is not None:
                current["body"].append(line)
        if current:
            out.append(current)
        return out

    def _outline_from_structure(items: list) -> str:
        lines = []
        for s in items or []:
            if isinstance(s, dict):
                num = str(s.get("number", "")).strip()
                title = str(s.get("title", "")).strip()
                lines.append(f"{num} {title}".strip())
        return "\n".join([ln for ln in lines if ln])

    def _docx_has_placeholders(doc: Document) -> bool:
        markers = ("{{", "}}", "{%", "%}")
        texts = []
        texts.extend(p.text for p in doc.paragraphs)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    texts.extend(p.text for p in cell.paragraphs)
        return any(any(m in t for m in markers) for t in texts)

    def _add_markdown_line(doc: Document, line: str) -> None:
        stripped = (line or "").strip()
        if not stripped:
            doc.add_paragraph("")
            return
        if stripped.startswith("### "):
            doc.add_heading(stripped.replace("### ", "", 1).strip(), level=3)
            return
        if stripped.startswith("## "):
            doc.add_heading(stripped.replace("## ", "", 1).strip(), level=2)
            return
        if stripped.startswith("# "):
            doc.add_heading(stripped.replace("# ", "", 1).strip(), level=1)
            return
        if stripped.startswith(("- ", "• ")):
            doc.add_paragraph(stripped[2:].strip(), style="List Bullet")
            return
        if re.match(r"^\d+[\.)]\s+", stripped):
            doc.add_paragraph(re.sub(r"^\d+[\.)]\s+", "", stripped), style="List Number")
            return

        # Basic bold support for lines containing **text** while preserving simplicity.
        p = doc.add_paragraph()
        parts = re.split(r"(\*\*[^*]+\*\*)", stripped)
        for part in parts:
            if part.startswith("**") and part.endswith("**") and len(part) > 4:
                r = p.add_run(part[2:-2])
                r.bold = True
            else:
                p.add_run(part)

    def _append_generated_content(doc: Document, content: str) -> None:
        if len(doc.paragraphs) > 0 or len(doc.tables) > 0:
            doc.add_page_break()
        title = plan_type or "Generated Plan"
        doc.add_heading(title, level=1)
        if project_name:
            p = doc.add_paragraph()
            p.add_run("Project: ").bold = True
            p.add_run(project_name)
        p = doc.add_paragraph()
        p.add_run("Generated: ").bold = True
        p.add_run(datetime.now().strftime("%Y-%m-%d %H:%M"))
        doc.add_paragraph("")

        for line in (content or "").splitlines():
            _add_markdown_line(doc, line)

        # Apply a readable default font size to generated paragraphs only where possible.
        try:
            for para in doc.paragraphs:
                for run in para.runs:
                    if run.font.size is None:
                        run.font.size = Pt(10)
        except Exception:
            pass

    sections = _parse_sections(plan_content)
    metadata_context = {
        "project_name": project_name or "",
        "plan_type": plan_type or "",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "outline": _outline_from_structure(structure),
        # Intentionally blank to avoid raw Markdown injection through docxtpl.
        "content": "",
        "sections": [],
        "structure": structure or [],
    }

    if template_bytes:
        base_doc = Document(io.BytesIO(template_bytes))
        has_placeholders = _docx_has_placeholders(base_doc)

        if has_placeholders:
            try:
                from docxtpl import DocxTemplate
                tpl = DocxTemplate(io.BytesIO(template_bytes))
                tpl.render(metadata_context)
                rendered = io.BytesIO()
                tpl.save(rendered)
                rendered.seek(0)
                doc = Document(rendered)
                _append_generated_content(doc, plan_content)
                buf = io.BytesIO(); doc.save(buf); return buf.getvalue()
            except Exception as e:
                log.warning(f"docxtpl metadata render failed, falling back to safe append: {e}")
                doc = Document(io.BytesIO(template_bytes))
                _append_generated_content(doc, plan_content)
                buf = io.BytesIO(); doc.save(buf); return buf.getvalue()

        _append_generated_content(base_doc, plan_content)
        buf = io.BytesIO(); base_doc.save(buf); return buf.getvalue()

    doc = Document()
    _append_generated_content(doc, plan_content)
    buf = io.BytesIO(); doc.save(buf); return buf.getvalue()


def build_docgen_context() -> str:
    parts = []
    if st.session_state.get("tender_report", "").strip():
        parts.append(truncate_to_token_budget(st.session_state.tender_report, 3000))
    if st.session_state.get("tender_texts"):
        for name, txt in list(st.session_state.tender_texts.items())[:4]:
            parts.append(f"=== {name} ===\n{truncate_to_token_budget(txt, 2200)}")
    return "\n\n".join(parts) if parts else "No tender context loaded."


def generate_json_via_ai(system_prompt: str, user_prompt: str) -> dict:
    client = get_client()
    if not client:
        return {}
    return call_ai_json(client, system_prompt, user_prompt)


def build_visual_prompt(text: str, mode: str) -> dict:
    prompt_kind = "3D isometric infographic" if mode == "Methodology" else "flat-style professional layout"
    prompt = (
        f"{prompt_kind}, Navy Blue and Gold corporate palette, "
        f"clean executive composition, premium construction proposal aesthetic, "
        f"technical detail, crisp labels, polished presentation, tailored to: {truncate_to_token_budget(text, 650)}"
    )
    return {
        "type": mode, "prompt": prompt,
        "negative_prompt": "cartoon, neon, childish, messy layout, oversaturated colors, low resolution",
        "aspect_ratio": "16:9",
        "style_notes": "Corporate, technical, proposal-ready",
    }


# ─────────────────────────────────────────────────────────────────────────────
# PDF GENERATORS (Comparison + Go/No-Go)
# ─────────────────────────────────────────────────────────────────────────────
def generate_comparison_pdf(projects: list[dict], decision: dict, title: str) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors as rlcolors
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

    NAVY = rlcolors.HexColor("#003087"); GOLD = rlcolors.HexColor("#FFB81C")
    GREEN = rlcolors.HexColor("#16A34A"); RED = rlcolors.HexColor("#DC2626")
    AMBER = rlcolors.HexColor("#D97706"); L_NAVY = rlcolors.HexColor("#EFF6FF")
    GRAY = rlcolors.HexColor("#64748B"); BLACK = rlcolors.HexColor("#0F172A")
    WHITE = rlcolors.white

    REGULAR_FONT, BOLD_FONT = get_pdf_font_names()

    def P(txt, size=9, color=BLACK, font=None, align=TA_LEFT, leading=None):
        font_name = pdf_font_alias(font, REGULAR_FONT, BOLD_FONT)
        return Paragraph(prepare_pdf_text(txt), ParagraphStyle("__", fontSize=size, textColor=color,
                                              fontName=font_name, alignment=align, leading=leading or size + 4))

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=16*mm, rightMargin=16*mm,
                            topMargin=10*mm, bottomMargin=12*mm)
    usable = A4[0] - 32*mm
    story = []

    hdr = Table([[
        P("<b>TenderLens Pro</b>", 13, GOLD, "Helvetica-Bold"),
        P("<b>Multi-Tender Comparison Report</b>", 12, WHITE, "Helvetica-Bold", TA_CENTER),
        P(datetime.now().strftime("%d %b %Y"), 9, rlcolors.HexColor("#93A5C8"), align=TA_RIGHT),
    ]], colWidths=[usable*0.28, usable*0.44, usable*0.28])
    hdr.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), NAVY),
        ("TOPPADDING", (0,0), (-1,-1), 14), ("BOTTOMPADDING", (0,0), (-1,-1), 14),
        ("LINEBELOW", (0,0), (-1,0), 3, GOLD),
    ]))
    story.append(hdr); story.append(Spacer(1, 4*mm))
    story.append(P(f"<b>{title}</b>", 12, NAVY, "Helvetica-Bold"))
    story.append(Spacer(1, 2*mm))

    matrix = [["Tender", "Readiness", "Compliance", "Clause Risk", "Milestones", "Timeline Pressure"]]
    for row in projects:
        matrix.append([
            row["name"], f"{row['readiness_score']}/100", f"{row['compliance_score']}%",
            f"{row['n_high_clauses']} high / {row['n_total_clauses']}",
            f"{row['n_urgent_milestones']} urgent / {row['n_total_milestones']}",
            row["timeline_pressure"],
        ])

    mt = Table(matrix, colWidths=[usable*0.18, usable*0.12, usable*0.12, usable*0.18, usable*0.16, usable*0.24])
    mt.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY), ("TEXTCOLOR", (0,0), (-1,0), WHITE),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, L_NAVY]),
        ("GRID", (0,0), (-1,-1), 0.4, rlcolors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 6), ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    story.append(mt); story.append(Spacer(1, 5*mm))

    verdict = decision.get("verdict", "GO WITH CAUTION")
    color = GREEN if verdict == "GO" else RED if verdict == "NO-GO" else AMBER
    story.append(P(f"<b>Best Bet Recommendation:</b> <font color='{color.hexval()}'>{verdict}</font>",
                   11, NAVY, "Helvetica-Bold"))
    story.append(Spacer(1, 2*mm))
    story.append(P(decision.get("summary", ""), 9, BLACK, leading=14))
    story.append(Spacer(1, 2*mm))

    for i, b in enumerate(decision.get("bullets", [])[:3], 1):
        story.append(P(f"<b>{i}.</b> {b}", 9, BLACK, leading=14))
    story.append(Spacer(1, 3*mm))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD))
    story.append(P("CONFIDENTIAL — For Executive Review Only", 7, RED, align=TA_CENTER))

    doc.build(story); return buf.getvalue()


def generate_gonogo_pdf(verdict_data: dict, dashboard_data: dict, project_name: str = "Tender Project") -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors as rlcolors
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

    NAVY = rlcolors.HexColor("#003087"); GOLD = rlcolors.HexColor("#FFB81C")
    GREEN = rlcolors.HexColor("#16A34A"); RED = rlcolors.HexColor("#DC2626")
    AMBER = rlcolors.HexColor("#D97706"); L_NAVY = rlcolors.HexColor("#EFF6FF")
    L_RED = rlcolors.HexColor("#FEF2F2"); L_AMB = rlcolors.HexColor("#FFFBEB")
    L_GRN = rlcolors.HexColor("#F0FDF4"); GRAY = rlcolors.HexColor("#64748B")
    BLACK = rlcolors.HexColor("#0F172A"); WHITE = rlcolors.white

    verdict = verdict_data.get("verdict", "GO WITH CAUTION")
    score = int(verdict_data.get("overall_score", 0))
    if verdict == "GO": vcolor, vbg = GREEN, L_GRN
    elif verdict == "NO-GO": vcolor, vbg = RED, L_RED
    else: vcolor, vbg = AMBER, L_AMB

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm,
                            topMargin=10*mm, bottomMargin=15*mm)
    W = A4[0] - 36*mm

    REGULAR_FONT, BOLD_FONT = get_pdf_font_names()

    def P(txt, size=9, color=BLACK, font=None, align=TA_LEFT, leading=None):
        font_name = pdf_font_alias(font, REGULAR_FONT, BOLD_FONT)
        return Paragraph(prepare_pdf_text(txt), ParagraphStyle("__", fontSize=size, textColor=color,
                                              fontName=font_name, alignment=align, leading=leading or (size+4)))

    story = []
    hdr = Table([[
        P("<b>TenderLens Pro</b>", 13, GOLD, "Helvetica-Bold", TA_LEFT),
        P("<b>EXECUTIVE BID DECISION REPORT</b><br/>Go / No-Go Analysis", 12, WHITE, "Helvetica-Bold", TA_CENTER),
        P(f"{datetime.now().strftime('%d %b %Y')}", 9, rlcolors.HexColor("#93A5C8"), align=TA_RIGHT),
    ]], colWidths=[W*0.28, W*0.44, W*0.28])
    hdr.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,-1), NAVY),
        ("TOPPADDING", (0,0),(-1,-1), 14), ("BOTTOMPADDING", (0,0),(-1,-1), 14),
        ("LINEBELOW", (0,0),(-1,0), 3, GOLD), ("VALIGN", (0,0),(-1,-1), "MIDDLE"),
    ]))
    story.append(hdr); story.append(Spacer(1, 4*mm))

    meta = Table([[
        P(f"<b>Project:</b> {safe_html(project_name)}", 9, BLACK),
        P("<b>Prepared by:</b> TenderLens AI Engine", 9, BLACK, align=TA_CENTER),
        P("<font color='#DC2626'><b>CONFIDENTIAL</b></font>", 9, align=TA_RIGHT),
    ]], colWidths=[W*0.40, W*0.35, W*0.25])
    meta.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,-1), L_NAVY),
        ("TOPPADDING", (0,0),(-1,-1), 6), ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("BOX", (0,0),(-1,-1), 0.5, rlcolors.HexColor("#BFDBFE")),
    ]))
    story.append(meta); story.append(Spacer(1, 5*mm))

    confidence = verdict_data.get("confidence", "MEDIUM")
    conf_colors = {"HIGH": "#16A34A", "MEDIUM": "#D97706", "LOW": "#DC2626"}
    verd_box = Table([[
        P(f"<b>{verdict}</b>", 32, vcolor, "Helvetica-Bold", TA_CENTER),
        Table([[
            P("<b>Readiness Score</b>", 9, NAVY, "Helvetica-Bold", TA_CENTER),
            P(f"<b>{score}</b>/100", 28, NAVY, "Helvetica-Bold", TA_CENTER),
            P(f"Confidence: <b>{confidence}</b>", 8,
              rlcolors.HexColor(conf_colors.get(confidence, "#D97706")), align=TA_CENTER),
        ]], colWidths=[W*0.22]),
    ]], colWidths=[W*0.74, W*0.26])
    verd_box.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(0,0), vbg),
        ("BACKGROUND", (1,0),(1,0), rlcolors.HexColor("#F8FAFC")),
        ("BOX", (0,0),(0,0), 2.5, vcolor), ("BOX", (1,0),(1,0), 1, NAVY),
        ("TOPPADDING", (0,0),(-1,-1), 12), ("BOTTOMPADDING", (0,0),(-1,-1), 12),
        ("VALIGN", (0,0),(-1,-1), "MIDDLE"),
    ]))
    story.append(verd_box); story.append(Spacer(1, 4*mm))

    exec_sum = verdict_data.get("executive_summary", "")
    if exec_sum:
        story.append(P("<b>Executive Summary</b>", 11, NAVY, "Helvetica-Bold"))
        story.append(Spacer(1, 2*mm))
        es_t = Table([[P(safe_html(exec_sum), 9, BLACK, leading=14)]], colWidths=[W])
        es_t.setStyle(TableStyle([
            ("BACKGROUND", (0,0),(-1,-1), L_NAVY), ("BOX", (0,0),(-1,-1), 1, NAVY),
            ("TOPPADDING", (0,0),(-1,-1), 8), ("BOTTOMPADDING", (0,0),(-1,-1), 8),
        ]))
        story.append(es_t); story.append(Spacer(1, 4*mm))

    bullets = verdict_data.get("bullets", [])
    if bullets:
        story.append(P("<b>Decision Justification</b>", 11, NAVY, "Helvetica-Bold"))
        story.append(Spacer(1, 2*mm))
        for i, b in enumerate(bullets, 1):
            story.append(P(f"<b>{i}.</b>  {safe_html(b)}", 9, BLACK, leading=14))
            story.append(Spacer(1, 1.5*mm))

    story.append(HRFlowable(width="100%", thickness=2, color=GOLD, spaceAfter=3))
    story.append(Table([[
        P("TenderLens Pro · Bid Intelligence Platform", 7, GRAY),
        P("CONFIDENTIAL — For Authorized Recipients Only", 7, RED, align=TA_CENTER),
        P(f"Generated: {datetime.now().strftime('%d %b %Y %H:%M')}", 7, GRAY, align=TA_RIGHT),
    ]], colWidths=[W/3, W/3, W/3]))

    doc.build(story); return buf.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# AI PROMPTS — UNCHANGED (Arabic + English)
# ─────────────────────────────────────────────────────────────────────────────
TENDER_ANALYSIS_PROMPT = """أنت مهندس فني أول لإعداد العروض الفنية وخبير تحليل وثائق مناقصات في قطاع المقاولات.

السياق: مقدم العرض هو شركة الرواف. مطلوب تحليل وثائق الجهة المالكة لاستخراج كل ما يجب على شركة الرواف الالتزام به في العرض الفني والتقديم.

مهمتك: إصدار تقرير تحليل مناقصة واحد، غزير، دقيق، عملي، وقابل للاستخدام مباشرة من فريق العروض الفنية.

قواعد صارمة:
1. اعتمد فقط على النصوص المرفوعة داخل الطلب. لا تفترض أي نطاق أو شرط أو مدة أو مورد غير ظاهر.
2. لكل معلومة مهمة اذكر مصدرها باسم الملف كما يظهر في السياق، قدر الإمكان.
3. استخرج كل متطلب تطلبه الجهة المالكة من مقدم العرض، وليس فقط وصف المشروع.
4. استخرج جميع الأرقام والنسب والمدد والكميات والمواعيد والغرامات والضمانات وشروط التقديم كما وردت.
5. افصل بين: متطلبات فنية، متطلبات تقديم، متطلبات منهجيات، متطلبات موارد، متطلبات جودة، متطلبات سلامة، متطلبات برنامج زمني، ومتطلبات مستندات.
6. إذا لم تظهر المعلومة في الوثائق، اكتب: غير محددة في الوثائق المرفوعة.
7. لا تستخدم لغة عامة مثل "حسب المواصفات" فقط؛ اذكر نص/مضمون المتطلب المحدد إن ظهر.
8. إذا وجدت بنداً بكمية صفر في جدول الكميات، اذكره في قسم مستقل بعنوان [بنود كمية صفر تحتاج تحقق] ولا تدرجه ضمن النطاق التنفيذي المعتمد.

هيكل التقرير المطلوب:

# 📋 الملخص التنفيذي للمنافسة
- طبيعة المشروع كما تظهر في الوثائق.
- درجة وضوح الوثائق.
- أهم متطلبات الجهة المالكة من مقدم العرض.
- أهم مخاطر أو فجوات تؤثر على قرار التقديم.

# 1. بطاقة حقائق المشروع
جدول يحتوي على: اسم المشروع، الجهة المالكة، موقع الأعمال، مدة المشروع، نطاق العمل، نوع العقد/الاتفاقية، موعد التقديم، مصادر كل معلومة.

# 2. نطاق العمل المستخلص
اعرض نطاق الأعمال والحزم التنفيذية كما تظهر في الوثائق، مع عدم إضافة أعمال غير مذكورة.

# 3. مصفوفة متطلبات الجهة المالكة من مقدم العرض
جدول إلزامي بالأعمدة التالية:
- رقم
- المتطلب المطلوب من مقدم العرض
- التصنيف: فني / إداري / تقديم / جودة / سلامة / زمني / موارد / وثائق / مالي-تعاقدي
- درجة الأهمية: حرج / رئيسي / داعم
- المصدر: اسم الملف أو البند إن توفر
- أثره على العرض الفني
- الإجراء المطلوب من شركة الرواف

# 4. المتطلبات الفنية والكودية
استخرج المواصفات الفنية، الأكواد، المعايير، المواد، الاختبارات، حدود القبول، ومتطلبات التنفيذ الواضحة.

# 5. المنهجيات والخطط المطلوبة في العرض الفني
اذكر كل منهجية أو خطة أو بيان طريقة تنفيذ تطلبه الوثائق صراحة أو يلزم لإثبات الامتثال الفني، مع مصدر كل مطلب.

# 6. الموارد والكوادر والمعدات المطلوبة
استخرج أي متطلبات للهيكل التنظيمي، الخبرات، المؤهلات، العمالة، المعدات، أو المقاولين/الموردين.

# 7. متطلبات الجودة والسلامة والبيئة
استخرج متطلبات ضبط الجودة، الفحوصات، السلامة، الصحة المهنية، البيئة، التصاريح، وخطط الموقع.

# 8. البرنامج الزمني والمواعيد والالتزامات الزمنية
استخرج مدة المشروع، تواريخ التقديم، الاستفسارات، الزيارات، الإنجاز، الضمانات، والقيود الزمنية.

# 9. جدول الكميات والأرقام المؤثرة
استخرج البنود والكميات والأرقام الحرجة التي تؤثر على النطاق الفني، مع تمييز أي بنود كمية صفر إن وجدت.

# 10. الشروط التعاقدية المؤثرة على العرض الفني
استخرج شروط الدفع، الغرامات، الضمانات، التأمينات، الفيديك أو الشروط الخاصة، وأثرها على التجهيز الفني.

# 11. الفجوات والتعارضات ونقاط الاستفسار
جدول بالأعمدة: رقم، الفجوة/التعارض/السؤال، سبب الأهمية، المصدر، الإجراء المقترح.

# 12. توصيات إعداد العرض الفني لشركة الرواف
اكتب توصيات عملية مباشرة للفريق: ماذا يجب تضمينه، ماذا يجب التحقق منه، وما الأولويات قبل التقديم.
"""

PROPOSAL_REVIEW_PROMPT = """أنت خبير تقييم عروض فنية دولي متخصص في مراجعة مطابقة العروض مع متطلبات الجهات المالكة.

التعليمات:
1. استخرج كل متطلب من وثائق الجهة المالكة وقيّم مدى استجابة العرض الفني له.
2. أعطِ تقييماً لكل بند: ✅ مستوفى / ⚠️ مستوفى جزئياً / ❌ غير مستوفى
3. اذكر رقم الصفحة أو البند من كل وثيقة عند الإشارة إليها.
4. كن صارماً وموضوعياً — أي نقص يجب الإشارة إليه بوضوح.

# 🎯 ملخص المطابقة العام
# 1. مطابقة نطاق العمل
# 2. مطابقة المنهجية والأسلوب التنفيذي
# 3. مطابقة الخبرات والكفاءات
# 4. مطابقة خطة الزمن والموارد
# 5. مطابقة متطلبات QHSE والبيئة
# 6. النواقص الجوهرية (Critical Gaps)
# 7. نقاط القوة في العرض
# 8. التوصيات والإجراءات المطلوبة

تقييم الامتثال النهائي:
- نسبة الامتثال: X%
- مستوى المخاطرة في التقديم: عالٍ / متوسط / منخفض
- التوصية: تقديم العرض / معالجة النواقص أولاً / إعادة الدراسة"""

FEEDBACK_REPORT_PROMPT = """أنت مهندس أول ومستشار عقود في لجنة تقييم العطاءات. اكتب تقرير تغذية راجعة رسمي بالعربية.

# EXECUTIVE_SUMMARY
[ملخص تنفيذي 4-6 جمل: النتيجة، نسبة الامتثال %، الجاهزية، التوصية]

# COMPLIANT_AREAS
[المتطلبات المُلتزم بها — قائمة رقمية مع الإيجابيات]

# CRITICAL_GAPS
[الثغرات والنواقص — مع مرجع كل بند، شدة الثغرة: 🔴 حرج / 🟡 رئيسي / 🟢 ثانوي]

# CORRECTIVE_ACTIONS
[Checklist رقمية بإجراءات + الجهة المسؤولة + الأولوية]"""

CLAUSE_TRACKER_PROMPT = """أنت محامٍ عقود متخصص في FIDIC ومشاريع البنية التحتية.

استخرج البنود حسب الفئات:
1. FIDIC_CLAUSE  2. PAYMENT  3. LIQUIDATED_DAMAGES  4. VARIATIONS  5. WARRANTIES

لكل بند أعِد JSON بالحقول: category, clause_ref, title, extracted_text, risk_level (HIGH/MEDIUM/LOW), risk_notes (AR), action_required (AR).

أعِد النتيجة كـ JSON array فقط."""

GONOGO_PROMPT = """You are a senior bid director with 20+ years in infrastructure tenders.

Return ONLY valid JSON:
{
  "verdict": "GO" | "NO-GO" | "GO WITH CAUTION",
  "overall_score": <0-100>,
  "confidence": "HIGH" | "MEDIUM" | "LOW",
  "executive_summary": "2-3 sentences",
  "bullets": ["just1", "just2", "just3"],
  "key_risks": ["risk1", "risk2", "risk3"],
  "key_opportunities": ["opp1", "opp2"],
  "recommended_actions": ["action1", "action2", "action3"]
}

Decision criteria:
- GO: compliance>=75 AND high_risk_clauses<=2 AND no_missed_deadlines
- NO-GO: compliance<40 OR high_risk_clauses>=8 OR submission_past
- Otherwise: GO WITH CAUTION"""

MILESTONE_PROMPT = """استخرج كل المواعيد والمعالم الزمنية من وثيقة المناقصة كـ JSON array.

لكل موعد: category, milestone, date_text, date_iso (YYYY-MM-DD أو ""), time_text, source_clause, notes, priority (HIGH/MEDIUM/LOW).

الفئات: Bid Submission | Site Visit | Clarification | Bid Bond | Performance Bond | Contract Award | Contract Duration | Mobilization | Completion | DLP | Insurance | Other

أعِد JSON array فقط."""

BOQ_AI_PROMPT = """استخرج بنود BOQ من النص كـ JSON array.

لكل بند: item_no, description, unit (m/m2/m3/t/kg/ls/nr/hr/day), quantity (رقم أو "LS").

تجاهل صفوف العناوين والمجاميع. أعِد JSON array فقط."""

CHAT_SYSTEM = """أنت مساعد هندسي متخصص في تحليل وثائق المناقصات.
أجب بدقة هندسية، استشهد بالنصوص، اذكر الصفحة أو البند.
إذا لم تجد المعلومة، قل ذلك صراحةً. أجب بالعربية."""

STRUCTURE_EXTRACTION_PROMPT = """Extract the COMPLETE structural outline from this DOCX template as JSON array.

Each object: {"level": 1|2|3, "number": "1.1.2" or "", "title": "..."}.

Include EVERY heading, preserve exact numbering. Return JSON array only."""

DOCGEN_CONTENT_PROMPT = """You are a senior {plan_type} specialist. Write a complete professional plan.

PROJECT CONTEXT:
{project_context}

STRUCTURE TO FOLLOW:
{structure_outline}

RULES:
1. Write detailed content for EVERY heading.
2. Match enterprise 50-page plan depth.
3. Use exact section numbers as "## NUMBER TITLE".
4. Project-specific content from RFP context.
5. Formal technical English (Arabic if context is Arabic).

Start directly with first section."""

VISUAL_PROMPTER_PROMPT = """Convert input to AI image prompt.
- Methodologies → "3D isometric infographic"
- Org charts → "flat-style professional layout"
- Navy Blue + Gold palette
Return JSON: type, prompt, negative_prompt, aspect_ratio, style_notes."""

SBC_SCANNER_PROMPT = """Saudi construction compliance specialist.
Scan for SBC (Saudi Building Code), local standards, technical compliance.
Note: "SEC" = Saudi engineering specifications (NOT Securities Exchange).

Return JSON: {findings: [{category, reference, issue, importance, recommendation}], summary}"""

STAKEHOLDER_MAPPER_PROMPT = """Senior tender analyst — extract ALL external entities, government bodies, utilities, third parties.

Return JSON: {stakeholders: [{authority_name, role_in_project, permits_nocs_coordination, source_reference}], summary}"""


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INIT — SINGLE SOURCE OF TRUTH
# ─────────────────────────────────────────────────────────────────────────────
_DEFAULTS = {
    "module": "tender",
    "user_api_key": "",
    "openai_model": DEFAULT_MODEL,
    "tender_texts": {}, "tender_report": "", "tender_chat": [],
    "req_texts": {}, "prop_texts": {}, "review_report": "", "review_chat": [],
    "feedback_report": "",
    "boq_texts": {}, "boq_tables_raw": {}, "boq_df": None, "boq_source": "auto",
    "clause_texts": {}, "clause_df": None,
    "milestone_texts": {}, "milestone_df": None,
    "gonogo_verdict": None,
    "docgen_ref_texts":  {"pm": None, "risk": None, "quality": None, "safety": None},
    "docgen_ref_names":  {"pm": "", "risk": "", "quality": "", "safety": ""},
    "docgen_ref_bytes":  {},
    "docgen_structures": {"pm": None, "risk": None, "quality": None, "safety": None},
    "docgen_outputs":    {"pm": "", "risk": "", "quality": "", "safety": ""},
    "tech_outputs":      {"visual": "", "sbc": "", "stakeholders": ""},
}
for _k, _v in _DEFAULTS.items():
    st.session_state.setdefault(_k, _v)
    # ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:16px 0 8px;">
        <div style="font-size:2.2rem;">🏛️</div>
        <div style="color:#FFB81C; font-size:1.1rem; font-weight:800; line-height:1.2;">
            TenderLens Pro | By Eng. Ahmed Almaamari
        </div>
        <div style="color:#6B82A8; font-size:0.72rem; margin-top:4px;">Enterprise Tender Intelligence</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── API KEY SECTION (NEW — Direct OpenAI) ───────────────────────────────
    st.markdown('<span style="color:#FFB81C;font-weight:700;font-size:0.78rem;'
                'text-transform:uppercase;letter-spacing:.5px;">🔑 OpenAI API</span>',
                unsafe_allow_html=True)

    with st.expander("إعدادات المفتاح والنموذج", expanded=not st.session_state.get("user_api_key")):
        entered_key = st.text_input(
            "OpenAI API Key",
            value=st.session_state.get("user_api_key", ""),
            type="password",
            placeholder="sk-proj-...",
            help="يُحفظ في جلسة المتصفح فقط. ولن يتم إرساله لأي خادم خارجي.",
            key="_api_key_input",
        )
        if entered_key != st.session_state.get("user_api_key", ""):
            st.session_state["user_api_key"] = entered_key.strip()
            try:
                _build_openai_client.clear()
            except Exception:
                pass
            if entered_key.strip():
                st.success("✅ تم حفظ المفتاح.")

        st.session_state["openai_model"] = st.selectbox(
            "النموذج (Model)",
            options=AVAILABLE_MODELS,
            index=AVAILABLE_MODELS.index(st.session_state.get("openai_model", DEFAULT_MODEL))
            if st.session_state.get("openai_model", DEFAULT_MODEL) in AVAILABLE_MODELS else 0,
        )

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔌 اختبار", use_container_width=True, key="api_test_btn"):
                ok, msg = test_api_connection()
                (st.success if ok else st.error)(msg)
        with col_b:
            if st.button("🗑️ مسح", use_container_width=True, key="api_clear_btn"):
                st.session_state["user_api_key"] = ""
                try:
                    _build_openai_client.clear()
                except Exception:
                    pass
                st.rerun()

    if st.session_state.get("user_api_key"):
        st.markdown('<div class="api-status-ok">🟢 OpenAI متصل</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="api-status-bad">🔴 لم يتم إدخال المفتاح</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ── MODULE SELECTOR ─────────────────────────────────────────────────────
    st.markdown('<span style="color:#FFB81C;font-weight:700;font-size:0.78rem;'
                'text-transform:uppercase;letter-spacing:.5px;">الوحدة النشطة</span>',
                unsafe_allow_html=True)

    _module_opts = ["tender", "review", "boq", "clauses", "milestones", "gonogo", "compare", "docgen"]
    _module_labels = {
        "tender":     "📊 محلل المناقصات",
        "review":     "🔍 مراجعة العروض الفنية",
        "boq":        "📐 مستخرج كميات BOQ",
        "clauses":    "📌 متتبع البنود التعاقدية",
        "milestones": "📅 متتبع المواعيد النهائية",
        "gonogo":     "🚦 قرار Go / No-Go",
        "compare":    "🏁 مقارنة المناقصات",
        "docgen":     "📝 مولّد الخطط الرسمية",
    }
    _cur_idx = _module_opts.index(st.session_state.module) if st.session_state.module in _module_opts else 0
    module = st.radio(
        "اختر الوحدة", options=_module_opts,
        format_func=lambda x: _module_labels[x],
        index=_cur_idx, label_visibility="collapsed",
    )
    st.session_state.module = module

    st.markdown("---")

    # ── PER-MODULE FILE UPLOADERS ───────────────────────────────────────────
    tender_files = []
    req_files = []
    prop_files = []
    boq_files = []
    clause_files = []
    milestone_files = []

    if module == "tender":
        st.markdown('<span style="color:#FFB81C;font-weight:700;font-size:0.78rem;'
                    'text-transform:uppercase;letter-spacing:.5px;">رفع وثائق المناقصة</span>',
                    unsafe_allow_html=True)
        st.caption("PDF فقط · الحد الأقصى 50MB لكل ملف")
        tender_files = st.file_uploader(
            "ملفات المناقصة", type=["pdf"], accept_multiple_files=True,
            key="tender_uploader", label_visibility="collapsed",
        )

    elif module == "review":
        st.markdown('<span style="color:#FFB81C;font-weight:700;font-size:0.78rem;">'
                    'متطلبات الجهة المالكة</span>', unsafe_allow_html=True)
        req_files = st.file_uploader("متطلبات", type=["pdf"], accept_multiple_files=True,
                                      key="req_uploader", label_visibility="collapsed")
        st.markdown("---")
        st.markdown('<span style="color:#FFB81C;font-weight:700;font-size:0.78rem;">'
                    'العرض الفني للمقاول</span>', unsafe_allow_html=True)
        prop_files = st.file_uploader("العرض الفني", type=["pdf"], accept_multiple_files=True,
                                       key="prop_uploader", label_visibility="collapsed")

    elif module == "boq":
        st.markdown('<span style="color:#FFB81C;font-weight:700;font-size:0.78rem;">ملفات BOQ</span>',
                    unsafe_allow_html=True)
        boq_files = st.file_uploader("BOQ", type=["pdf"], accept_multiple_files=True,
                                      key="boq_uploader", label_visibility="collapsed")
        st.markdown("---")
        boq_method = st.radio(
            "طريقة الاستخراج", options=["auto", "ai"],
            format_func=lambda x: "⚡ تلقائي" if x == "auto" else "🧠 ذكاء اصطناعي",
            index=0 if st.session_state.boq_source == "auto" else 1,
        )
        st.session_state.boq_source = boq_method

    elif module == "clauses":
        st.markdown('<span style="color:#FFB81C;font-weight:700;font-size:0.78rem;">'
                    'وثائق العقد</span>', unsafe_allow_html=True)
        clause_files = st.file_uploader("عقد", type=["pdf"], accept_multiple_files=True,
                                         key="clause_uploader", label_visibility="collapsed")

    elif module == "milestones":
        st.markdown('<span style="color:#FFB81C;font-weight:700;font-size:0.78rem;">'
                    'وثائق المناقصة</span>', unsafe_allow_html=True)
        milestone_files = st.file_uploader("RFP", type=["pdf"], accept_multiple_files=True,
                                            key="milestone_uploader", label_visibility="collapsed")

    elif module == "compare":
        st.markdown('<span style="color:#FFB81C;font-weight:700;font-size:0.78rem;">المقارنة</span>',
                    unsafe_allow_html=True)
        compare_names_avail = list(st.session_state.get("tender_texts", {}).keys())
        st.session_state["compare_selection"] = st.multiselect(
            "اختر المناقصات", options=compare_names_avail,
            default=compare_names_avail[:2] if len(compare_names_avail) >= 2 else compare_names_avail,
            max_selections=3, label_visibility="collapsed", key="cmp_select",
        )

    st.markdown("---")
    st.caption("TenderLens Pro v3.0 · OpenAI Direct Edition")


# ─────────────────────────────────────────────────────────────────────────────
# MASTHEAD
# ─────────────────────────────────────────────────────────────────────────────
_MAST = {
    "tender":     ("محلل وثائق المناقصات", "Tender Document Analysis Engine", "Module 1 · Analysis"),
    "review":     ("مراجعة العروض الفنية", "Technical Proposal Compliance Review", "Module 2 · Review"),
    "boq":        ("مستخرج كميات BOQ", "BOQ Quantities Extractor", "Module 3 · BOQ"),
    "clauses":    ("متتبع البنود التعاقدية", "Smart Clause Tracker", "Module 4 · Clauses"),
    "milestones": ("متتبع المواعيد النهائية", "Tender Deadline & Milestone Tracker", "Module 5 · Milestones"),
    "gonogo":     ("لوحة قرار Go / No-Go", "Bid Decision Dashboard", "Module 6 · Go/No-Go"),
    "compare":    ("مقارنة وترتيب المناقصات", "Multi-Tender Comparison", "Module 7 · Compare"),
    "docgen":     ("مولّد الخطط الرسمية", "Reference-Based Document Generator", "Module 8 · DocGen"),
}
_title, _subtitle, _badge = _MAST.get(st.session_state.module, _MAST["tender"])

st.markdown(f"""
<div class="masthead">
  <div>
    <div class="masthead-title">🏛️ TenderLens Pro | By Eng. Ahmed Almaamari</div>
    <div class="masthead-sub">{safe_html(_subtitle)}</div>
  </div>
  <div class="masthead-badge">{safe_html(_badge)}</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Helper: API guard before any AI button
# ─────────────────────────────────────────────────────────────────────────────
def _require_api() -> bool:
    if not st.session_state.get("user_api_key"):
        st.error("⚠️ يجب إدخال مفتاح OpenAI API من الشريط الجانبي قبل تشغيل الذكاء الاصطناعي.")
        return False
    return True


# ═════════════════════════════════════════════════════════════════════════════
# MODULE 1 — TENDER ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.module == "tender":
    for f in (tender_files or []):
        if f.name not in st.session_state.tender_texts:
            valid, msg = validate_uploaded_file(f)
            if not valid:
                st.warning(f"⚠️ {f.name}: {msg}")
                continue
            with st.spinner(f"جاري قراءة: {f.name}…"):
                raw = extract_text(f.read(), f.name)
                if raw:
                    st.session_state.tender_texts[f.name] = raw
                else:
                    st.error(f"❌ تعذّر قراءة {f.name}")

    if st.session_state.tender_texts:
        total_words = sum(word_count(v) for v in st.session_state.tender_texts.values())
        total_chars = sum(len(v) for v in st.session_state.tender_texts.values())
        total_tokens = sum(count_tokens(v) for v in st.session_state.tender_texts.values())
        c = st.columns(4)
        c[0].metric("الملفات", len(st.session_state.tender_texts))
        c[1].metric("الكلمات", f"{total_words:,}")
        c[2].metric("الأحرف", f"{total_chars:,}")
        c[3].metric("السياق", f"~{total_tokens:,} token")

        st.markdown("**الملفات المحملة:**")
        for fname in st.session_state.tender_texts:
            wc = word_count(st.session_state.tender_texts[fname])
            st.markdown(f'<div class="file-item">📄 {safe_html(fname)} · '
                        f'<span style="color:#718096">{wc:,} كلمة</span></div>',
                        unsafe_allow_html=True)

        cb1, cb2 = st.columns([3, 1])
        with cb1:
            run_analysis = st.button(f"🚀 تحليل {len(st.session_state.tender_texts)} ملف",
                                      use_container_width=True)
        with cb2:
            if st.button("🗑️ مسح", use_container_width=True, key="t_clear"):
                st.session_state.tender_texts = {}
                st.session_state.tender_report = ""
                st.session_state.tender_chat = []
                st.rerun()

        if run_analysis and _require_api():
            client = get_client()

            progress = st.progress(10, text="تجهيز التحليل المرحلي الآمن…")
            with st.spinner("🧠 يتم تحليل الوثائق على دفعات آمنة…"):
                # لا نرسل كل الملفات دفعة واحدة حتى لا يظهر خطأ Request too large.
                report = analyze_tender_in_batches(client, st.session_state.tender_texts)
                st.session_state.tender_report = report

            progress.progress(100, text="اكتمل!")
            time.sleep(0.4); progress.empty()
            if report.startswith("[AI Error"):
                st.error(report)
            else:
                st.success("✅ اكتمل التحليل المرحلي الآمن!")
    else:
        st.markdown("""
        <div style="text-align:center;padding:60px 0;color:#A0AEC0;">
            <div style="font-size:4rem;">📋</div>
            <h3 style="color:#003087;margin-top:16px;">ابدأ برفع وثائق المناقصة</h3>
            <p>ارفع ملفات PDF من الشريط الجانبي.</p>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.tender_report:
        st.markdown("---")
        tab_r, tab_c, tab_raw = st.tabs(["📊 التقرير", "💬 استفسر", "📄 النصوص"])

        with tab_r:
            d1, d2, d3 = st.columns(3)
            ts = datetime.now().strftime('%Y%m%d_%H%M')
            with d1:
                st.download_button("⬇️ TXT", st.session_state.tender_report.encode("utf-8"),
                                    f"TenderReport_{ts}.txt", "text/plain", use_container_width=True)
            with d2:
                jo = json.dumps({"generated_at": datetime.now().isoformat(),
                                  "report": st.session_state.tender_report}, ensure_ascii=False, indent=2)
                st.download_button("⬇️ JSON", jo.encode("utf-8"),
                                    f"TenderData_{ts}.json", "application/json", use_container_width=True)
            with d3:
                raw_combined = "\n\n".join(f"=== {n} ===\n{t}" for n, t in st.session_state.tender_texts.items())
                st.download_button("⬇️ Raw", raw_combined.encode("utf-8"),
                                    f"RawText_{ts}.txt", "text/plain", use_container_width=True)
            if st.button("🧹 تفريغ النصوص الخام من الذاكرة مع إبقاء التقرير", key="t_release_raw", use_container_width=True):
                st.session_state.tender_texts = {}
                st.session_state.tender_chat = []
                st.success("تم تفريغ النصوص الخام من الذاكرة. بقي التقرير النهائي محفوظاً.")
                st.rerun()
            st.markdown("---")

            sections = re.split(r'\n(?=# )', st.session_state.tender_report)
            for sec in sections:
                if not sec.strip():
                    continue
                lines = sec.strip().split("\n")
                heading = lines[0].replace("#", "").strip()
                body = "\n".join(lines[1:]).strip()
                sec_num_match = re.match(r'[📋\s]*(\d+)\.', heading)
                sec_num = sec_num_match.group(1) if sec_num_match else ""
                card_cls = "card card-gold" if sec_num in {"3", "4", "5", "8"} else "card"

                body_html = (safe_html(body)
                             .replace("\n", "<br>")
                             .replace("✅", '<span style="color:#38A169">✅</span>')
                             .replace("⚠️", '<span style="color:#D69E2E">⚠️</span>')
                             .replace("❌", '<span style="color:#E53E3E">❌</span>'))
                st.markdown(f'<div class="{card_cls}"><h4>{safe_html(heading)}</h4>'
                            f'<p>{body_html}</p></div>', unsafe_allow_html=True)

        with tab_c:
            st.markdown("##### استفسر عن أي تفصيل")
            for msg in st.session_state.tender_chat:
                if msg["role"] == "user":
                    st.markdown(f'<p class="chat-lbl" style="text-align:right">أنت</p>'
                                f'<div class="chat-user">{safe_html(msg["content"])}</div>',
                                unsafe_allow_html=True)
                else:
                    st.markdown(f'<p class="chat-lbl">TenderLens</p>'
                                f'<div class="chat-bot">{safe_html(msg["content"])}</div>',
                                unsafe_allow_html=True)

            with st.form("tender_chat_form", clear_on_submit=True):
                q = st.text_input("سؤالك", placeholder="ما قيمة الغرامة اليومية؟",
                                   label_visibility="collapsed")
                submitted = st.form_submit_button("إرسال →", use_container_width=True)

            if submitted and q.strip() and _require_api():
                client = get_client()
                combined = build_context_bundle(
                    st.session_state.tender_texts,
                    "وثيقة",
                    max_total_tokens=MAX_CHAT_CONTEXT_TOKENS,
                    per_file_tokens=8_000,
                )
                with st.spinner("جاري البحث…"):
                    answer = call_ai(client, CHAT_SYSTEM + f"\n\nالوثائق:\n{combined}", q)
                st.session_state.tender_chat.append({"role": "user", "content": q})
                st.session_state.tender_chat.append({"role": "bot", "content": answer})
                st.rerun()

            if st.session_state.tender_chat and st.button("مسح المحادثة", use_container_width=True):
                st.session_state.tender_chat = []
                st.rerun()

        with tab_raw:
            for fname, text in st.session_state.tender_texts.items():
                with st.expander(f"📄 {fname} ({word_count(text):,} كلمة)"):
                    st.text_area("", value=safe_truncate(text, 20000), height=350,
                                  label_visibility="collapsed", disabled=True, key=f"raw_t_{fname}")
                    st.download_button(f"تحميل {fname}", text.encode("utf-8"),
                                        Path(fname).stem + ".txt", "text/plain",
                                        use_container_width=True, key=f"dl_{fname}")


# ═════════════════════════════════════════════════════════════════════════════
# MODULE 2 — PROPOSAL COMPLIANCE REVIEW
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.module == "review":
    for f in (req_files or []):
        if f.name not in st.session_state.req_texts:
            valid, msg = validate_uploaded_file(f)
            if not valid: continue
            with st.spinner(f"قراءة: {f.name}…"):
                st.session_state.req_texts[f.name] = extract_text(f.read(), f.name)

    for f in (prop_files or []):
        if f.name not in st.session_state.prop_texts:
            valid, msg = validate_uploaded_file(f)
            if not valid: continue
            with st.spinner(f"قراءة: {f.name}…"):
                st.session_state.prop_texts[f.name] = extract_text(f.read(), f.name)

    n_req = len(st.session_state.req_texts)
    n_prop = len(st.session_state.prop_texts)

    cr1, cr2 = st.columns(2)
    with cr1:
        w_req = sum(word_count(v) for v in st.session_state.req_texts.values())
        st.markdown(f"""
        <div class="card"><h4>📁 وثائق المالك</h4>
        <p><span class="chip">{("✅ جاهز" if n_req else "⏳")}</span>
        <span class="chip chip-gray">{n_req} ملف · {w_req:,} كلمة</span></p></div>
        """, unsafe_allow_html=True)
        for fname in st.session_state.req_texts:
            st.markdown(f'<div class="file-item">📋 {safe_html(fname)}</div>', unsafe_allow_html=True)

    with cr2:
        w_prop = sum(word_count(v) for v in st.session_state.prop_texts.values())
        st.markdown(f"""
        <div class="card card-gold"><h4>📝 العرض الفني</h4>
        <p><span class="chip chip-gold">{("✅ جاهز" if n_prop else "⏳")}</span>
        <span class="chip chip-gray">{n_prop} ملف · {w_prop:,} كلمة</span></p></div>
        """, unsafe_allow_html=True)
        for fname in st.session_state.prop_texts:
            st.markdown(f'<div class="file-item">📝 {safe_html(fname)}</div>', unsafe_allow_html=True)

    st.markdown("---")
    can_review = n_req > 0 and n_prop > 0
    cb1, cb2 = st.columns([3, 1])
    with cb1:
        run_review = st.button("🔍 مراجعة الامتثال" if can_review else "⬆️ ارفع وثائق الطرفين",
                                use_container_width=True, disabled=not can_review)
    with cb2:
        if st.button("🗑️ مسح", use_container_width=True, key="r_clear"):
            for k in ("req_texts", "prop_texts", "review_report", "review_chat", "feedback_report"):
                st.session_state[k] = {} if "texts" in k else ([] if "chat" in k else "")
            st.rerun()

    if run_review and can_review and _require_api():
        client = get_client()
        req_ctx = build_context_bundle(
            st.session_state.req_texts,
            "متطلبات",
            max_total_tokens=MAX_REVIEW_CONTEXT_TOKENS // 2,
            per_file_tokens=10_000,
        )
        prop_ctx = build_context_bundle(
            st.session_state.prop_texts,
            "عرض",
            max_total_tokens=MAX_REVIEW_CONTEXT_TOKENS // 2,
            per_file_tokens=10_000,
        )
        progress = st.progress(25, text="إرسال للـ AI…")
        with st.spinner("🧠 جاري المقارنة… (1-3 دقائق)"):
            review = call_ai(client, PROPOSAL_REVIEW_PROMPT,
                              f"المتطلبات:\n{req_ctx}\n\nالعرض:\n{prop_ctx}\n\nأصدر تقرير الامتثال.")
            st.session_state.review_report = review
        progress.progress(100); time.sleep(0.4); progress.empty()
        if review.startswith("[AI Error"):
            st.error(review)
        else:
            st.success("✅ اكتملت المراجعة!")

    if st.session_state.review_report:
        st.markdown("---")
        score_match = re.search(r'نسبة الامتثال[^\d]*(\d+)%', st.session_state.review_report)
        score_val = int(score_match.group(1)) if score_match else None
        risk_match = re.search(r'مستوى المخاطرة[^:]*:[^\n]*(عالٍ|متوسط|منخفض)', st.session_state.review_report)
        risk_val = risk_match.group(1) if risk_match else "—"

        kc = st.columns(3)
        if score_val is not None:
            ring_cls = "score-high" if score_val >= 75 else ("score-mid" if score_val >= 50 else "score-low")
            kc[0].markdown(f'<div style="text-align:center"><div class="score-ring {ring_cls}">'
                           f'<div class="score-num">{score_val}%</div>'
                           f'<div class="score-label">الامتثال</div></div></div>',
                           unsafe_allow_html=True)
        risk_color = {"عالٍ": "#E53E3E", "متوسط": "#D69E2E", "منخفض": "#38A169"}.get(risk_val, "#718096")
        kc[1].markdown(f'<div style="text-align:center;padding-top:8px;">'
                       f'<div style="font-size:2rem;font-weight:800;color:{risk_color}">{safe_html(risk_val)}</div>'
                       f'<div style="font-size:0.78rem;color:#718096">المخاطرة</div></div>',
                       unsafe_allow_html=True)
        kc[2].markdown(f'<div style="text-align:center;padding-top:8px;">'
                       f'<div style="font-size:2rem;font-weight:800;color:#003087">{n_req+n_prop}</div>'
                       f'<div style="font-size:0.78rem;color:#718096">الملفات</div></div>',
                       unsafe_allow_html=True)
        st.markdown("---")

        tab_rev, tab_fb, tab_ch, tab_rw = st.tabs(["📊 الامتثال", "📋 الملاحظات الرسمية",
                                                     "💬 استفسر", "📄 النصوص"])

        with tab_rev:
            d1, d2 = st.columns(2)
            ts = datetime.now().strftime('%Y%m%d_%H%M')
            with d1:
                st.download_button("⬇️ TXT", st.session_state.review_report.encode("utf-8"),
                                    f"Compliance_{ts}.txt", "text/plain", use_container_width=True)
            with d2:
                jo = json.dumps({"compliance_score": score_val, "risk_level": risk_val,
                                  "report": st.session_state.review_report}, ensure_ascii=False, indent=2)
                st.download_button("⬇️ JSON", jo.encode("utf-8"),
                                    f"Compliance_{ts}.json", "application/json", use_container_width=True)
            st.markdown("---")

            sections = re.split(r'\n(?=# )', st.session_state.review_report)
            for sec in sections:
                if not sec.strip(): continue
                lines = sec.strip().split("\n")
                heading = lines[0].replace("#", "").strip()
                body = "\n".join(lines[1:]).strip()
                has_gap = "النواقص" in heading or "Gap" in heading
                has_str = "القوة" in heading or "Strength" in heading
                card_cls = "card card-red" if has_gap else ("card card-green" if has_str else "card")
                body_html = (safe_html(body).replace("\n", "<br>")
                             .replace("✅", '<span style="color:#38A169;font-weight:700">✅</span>')
                             .replace("⚠️", '<span style="color:#D69E2E;font-weight:700">⚠️</span>')
                             .replace("❌", '<span style="color:#E53E3E;font-weight:700">❌</span>'))
                st.markdown(f'<div class="{card_cls}"><h4>{safe_html(heading)}</h4>'
                            f'<p>{body_html}</p></div>', unsafe_allow_html=True)

        with tab_fb:
            st.markdown("""<div style="background:linear-gradient(135deg,#003087,#0052CC);
            border-radius:10px;padding:18px 24px;margin-bottom:20px;color:white;">
            <div style="font-size:1.05rem;font-weight:700;margin-bottom:4px;">📋 تقرير التغذية الراجعة الرسمي</div>
            <div style="font-size:0.82rem;color:#FFB81C;font-weight:600;">جاهز للإرسال للمقاول</div></div>
            """, unsafe_allow_html=True)

            f1, f2 = st.columns(2)
            with f1:
                fb_project = st.text_input("اسم المشروع", key="fb_proj")
                fb_ref = st.text_input("رقم المناقصة", key="fb_ref")
            with f2:
                fb_to = st.text_input("الجهة المُرسَل إليها", key="fb_to")
                fb_reviewer = st.text_input("اسم المراجع", key="fb_reviewer")

            gen_fb = st.button("🧠 توليد تقرير الملاحظات", use_container_width=True,
                                disabled=not can_review)

            if gen_fb and _require_api():
                client = get_client()
                req_ctx = build_context_bundle(
                    st.session_state.req_texts,
                    "متطلبات",
                    max_total_tokens=MAX_FEEDBACK_CONTEXT_TOKENS // 2,
                    per_file_tokens=8_000,
                )
                prop_ctx = build_context_bundle(
                    st.session_state.prop_texts,
                    "عرض",
                    max_total_tokens=MAX_FEEDBACK_CONTEXT_TOKENS // 2,
                    per_file_tokens=8_000,
                )
                with st.spinner("🧠 جاري التوليد…"):
                    fb_text = call_ai(client, FEEDBACK_REPORT_PROMPT,
                                       f"المتطلبات:\n{req_ctx}\n\nالعرض:\n{prop_ctx}")
                if fb_text.startswith("[AI Error"):
                    st.error(fb_text)
                else:
                    st.session_state.feedback_report = fb_text
                    st.success("✅ تم التوليد!")

            if st.session_state.feedback_report:
                fb_meta = {
                    "المشروع": fb_project or "—",
                    "رقم المناقصة": fb_ref or "—",
                    "الجهة المرسَل إليها": fb_to or "—",
                    "المراجع": fb_reviewer or "—",
                    "التاريخ": datetime.now().strftime("%Y-%m-%d"),
                    "الملفات": f"{n_req} متطلبات + {n_prop} عروض",
                }
                st.markdown("---")
                ts_fb = datetime.now().strftime("%Y%m%d_%H%M")
                e1, e2, e3 = st.columns(3)
                with e1:
                    try:
                        docx_b = generate_feedback_docx(st.session_state.feedback_report, fb_meta)
                        st.download_button("⬇️ Word", docx_b, f"Feedback_{ts_fb}.docx",
                            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True)
                    except Exception as e:
                        st.error(f"DOCX error: {e}")
                with e2:
                    try:
                        html_s = generate_feedback_html(st.session_state.feedback_report, fb_meta)
                        st.download_button("⬇️ HTML", html_s.encode("utf-8"),
                            f"Feedback_{ts_fb}.html", "text/html", use_container_width=True)
                    except Exception as e:
                        st.error(f"HTML error: {e}")
                with e3:
                    st.download_button("⬇️ TXT", st.session_state.feedback_report.encode("utf-8"),
                        f"Feedback_{ts_fb}.txt", "text/plain", use_container_width=True)

        with tab_ch:
            for msg in st.session_state.review_chat:
                if msg["role"] == "user":
                    st.markdown(f'<p class="chat-lbl" style="text-align:right">أنت</p>'
                                f'<div class="chat-user">{safe_html(msg["content"])}</div>',
                                unsafe_allow_html=True)
                else:
                    st.markdown(f'<p class="chat-lbl">TenderLens</p>'
                                f'<div class="chat-bot">{safe_html(msg["content"])}</div>',
                                unsafe_allow_html=True)
            with st.form("rev_chat", clear_on_submit=True):
                qr = st.text_input("سؤالك", label_visibility="collapsed")
                if st.form_submit_button("إرسال →", use_container_width=True) and qr.strip() and _require_api():
                    client = get_client()
                    ctx = "تقرير المراجعة:\n" + truncate_to_token_budget(st.session_state.review_report, 8_000)
                    with st.spinner("…"):
                        ans = call_ai(client, CHAT_SYSTEM + f"\n\n{ctx}", qr)
                    st.session_state.review_chat.append({"role": "user", "content": qr})
                    st.session_state.review_chat.append({"role": "bot", "content": ans})
                    st.rerun()

        with tab_rw:
            if st.session_state.req_texts:
                st.markdown("**متطلبات:**")
                for fname, text in st.session_state.req_texts.items():
                    with st.expander(f"📋 {fname}"):
                        st.text_area("", safe_truncate(text, 15000), height=280,
                                      label_visibility="collapsed", disabled=True, key=f"rq_{fname}")
            if st.session_state.prop_texts:
                st.markdown("**عرض:**")
                for fname, text in st.session_state.prop_texts.items():
                    with st.expander(f"📝 {fname}"):
                        st.text_area("", safe_truncate(text, 15000), height=280,
                                      label_visibility="collapsed", disabled=True, key=f"pr_{fname}")


# ═════════════════════════════════════════════════════════════════════════════
# MODULE 3 — BOQ EXTRACTOR
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.module == "boq":
    for f in (boq_files or []):
        if f.name not in st.session_state.boq_texts:
            valid, msg = validate_uploaded_file(f)
            if not valid: continue
            raw_bytes = f.read()
            with st.spinner(f"قراءة: {f.name}…"):
                st.session_state.boq_texts[f.name] = extract_text(raw_bytes, f.name)
                st.session_state.boq_tables_raw[f.name] = raw_bytes

    n_boq = len(st.session_state.boq_texts)

    if n_boq == 0 and st.session_state.boq_df is None:
        st.markdown("""<div style="text-align:center;padding:60px 0;color:#A0AEC0;">
        <div style="font-size:4rem;">📐</div>
        <h3 style="color:#003087;margin-top:16px;">ارفع ملفات BOQ</h3></div>""",
        unsafe_allow_html=True)
    else:
        kc = st.columns(4)
        kc[0].metric("الملفات", n_boq)
        kc[1].metric("الكلمات", f"{sum(word_count(v) for v in st.session_state.boq_texts.values()):,}")
        kc[2].metric("الطريقة", "⚡ تلقائي" if st.session_state.boq_source == "auto" else "🧠 AI")
        kc[3].metric("بنود", len(st.session_state.boq_df) if st.session_state.boq_df is not None else "—")

        for fname in st.session_state.boq_texts:
            st.markdown(f'<div class="file-item">📐 {safe_html(fname)}</div>', unsafe_allow_html=True)

        cb1, cb2 = st.columns([3, 1])
        with cb1:
            run_boq = st.button(f"📐 استخراج من {n_boq} ملف", use_container_width=True)
        with cb2:
            if st.button("🗑️ مسح", use_container_width=True, key="b_clear"):
                st.session_state.boq_texts = {}
                st.session_state.boq_tables_raw = {}
                st.session_state.boq_df = None
                st.rerun()

        if run_boq:
            need_api = st.session_state.boq_source == "ai"
            if need_api and not _require_api():
                pass
            else:
                all_rows = []
                progress = st.progress(0, text="جاري…")
                for i, (fname, raw_b) in enumerate(st.session_state.boq_tables_raw.items()):
                    progress.progress(int(i / max(n_boq, 1) * 80), text=f"{fname}…")
                    if st.session_state.boq_source == "auto":
                        rows = extract_boq_tables_auto(raw_b)
                        if len(rows) < 3 and st.session_state.get("user_api_key"):
                            client = get_client()
                            if client:
                                rows = extract_boq_ai(client, st.session_state.boq_texts[fname])
                    else:
                        client = get_client()
                        rows = extract_boq_ai(client, st.session_state.boq_texts[fname]) if client else []
                    for r in rows:
                        r["source_file"] = fname
                    all_rows.extend(rows)

                progress.progress(95, text="بناء الجدول…")
                df = build_boq_dataframe(all_rows)
                if "source_file" in df.columns:
                    df = df.rename(columns={"source_file": "Source File"})
                st.session_state.boq_df = df
                # Raw PDF bytes are only needed during extraction; release them to reduce Streamlit Cloud RAM usage.
                st.session_state.boq_tables_raw = {}
                progress.progress(100); time.sleep(0.3); progress.empty()
                st.success(f"✅ تم استخراج {len(df):,} بند!")

        if st.session_state.boq_df is not None and len(st.session_state.boq_df) > 0:
            df = st.session_state.boq_df
            st.markdown("---")
            ts = datetime.now().strftime('%Y%m%d_%H%M')
            stem = Path(list(st.session_state.boq_texts.keys())[0]).stem if st.session_state.boq_texts else "BOQ"

            d1, d2, d3 = st.columns(3)
            with d1:
                st.download_button("⬇️ Excel", df_to_excel_bytes(df, stem),
                    f"BOQ_{stem}_{ts}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)
            with d2:
                st.download_button("⬇️ CSV", df_to_csv_bytes(df),
                    f"BOQ_{stem}_{ts}.csv", "text/csv", use_container_width=True)
            with d3:
                jb = json.dumps(df.to_dict("records"), ensure_ascii=False, indent=2).encode("utf-8")
                st.download_button("⬇️ JSON", jb, f"BOQ_{stem}_{ts}.json",
                                    "application/json", use_container_width=True)

            st.markdown("---")
            st.dataframe(df, use_container_width=True, height=500, hide_index=True)


# ═════════════════════════════════════════════════════════════════════════════
# MODULE 4 — CLAUSE TRACKER
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.module == "clauses":
    for f in (clause_files or []):
        if f.name not in st.session_state.clause_texts:
            valid, msg = validate_uploaded_file(f)
            if not valid: continue
            with st.spinner(f"قراءة: {f.name}…"):
                st.session_state.clause_texts[f.name] = extract_text(f.read(), f.name)

    n = len(st.session_state.clause_texts)

    if n == 0 and st.session_state.clause_df is None:
        st.markdown("""<div style="text-align:center;padding:60px 0;color:#A0AEC0;">
        <div style="font-size:4rem;">📌</div><h3 style="color:#003087;">ارفع وثائق العقد</h3></div>""",
        unsafe_allow_html=True)
    else:
        kc = st.columns(4)
        kc[0].metric("الملفات", n)
        kc[1].metric("الكلمات", f"{sum(word_count(v) for v in st.session_state.clause_texts.values()):,}")
        df_cl = st.session_state.clause_df
        n_h = len(df_cl[df_cl["Risk Level"] == "HIGH"]) if df_cl is not None else 0
        kc[2].metric("🔴 عالية", n_h)
        kc[3].metric("الإجمالي", len(df_cl) if df_cl is not None else "—")

        cb1, cb2 = st.columns([3, 1])
        with cb1:
            run_cl = st.button(f"📌 تحليل {n} ملف", use_container_width=True)
        with cb2:
            if st.button("🗑️", use_container_width=True, key="c_clear"):
                st.session_state.clause_texts = {}
                st.session_state.clause_df = None
                st.rerun()

        if run_cl and _require_api():
            client = get_client()
            all_items = []
            progress = st.progress(0, text="…")
            for i, (fname, text) in enumerate(st.session_state.clause_texts.items()):
                progress.progress(int(i / n * 90), text=f"{fname}…")
                with st.spinner(f"🧠 {fname}…"):
                    items = ai_extract_clauses(client, text)
                for it in items:
                    it["source_file"] = fname
                all_items.extend(items)
            progress.progress(98)
            st.session_state.clause_df = build_clause_df(all_items)
            progress.progress(100); time.sleep(0.3); progress.empty()
            st.success(f"✅ {len(st.session_state.clause_df)} بند مستخرج")

        if st.session_state.clause_df is not None and len(st.session_state.clause_df) > 0:
            df_cl = st.session_state.clause_df
            st.markdown("---")
            ts = datetime.now().strftime('%Y%m%d_%H%M')
            stem = Path(list(st.session_state.clause_texts.keys())[0]).stem \
                if st.session_state.clause_texts else "Contract"

            e1, e2, e3 = st.columns(3)
            with e1:
                st.download_button("⬇️ Excel", df_to_clause_excel_bytes(df_cl, stem),
                    f"Clauses_{stem}_{ts}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)
            with e2:
                st.download_button("⬇️ CSV", df_cl.to_csv(index=False).encode("utf-8-sig"),
                    f"Clauses_{stem}_{ts}.csv", "text/csv", use_container_width=True)
            with e3:
                jc = json.dumps(df_cl.to_dict("records"), ensure_ascii=False, indent=2).encode("utf-8")
                st.download_button("⬇️ JSON", jc, f"Clauses_{stem}_{ts}.json",
                                    "application/json", use_container_width=True)
            st.markdown("---")
            st.dataframe(df_cl, use_container_width=True, height=520, hide_index=True)


# ═════════════════════════════════════════════════════════════════════════════
# MODULE 5 — MILESTONE TRACKER
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.module == "milestones":
    for f in (milestone_files or []):
        if f.name not in st.session_state.milestone_texts:
            valid, msg = validate_uploaded_file(f)
            if not valid: continue
            with st.spinner(f"قراءة: {f.name}…"):
                st.session_state.milestone_texts[f.name] = extract_text(f.read(), f.name)

    n = len(st.session_state.milestone_texts)

    if n == 0 and st.session_state.milestone_df is None:
        st.markdown("""<div style="text-align:center;padding:60px 0;color:#A0AEC0;">
        <div style="font-size:4rem;">📅</div><h3 style="color:#003087;">ارفع وثائق المناقصة</h3></div>""",
        unsafe_allow_html=True)
    else:
        df_ms = st.session_state.milestone_df
        kc = st.columns(4)
        kc[0].metric("الملفات", n)
        kc[1].metric("الكلمات", f"{sum(word_count(v) for v in st.session_state.milestone_texts.values()):,}")
        n_dated = len(df_ms[df_ms["Date (ISO)"].astype(str).str.len() >= 10]) if df_ms is not None else 0
        kc[2].metric("بتاريخ", n_dated if df_ms is not None else "—")
        n_urg = 0
        if df_ms is not None:
            try:
                n_urg = int((df_ms["Days Remaining"].dropna().astype(float) <= 14).sum())
            except: pass
        kc[3].metric("عاجلة ⚠️", n_urg if df_ms is not None else "—")

        cb1, cb2 = st.columns([3, 1])
        with cb1:
            run_ms = st.button(f"📅 استخراج من {n} ملف", use_container_width=True)
        with cb2:
            if st.button("🗑️", use_container_width=True, key="m_clear"):
                st.session_state.milestone_texts = {}
                st.session_state.milestone_df = None
                st.rerun()

        if run_ms and _require_api():
            client = get_client()
            all_items = []
            prog = st.progress(0, text="…")
            for i, (fname, text) in enumerate(st.session_state.milestone_texts.items()):
                prog.progress(int(i / n * 85), text=f"{fname}…")
                items = ai_extract_milestones(client, text)
                for it in items:
                    it["source_file"] = fname
                all_items.extend(items)
            prog.progress(95)
            st.session_state.milestone_df = build_milestone_df(all_items)
            prog.progress(100); time.sleep(0.3); prog.empty()
            st.success(f"✅ {len(st.session_state.milestone_df)} موعد")

        if st.session_state.milestone_df is not None and len(st.session_state.milestone_df) > 0:
            df_ms = st.session_state.milestone_df
            st.markdown("---")
            ts = datetime.now().strftime("%Y%m%d_%H%M")
            stem = Path(list(st.session_state.milestone_texts.keys())[0]).stem \
                if st.session_state.milestone_texts else "Project"

            e1, e2, e3 = st.columns(3)
            with e1:
                st.download_button("⬇️ Excel", df_to_milestone_excel(df_ms, stem),
                    f"Milestones_{stem}_{ts}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)
            with e2:
                st.download_button("⬇️ Calendar (.ics)", generate_milestone_ics(df_ms, stem),
                    f"Calendar_{stem}_{ts}.ics", "text/calendar", use_container_width=True)
            with e3:
                st.download_button("⬇️ CSV", df_ms.to_csv(index=False).encode("utf-8-sig"),
                    f"Milestones_{stem}_{ts}.csv", "text/csv", use_container_width=True)
            st.markdown("---")
            st.dataframe(df_ms, use_container_width=True, height=480, hide_index=True)


# ═════════════════════════════════════════════════════════════════════════════
# MODULE 6 — GO / NO-GO DASHBOARD (FIXED — no orphan elif)
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.module == "gonogo":
    dd = compute_dashboard_data()
    n_ready = sum([dd["has_tender"], dd["has_review"], dd["has_boq"],
                    dd["has_clauses"], dd["has_milestones"]])
    today_str = datetime.now().strftime("%d %b %Y")
    ts_gg = datetime.now().strftime("%Y%m%d_%H%M")

    banner_color = "#10B981" if n_ready >= 4 else ("#D97706" if n_ready >= 2 else "#DC2626")
    banner_text = "جاهز" if n_ready >= 4 else ("جزئي" if n_ready >= 2 else "غير كافٍ")
    st.markdown(
        f'<div style="background:{banner_color}18;border:1.5px solid {banner_color}44;'
        f'border-radius:10px;padding:12px 20px;margin-bottom:16px;'
        f'display:flex;justify-content:space-between;">'
        f'<span style="font-weight:700;color:{banner_color}">'
        f'{"✅" if n_ready>=4 else "⚠️" if n_ready>=2 else "❌"} {banner_text}</span>'
        f'<span style="color:#64748B">{n_ready} / 5 وحدات</span></div>',
        unsafe_allow_html=True,
    )

    rs = dd["readiness_score"]
    gauge_color = "#16A34A" if rs >= 70 else ("#D97706" if rs >= 45 else "#DC2626")
    gauge_label = "ممتاز" if rs >= 85 else ("جيد" if rs >= 70 else
                  ("متوسط" if rs >= 50 else ("ضعيف" if rs >= 30 else "غير مقبول")))

    angle = (rs / 100.0) * 180
    rad = math.pi * angle / 180
    cx, cy, r_out = 100, 100, 80
    end_x = cx + r_out * math.cos(math.pi - rad)
    end_y = cy - r_out * math.sin(rad)
    large_arc = 1 if angle > 90 else 0
    bg_path = f"M {cx-r_out},{cy} A {r_out},{r_out} 0 0 1 {cx+r_out},{cy}"
    val_path = f"M {cx-r_out},{cy} A {r_out},{r_out} 0 {large_arc} 1 {end_x:.2f},{end_y:.2f}"

    g_col, l_col = st.columns([2, 1])
    with g_col:
        st.markdown("#### 🎯 مؤشر الجاهزية")
        st.markdown(f"""<div style="text-align:center;">
        <svg viewBox="0 0 200 115" width="280" style="display:block;margin:0 auto;">
        <path d="{bg_path}" fill="none" stroke="#E2E8F0" stroke-width="18" stroke-linecap="round"/>
        <path d="{val_path}" fill="none" stroke="{gauge_color}" stroke-width="18" stroke-linecap="round"/>
        <text x="100" y="88" text-anchor="middle" font-size="30" font-weight="bold"
              fill="{gauge_color}">{rs}</text>
        <text x="100" y="104" text-anchor="middle" font-size="11" fill="#64748B">/ 100</text>
        </svg>
        <div style="font-size:1rem;font-weight:700;color:{gauge_color}">{gauge_label}</div>
        </div>""", unsafe_allow_html=True)

    with l_col:
        st.markdown("#### 🚦 المؤشر")
        light_go = rs >= 70; light_caut = 45 <= rs < 70; light_nogo = rs < 45

        def _light(on, color_on, color_off, label):
            c = color_on if on else color_off
            glow = f"box-shadow:0 0 18px 6px {color_on}88;" if on else ""
            return (f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:18px;">'
                    f'<div style="width:42px;height:42px;border-radius:50%;background:{c};{glow}'
                    f'border:3px solid {"white" if on else "#E2E8F0"};flex-shrink:0;"></div>'
                    f'<div style="font-size:0.85rem;font-weight:{"700" if on else "400"};'
                    f'color:{"#0F172A" if on else "#94A3B8"}">{label}</div></div>')

        st.markdown(
            f'<div style="background:#0F172A;border-radius:14px;padding:20px;border:3px solid #1E293B;">'
            + _light(light_nogo, "#DC2626", "#2D0A0A", "NO-GO — لا تُقدّم")
            + _light(light_caut, "#D97706", "#2D1A00", "تحفّظ — CAUTION")
            + _light(light_go, "#16A34A", "#042A12", "GO — أقدِم")
            + '</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🧠 محرك التوصية")
    g1, g2 = st.columns([3, 1])
    with g1:
        project_name_gg = st.text_input("اسم المشروع", value="Tender Project", key="gg_proj")
    with g2:
        run_gg = st.button("🚦 توليد القرار", use_container_width=True, type="primary")

    if run_gg:
        if not _require_api():
            pass
        elif n_ready < 1:
            st.warning("شغّل وحدة واحدة على الأقل أولاً.")
        else:
            client = get_client()
            payload = json.dumps({
                "compliance_score": dd["compliance_score"],
                "n_high_risk_clauses": dd["n_high_clauses"],
                "n_total_clauses": dd["n_total_clauses"],
                "boq_items_count": dd["boq_items"],
                "boq_complete": dd["has_boq"] and dd["boq_items"] > 5,
                "n_urgent_milestones": dd["n_urgent_milestones"],
                "n_past_milestones": dd["n_past_milestones"],
                "n_total_milestones": dd["n_total_milestones"],
                "days_to_next_deadline": dd["days_to_next"],
                "submission_deadline_past": dd["n_past_milestones"] > 0,
                "readiness_score": dd["readiness_score"],
                "modules_with_data": n_ready,
            }, ensure_ascii=False, indent=2)
            with st.spinner("🧠 يجري التحليل…"):
                vd = call_ai_json(client, GONOGO_PROMPT, payload)
            if vd:
                st.session_state.gonogo_verdict = vd
                st.success("✅ تم التوليد")
            else:
                st.error("لم يتم استلام JSON صالح من النموذج.")

    vd = st.session_state.get("gonogo_verdict")
    if vd:
        verdict = vd.get("verdict", "GO WITH CAUTION")
        v_score = int(vd.get("overall_score", dd["readiness_score"]))
        conf = vd.get("confidence", "MEDIUM")

        if verdict == "GO":
            vbg, vborder, vicon = "#F0FDF4", "#16A34A", "✅"
        elif verdict == "NO-GO":
            vbg, vborder, vicon = "#FEF2F2", "#DC2626", "🚫"
        else:
            vbg, vborder, vicon = "#FFFBEB", "#D97706", "⚠️"

        st.markdown("---")
        st.markdown(
            f'<div style="background:{vbg};border:3px solid {vborder};border-radius:14px;'
            f'padding:24px;text-align:center">'
            f'<div style="font-size:3rem">{vicon}</div>'
            f'<div style="font-size:2.2rem;font-weight:900;color:{vborder}">{safe_html(verdict)}</div>'
            f'<div style="margin-top:12px"><span style="background:white;border-radius:8px;'
            f'padding:6px 16px;font-weight:700">🎯 {v_score}/100 · Confidence: {safe_html(conf)}</span>'
            f'</div></div>', unsafe_allow_html=True)

        if vd.get("executive_summary"):
            st.markdown(f'<div style="background:#EFF6FF;border-left:4px solid #003087;'
                        f'padding:14px 18px;margin:16px 0">'
                        f'<b>الملخص:</b><br>{safe_html(vd["executive_summary"])}</div>',
                        unsafe_allow_html=True)

        rc, oc, ac = st.columns(3)
        with rc:
            st.markdown("##### ⚠️ المخاطر")
            for r in vd.get("key_risks", []):
                st.markdown(f'<div style="background:#FEF2F2;border-left:3px solid #DC2626;'
                            f'padding:8px 12px;margin-bottom:6px">{safe_html(r)}</div>',
                            unsafe_allow_html=True)
        with oc:
            st.markdown("##### 💡 الفرص")
            for o in vd.get("key_opportunities", []):
                st.markdown(f'<div style="background:#F0FDF4;border-left:3px solid #16A34A;'
                            f'padding:8px 12px;margin-bottom:6px">{safe_html(o)}</div>',
                            unsafe_allow_html=True)
        with ac:
            st.markdown("##### 📋 الإجراءات")
            for i, a in enumerate(vd.get("recommended_actions", []), 1):
                st.markdown(f'<div style="background:#EFF6FF;border-left:3px solid #003087;'
                            f'padding:8px 12px;margin-bottom:6px"><b>{i}.</b> {safe_html(a)}</div>',
                            unsafe_allow_html=True)

        st.markdown("---")
        e1, e2 = st.columns(2)
        with e1:
            try:
                pdf_b = generate_gonogo_pdf(vd, dd, project_name_gg)
                st.download_button("📄 PDF تقرير", pdf_b, f"GoNoGo_{ts_gg}.pdf",
                                    "application/pdf", use_container_width=True, type="primary")
            except Exception as e:
                st.error(f"PDF: {e}")
        with e2:
            rj = json.dumps({"project": project_name_gg, "verdict": vd, "dashboard": dd},
                             ensure_ascii=False, indent=2)
            st.download_button("📊 JSON", rj.encode("utf-8"), f"GoNoGo_{ts_gg}.json",
                                "application/json", use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# MODULE 7 — MULTI-TENDER COMPARE
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.module == "compare":
    cmp_names = st.session_state.get("compare_selection", [])
    if len(cmp_names) < 2:
        st.markdown("""<div style="text-align:center;padding:40px;background:#F8FAFC;
        border-radius:12px;border:2px dashed #E2E8F0">
        <div style="font-size:3rem">🏁</div>
        <h4 style="color:#003087">اختر مناقصتين أو ثلاثاً</h4>
        <p style="color:#64748B">من القائمة في الشريط الجانبي</p></div>""",
        unsafe_allow_html=True)
    else:
        snapshots = [build_tender_snapshot(n) for n in cmp_names[:3]]
        decision = compare_tender_snapshots(snapshots)
        best = decision["best"]
        ts_cmp = datetime.now().strftime("%Y%m%d_%H%M")

        st.markdown("#### 🧭 مصفوفة المقارنة")
        cols = st.columns(len(snapshots))
        for col, snap in zip(cols, snapshots):
            with col:
                st.markdown(
                    f'<div style="background:#F8FAFC;border:1.5px solid #E2E8F0;border-radius:12px;'
                    f'padding:14px;text-align:center">'
                    f'<div style="font-weight:800;color:#003087">{safe_html(snap["name"])}</div>'
                    f'<div style="font-size:2rem;font-weight:900;color:#FFB81C;margin:8px 0">'
                    f'{snap["readiness_score"]}</div>'
                    f'<div style="font-size:0.78rem;color:#475569">Readiness / 100</div>'
                    f'<div style="margin-top:10px;font-size:0.8rem">Compliance: <b>{snap["compliance_score"]}%</b></div>'
                    f'<div style="font-size:0.8rem">Risk: <b>{snap["n_high_clauses"]} HIGH</b></div>'
                    f'<div style="font-size:0.8rem">Timing: <b>{safe_html(snap["timeline_pressure"])}</b></div>'
                    f'</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f"### 🏆 Best Bet: {safe_html(best.get('name', '—'))} · {safe_html(decision['verdict'])}")
        st.markdown(f'<div style="background:#EFF6FF;border-left:4px solid #003087;'
                    f'padding:14px 18px;margin-bottom:16px">{safe_html(decision["summary"])}</div>',
                    unsafe_allow_html=True)
        for i, b in enumerate(decision["bullets"], 1):
            st.markdown(f'<div style="background:#F8FAFC;border:1px solid #E2E8F0;'
                        f'border-radius:8px;padding:10px;margin-bottom:8px"><b>{i}.</b> {safe_html(b)}</div>',
                        unsafe_allow_html=True)

        st.markdown("#### 📋 الجدول")
        st.dataframe(pd.DataFrame(decision["matrix_rows"],
            columns=["Tender", "Readiness", "Compliance", "Clause Risk", "Milestones", "Timeline"]),
            use_container_width=True, hide_index=True)

        st.markdown("---")
        try:
            pdf_b = generate_comparison_pdf(snapshots, decision, "Multi-Tender Comparison")
            st.download_button("📄 PDF تقرير", pdf_b, f"Comparison_{ts_cmp}.pdf",
                                "application/pdf", use_container_width=True, type="primary")
        except Exception as e:
            st.error(f"PDF: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# MODULE 8 — DOCUMENT GENERATOR
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.module == "docgen":
    PLAN_DEFS = {
        "pm":      {"key": "pm", "short": "Project Management Plan", "icon": "📋", "color": "#003087",
                    "plan_type": "Project Management and Execution Plan"},
        "risk":    {"key": "risk", "short": "Risk Management Plan", "icon": "⚠️", "color": "#DC2626",
                    "plan_type": "Risk Management Plan"},
        "quality": {"key": "quality", "short": "Quality Management Plan", "icon": "✅", "color": "#16A34A",
                    "plan_type": "Quality Management Plan"},
        "safety":  {"key": "safety", "short": "Safety (HSE) Plan", "icon": "🦺", "color": "#D97706",
                    "plan_type": "HSE Management Plan"},
    }

    _ctx_parts = []
    if st.session_state.get("tender_report", "").strip():
        _ctx_parts.append("=== TENDER REPORT ===\n" + safe_truncate(st.session_state.tender_report, 8000))
    if st.session_state.get("tender_texts"):
        for fn, tx in list(st.session_state.tender_texts.items())[:3]:
            _ctx_parts.append(f"=== {fn} ===\n{safe_truncate(tx, 5000)}")
    _ctx = "\n\n".join(_ctx_parts) if _ctx_parts else "No tender context."

    _proj_name = (list(st.session_state.get("tender_texts", {}).keys())[0].replace(".pdf", "")
                  if st.session_state.get("tender_texts") else "Infrastructure Project")

    st.markdown(f"""<div style="background:linear-gradient(135deg,#003087,#001a54);
    border-radius:12px;padding:20px;margin-bottom:24px;border-bottom:3px solid #FFB81C">
    <h3 style="color:#FFB81C;margin:0 0 6px;">📝 Reference-Based Document Generator</h3>
    <p style="color:#93A5C8;margin:0;font-size:0.85rem">ارفع DOCX قالب · سيُعاد كتابة المحتوى بمشروعك</p>
    </div>""", unsafe_allow_html=True)

    if _ctx_parts:
        st.success(f"✅ {len(_ctx_parts)} مصدر سياق محمّل")
    else:
        st.warning("⚠️ لا توجد وثائق مناقصة. شغّل Module 1 أولاً.")

    _proj_name = st.text_input("اسم المشروع (للغلاف)", value=_proj_name, key="dg_proj")

    def _struct_to_outline(struct):
        return "\n".join(f"{s.get('number', '')} {s.get('title', '')}".strip() for s in struct)

    def _render_plan_tab(plan_def):
        key, color = plan_def["key"], plan_def["color"]
        st.markdown(f'<div style="background:{color}12;border-left:4px solid {color};'
                    f'padding:12px;margin-bottom:16px"><b style="color:{color}">'
                    f'{plan_def["icon"]} {plan_def["short"]}</b></div>',
                    unsafe_allow_html=True)

        st.markdown("#### Step 1 — رفع DOCX قالب مرجعي")
        ref_file = st.file_uploader(f"DOCX template", type=["docx"], key=f"dg_ref_{key}",
                                     label_visibility="collapsed")

        if ref_file:
            if st.session_state.docgen_ref_names[key] != ref_file.name:
                with st.spinner(f"قراءة {ref_file.name}…"):
                    fb = ref_file.read()
                st.session_state.docgen_ref_texts[key] = extract_text(fb, ref_file.name)
                st.session_state.docgen_ref_names[key] = ref_file.name
                st.session_state.docgen_ref_bytes[key] = fb
                st.session_state.docgen_structures[key] = None
                st.session_state.docgen_outputs[key] = ""

        ref_text = st.session_state.docgen_ref_texts.get(key)
        if ref_text:
            st.markdown(f'<div style="background:#F0FDF4;border:1px solid #86EFAC;'
                        f'border-radius:8px;padding:10px;margin-bottom:12px">'
                        f'📄 <b>{safe_html(st.session_state.docgen_ref_names[key])}</b> · '
                        f'{word_count(ref_text):,} كلمة</div>',
                        unsafe_allow_html=True)

            st.markdown("#### Step 2 — تحليل البنية")
            ca, cc = st.columns([3, 1])
            with ca:
                do_a = st.button("🔍 تحليل", key=f"dg_a_{key}", use_container_width=True)
            with cc:
                if st.button("🗑️", key=f"dg_c_{key}", use_container_width=True):
                    st.session_state.docgen_ref_texts[key] = None
                    st.session_state.docgen_ref_names[key] = ""
                    st.session_state.docgen_ref_bytes.pop(key, None)
                    st.session_state.docgen_structures[key] = None
                    st.session_state.docgen_outputs[key] = ""
                    st.rerun()

            if do_a and _require_api():
                client = get_client()
                with st.spinner("🧠 تحليل البنية…"):
                    raw = call_ai_json(client, STRUCTURE_EXTRACTION_PROMPT,
                                        f"Document text:\n\n{truncate_to_token_budget(ref_text, MAX_DOCGEN_CONTEXT_TOKENS)}")
                if isinstance(raw, list) and raw:
                    st.session_state.docgen_structures[key] = raw
                    st.success(f"✅ {len(raw)} قسم")
                    st.rerun()
                else:
                    st.error("تعذّر استخراج البنية.")

            struct = st.session_state.docgen_structures.get(key)
            if struct:
                with st.expander(f"📑 البنية ({len(struct)} قسم)"):
                    st.code("\n".join(f"{'  '*(s.get('level',1)-1)}{s.get('number','')} {s.get('title','')}"
                                       for s in struct))

                st.markdown("---")
                st.markdown("#### Step 3 — توليد المحتوى")
                has_template_bytes = bool(st.session_state.docgen_ref_bytes.get(key))
                if not has_template_bytes:
                    st.warning("⚠️ تم حذف قالب Word من الذاكرة. أعد رفع القالب قبل توليد المحتوى أو التصدير.")
                if st.button(f"🚀 توليد {plan_def['short']}", key=f"dg_g_{key}",
                              use_container_width=True, type="primary", disabled=not has_template_bytes):
                    if _require_api():
                        client = get_client()
                        outline = _struct_to_outline(struct)
                        user_msg = DOCGEN_CONTENT_PROMPT.format(
                            plan_type=plan_def["plan_type"],
                            project_context=_ctx,
                            structure_outline=outline,
                        )
                        with st.spinner("🧠 جارٍ الكتابة… (1-2 دقيقة)"):
                            gen = call_ai(client, "You are a senior plan writer.", user_msg)
                        if gen.startswith("[AI Error"):
                            st.error(gen)
                        else:
                            st.session_state.docgen_outputs[key] = gen
                            st.success("✅ تم!")
                            st.rerun()

                output = st.session_state.docgen_outputs.get(key, "")
                if output:
                    st.markdown("---")
                    st.markdown("#### Step 4 — التصدير")
                    ts_d = datetime.now().strftime("%Y%m%d_%H%M")
                    e1, e2 = st.columns(2)
                    with e1:
                        try:
                            template_bytes = st.session_state.docgen_ref_bytes.get(key)
                            if not template_bytes:
                                st.warning("⚠️ لا يمكن تصدير Word لأن قالب DOCX غير موجود في الذاكرة. أعد رفع القالب أولاً.")
                            else:
                                db = generate_plan_docx(plan_def["short"], output, _proj_name, struct, template_bytes)
                                st.download_button(f"📄 Word", db, f"TLP_{key}_{ts_d}.docx",
                                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    use_container_width=True, type="primary", key=f"dg_dl_{key}")
                        except Exception as e:
                            st.error(f"DOCX: {e}")
                    with e2:
                        st.download_button(f"📝 TXT", output.encode("utf-8"),
                            f"TLP_{key}_{ts_d}.txt", "text/plain",
                            use_container_width=True, key=f"dg_dlt_{key}")

                    with st.expander("📄 معاينة"):
                        st.markdown(safe_html(output).replace("\n", "<br>"), unsafe_allow_html=True)
        else:
            st.markdown(f"""<div style="text-align:center;padding:36px;background:#F8FAFC;
            border-radius:12px;border:2px dashed #E2E8F0">
            <div style="font-size:2.5rem">{plan_def['icon']}</div>
            <h4 style="color:#003087">ارفع قالب {plan_def['short']}</h4></div>""",
            unsafe_allow_html=True)

    tabs = st.tabs(["📋 PM", "⚠️ Risk", "✅ Quality", "🦺 Safety"])
    for tab, key in zip(tabs, ["pm", "risk", "quality", "safety"]):
        with tab:
            _render_plan_tab(PLAN_DEFS[key])

    # ── Technical tools ──
    st.markdown("---")
    st.markdown("""<div style="background:linear-gradient(135deg,#003087,#001a54);
    border-radius:12px;padding:18px;margin:14px 0">
    <h3 style="color:#FFB81C;margin:0;font-size:1.1rem">🛠️ Technical Intelligence Tools</h3></div>""",
    unsafe_allow_html=True)

    ttabs = st.tabs(["🎨 Visual", "🏗️ SBC", "🧭 Stakeholders"])

    with ttabs[0]:
        vp_mode = st.radio("Mode", ["Methodology", "Org Chart"], horizontal=True, key="vp_mode")
        vp_src = st.text_area("Source", value=safe_truncate(st.session_state.get("tender_report", ""), 5000),
                                height=220, key="vp_src")
        if st.button("🎨 Generate", key="vp_gen", use_container_width=True):
            st.session_state.tech_outputs["visual"] = json.dumps(
                build_visual_prompt(vp_src, vp_mode), ensure_ascii=False, indent=2)
        if st.session_state.tech_outputs["visual"]:
            st.text_area("Result", st.session_state.tech_outputs["visual"], height=240, key="vp_res")
            st.download_button("⬇️ Download", st.session_state.tech_outputs["visual"].encode("utf-8"),
                                "Visual_Prompt.json", "application/json", use_container_width=True)

    with ttabs[1]:
        sbc_r = st.text_area("RFP", value=safe_truncate(build_docgen_context(), 5000),
                              height=180, key="sbc_r")
        sbc_p = st.text_area("Proposal", value=safe_truncate(st.session_state.get("review_report", ""), 5000),
                              height=180, key="sbc_p")
        if st.button("🔎 Scan", key="sbc_g", use_container_width=True) and _require_api():
            with st.spinner("…"):
                out = generate_json_via_ai(SBC_SCANNER_PROMPT,
                                            f"RFP:\n{sbc_r}\n\nPROPOSAL:\n{sbc_p}")
            if not out:
                out = {"summary": "No response.", "findings": []}
            st.session_state.tech_outputs["sbc"] = json.dumps(out, ensure_ascii=False, indent=2)
        if st.session_state.tech_outputs["sbc"]:
            st.text_area("Result", st.session_state.tech_outputs["sbc"], height=260, key="sbc_res")
            st.download_button("⬇️ Download", st.session_state.tech_outputs["sbc"].encode("utf-8"),
                                "SBC_Scan.json", "application/json", use_container_width=True)

    with ttabs[2]:
        sm_t = st.text_area("Tender", value=safe_truncate(build_docgen_context(), 7000),
                              height=260, key="sm_t")
        if st.button("🧭 Extract", key="sm_g", use_container_width=True) and _require_api():
            with st.spinner("…"):
                out = generate_json_via_ai(STAKEHOLDER_MAPPER_PROMPT, sm_t)
            if not out:
                out = {"summary": "No response.", "stakeholders": []}
            st.session_state.tech_outputs["stakeholders"] = json.dumps(out, ensure_ascii=False, indent=2)
        if st.session_state.tech_outputs["stakeholders"]:
            st.text_area("Result", st.session_state.tech_outputs["stakeholders"], height=260, key="sm_res")
            st.download_button("⬇️ Download", st.session_state.tech_outputs["stakeholders"].encode("utf-8"),
                                "Stakeholders.json", "application/json", use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# END OF APP
# ═════════════════════════════════════════════════════════════════════════════
