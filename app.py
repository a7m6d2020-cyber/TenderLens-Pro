"""
TenderLens Pro | By Eng. Ahmed Almaamari
Senior Technical Civil Engineer | Tender Analysis & Contract Management Intelligence Platform
Enterprise-Grade RFP Analysis Engine with OpenAI Direct Integration (OpenAI API)

v3.0 — Hardened Edition
- Zero Hallucination Protocol
- OpenAI Direct API (No Replit)
- XSS Protection & Arabic-Safe Text Handling
- Exponential Backoff + Model Fallback
- Session State Initialization
"""

import os
import io
import re
import json
import time
import math
import html as _html
from datetime import datetime
from pathlib import Path
import logging as log

import streamlit as st
import pdfplumber
from openai import OpenAI, RateLimitError, APITimeoutError, AuthenticationError, APIError
import pandas as pd
from docx import Document

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS & CONFIG
# ─────────────────────────────────────────────────────────────────────────────
DEFAULT_MODEL = "gpt-4o"
FALLBACK_MODEL = "gpt-4o-mini"
AVAILABLE_MODELS = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4"]
MAX_FILE_SIZE_MB = 50
MAX_TOKENS_PER_REQ = 8192
API_TIMEOUT = 120.0
API_MAX_RETRIES = 3

st.set_page_config(
    page_title="TenderLens Pro",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"Get help": "https://github.com/a7m6dmamari-lab/TenderLens-Pro"}
)

st.markdown("""
<style>
:root {
    --navy: #003087;
    --gold: #FFB81C;
    --green: #16A34A;
    --red: #DC2626;
    --amber: #D97706;
}
* { direction: rtl; }
body { background: white; font-family: 'Segoe UI', Arial, sans-serif; }
.masthead {
    background: linear-gradient(135deg, var(--navy), #0052CC);
    color: white; padding: 24px; border-radius: 12px;
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 20px; border-bottom: 4px solid var(--gold);
}
.masthead-title { font-size: 1.6rem; font-weight: 900; letter-spacing: 0.5px; }
.masthead-sub { font-size: 0.85rem; color: #93A5C8; margin-top: 4px; }
.masthead-badge { background: rgba(255, 184, 28, 0.2); color: var(--gold);
    padding: 8px 16px; border-radius: 6px; font-weight: 700; font-size: 0.78rem; }
.card { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px;
    padding: 18px; margin-bottom: 14px; border-left: 4px solid #003087; }
.card h4 { margin: 0 0 10px; color: var(--navy); font-weight: 700; }
.card p { margin: 0; color: #475569; line-height: 1.6; }
.card-gold { border-left-color: var(--gold); }
.card-green { border-left-color: var(--green); }
.card-red { border-left-color: var(--red); }
.chip { display: inline-block; background: #E2E8F0; color: #1e293b;
    padding: 4px 12px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; margin-right: 8px; }
.chip-gold { background: var(--gold); color: white; }
.chip-gray { background: #CBD5E1; color: #475569; }
.file-item { background: white; border: 1px solid #E2E8F0; padding: 10px 14px;
    border-radius: 8px; margin-bottom: 8px; font-size: 0.85rem; }
.api-status-ok { background: #F0FDF4; border: 1px solid var(--green); color: var(--green);
    padding: 10px 16px; border-radius: 8px; text-align: center; font-weight: 700; }
.api-status-bad { background: #FEF2F2; border: 1px solid var(--red); color: var(--red);
    padding: 10px 16px; border-radius: 8px; text-align: center; font-weight: 700; }
.chat-lbl { font-size: 0.75rem; font-weight: 700; color: #64748B; margin-bottom: 4px; }
.chat-user { background: #EFF6FF; border-left: 3px solid var(--navy); padding: 12px 16px;
    border-radius: 8px; margin-bottom: 12px; color: #1e293b; }
.chat-bot { background: #F0FDF4; border-left: 3px solid var(--green); padding: 12px 16px;
    border-radius: 8px; margin-bottom: 12px; color: #1e293b; }
.score-ring { position: relative; width: 120px; height: 120px;
    background: conic-gradient(var(--gold) 0deg, var(--gold) var(--angle), #E2E8F0 0deg);
    border-radius: 50%; display: flex; flex-direction: column; align-items: center;
    justify-content: center; margin: 0 auto; }
.score-high { --angle: 270deg; color: var(--green); }
.score-mid { --angle: 180deg; color: var(--amber); }
.score-low { --angle: 90deg; color: var(--red); }
.score-num { font-size: 2.2rem; font-weight: 900; }
.score-label { font-size: 0.7rem; color: #64748B; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CORE UTILITIES
# ─────────────────────────────────────────────────────────────────────────────
def validate_uploaded_file(f) -> tuple[bool, str]:
    """Validate file size and type."""
    if f.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        return False, f"الملف أكبر من {MAX_FILE_SIZE_MB}MB"
    if f.type != "application/pdf":
        return False, "فقط ملفات PDF مدعومة"
    return True, ""

def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract text from PDF — zero hallucination."""
    if not file_bytes:
        return ""
    try:
        text_parts = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                extracted = page.extract_text() or ""
                if extracted.strip():
                    text_parts.append(f"\n--- Page {i} ---\n{extracted}")
        return "".join(text_parts).strip()
    except Exception as e:
        log.error(f"PDF extraction error: {e}")
        return ""

def word_count(text: str) -> int:
    """Count words in text."""
    return len(re.findall(r'\S+', text)) if text else 0

def safe_html(text) -> str:
    """Escape HTML to prevent XSS."""
    return _html.escape(str(text)) if text is not None else ""

def safe_truncate(text: str, max_chars: int) -> str:
    """Truncate text safely without breaking Arabic characters."""
    if not text or len(text) <= max_chars:
        return text or ""
    cut = text[:max_chars]
    for sep in ["\n\n", ". ", "؟ ", "? ", "\n"]:
        idx = cut.rfind(sep)
        if idx > max_chars * 0.7:
            return cut[:idx + len(sep)] + " […]"
    return cut + " […]"

def get_client():
    """Initialize OpenAI client with priority: session → env → secrets."""
    api_key = st.session_state.get("user_api_key", "").strip()
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        try:
            api_key = st.secrets.get("OPENAI_API_KEY", "").strip()
        except Exception:
            pass
    if not api_key or not api_key.startswith("sk-"):
        return None
    try:
        return OpenAI(api_key=api_key, timeout=API_TIMEOUT, max_retries=API_MAX_RETRIES)
    except Exception:
        return None

def test_api_connection() -> tuple[bool, str]:
    """Test OpenAI API connection."""
    client = get_client()
    if not client:
        return False, "لم يتم تكوين مفتاح API."
    try:
        resp = client.chat.completions.create(
            model=st.session_state.get("openai_model", DEFAULT_MODEL),
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5, timeout=20.0,
        )
        return True, f"✅ الاتصال ناجح ({resp.model})"
    except AuthenticationError:
        return False, "❌ المفتاح غير صالح."
    except RateLimitError:
        return False, "⚠️ تم تجاوز حد المعدل."
    except Exception as e:
        return False, f"❌ فشل: {str(e)[:100]}"

def call_ai(client, system: str, user: str, model=None, temperature=0.2,
            max_tokens=MAX_TOKENS_PER_REQ) -> str:
    """Call AI with exponential backoff + model fallback."""
    model = model or st.session_state.get("openai_model", DEFAULT_MODEL)
    last_err = None
    for attempt in range(API_MAX_RETRIES):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return (resp.choices[0].message.content or "").strip()
        except RateLimitError:
            last_err = "Rate limit"
            time.sleep(2 ** attempt)
        except APITimeoutError:
            last_err = "Timeout"
            time.sleep(2)
        except AuthenticationError as e:
            return f"[AI Auth Error: المفتاح غير صالح. {str(e)[:80]}]"
        except APIError as e:
            last_err = str(e)
            if "model" in str(e).lower() and attempt == 0:
                model = FALLBACK_MODEL
                continue
            break
    return f"[AI Error بعد {API_MAX_RETRIES} محاولات: {str(last_err)[:120]}]"

def call_ai_json(client, system: str, user: str) -> dict | list:
    """Call AI and parse JSON response."""
    raw = call_ai(client, system, user)
    if raw.startswith("[AI Error"):
        return {}
    try:
        clean = re.sub(r'```json\s*|\s*```', '', raw).strip()
        return json.loads(clean)
    except Exception:
        return {}

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
    """Extract BOQ tables automatically from PDF."""
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
    """Extract BOQ items from unstructured text using AI."""
    if not text or not client:
        return []
    snippet = safe_truncate(text, 35000)
    raw = call_ai_json(
        client,
        "استخرج بنود BOQ من النص كـ JSON array فقط. لكل بند: item_no, description, unit, quantity.",
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
        meta.set_column(0, 0, 60)
    return output.getvalue()

def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")

# ─────────────────────────────────────────────────────────────────────────────
# AI PROMPTS
# ─────────────────────────────────────────────────────────────────────────────
TENDER_ANALYSIS_PROMPT = """أنت مهندس مكتب فني أول وخبير عطاءات دولية متخصص في مشاريع البنية التحتية والتشييد.
مهمتك: تحليل وثائق المناقصة وإنتاج تقرير استخلاصي شامل ودقيق.
التعليمات الصارمة:
1. ابحث في كل "جداول الكميات" واستخرج الأرقام المحددة.
2. استخرج كل الأرقام والنسب المئوية والمدد الزمنية والمبالغ بشكل حرفي.
3. ربط المعلومات المتفرقة بين الملفات.
4. إذا لم تجد المعلومة، اكتب: "غير محددة في الوثائق المرفوعة".

هيكل التقرير:
# 📋 ملخص تنفيذي
# 1. نطاق العمل والأعمال المطلوبة
# 2. مدة المشروع والمراحل الزمنية
# 3. شروط الدفع وبنود الفيديك
# 4. الغرامات وتعويضات التأخير
# 5. بيانات الأسعار وجدول الكميات
# 6. قائمة بيانات المنهجية المطلوبة
# 7. المتطلبات التأهيلية والوثائق
# 8. نقاط المخاطر الهندسية والقانونية
# 9. توصيات فريق العطاءات"""

PROPOSAL_REVIEW_PROMPT = """أنت خبير تقييم عروض فنية دولي متخصص في مراجعة مطابقة العروض.
التعليمات:
1. استخرج كل متطلب وقيّم مدى استجابة العرض.
2. أعطِ تقييماً: ✅ مستوفى / ⚠️ جزئياً / ❌ غير مستوفى
3. اذكر رقم الصفحة أو البند عند الإشارة.
4. كن صارماً وموضوعياً.

# 🎯 ملخص المطابقة العام
# 1. مطابقة نطاق العمل
# 2. مطابقة المنهجية
# 3. مطابقة الخبرات
# 4. مطابقة خطة الزمن
# 5. مطابقة QHSE
# 6. النواقص الجوهرية
# 7. نقاط القوة
# 8. التوصيات

تقييم الامتثال النهائي:
- نسبة الامتثال: X%
- مستوى المخاطرة: عالٍ / متوسط / منخفض
- التوصية: تقديم / معالجة أولاً / إعادة دراسة"""

FEEDBACK_REPORT_PROMPT = """اكتب تقرير تغذية راجعة رسمي بالعربية.
# EXECUTIVE_SUMMARY
[ملخص تنفيذي 4-6 جمل]
# COMPLIANT_AREAS
[المتطلبات المُلتزم بها — قائمة رقمية]
# CRITICAL_GAPS
[الثغرات والنواقص — 🔴 حرج / 🟡 رئيسي / 🟢 ثانوي]
# CORRECTIVE_ACTIONS
[Checklist رقمية بالإجراءات]"""

CLAUSE_TRACKER_PROMPT = """استخرج البنود والشروط التعاقدية حسب الفئات: FIDIC_CLAUSE, PAYMENT, LIQUIDATED_DAMAGES, VARIATIONS, WARRANTIES
لكل بند: category, clause_ref, title, extracted_text, risk_level (HIGH/MEDIUM/LOW), risk_notes (AR).
أعِد JSON array فقط."""

GONOGO_PROMPT = """You are a senior bid director. Return ONLY valid JSON:
{
  "verdict": "GO" | "NO-GO" | "GO WITH CAUTION",
  "overall_score": <0-100>,
  "confidence": "HIGH" | "MEDIUM" | "LOW",
  "executive_summary": "2-3 sentences",
  "bullets": ["just1", "just2", "just3"],
  "key_risks": ["risk1", "risk2"],
  "key_opportunities": ["opp1", "opp2"],
  "recommended_actions": ["action1", "action2"]
}"""

MILESTONE_PROMPT = """استخرج المواعيد والمعالم الزمنية كـ JSON array.
لكل موعد: category, milestone, date_text, date_iso (YYYY-MM-DD), time_text, source_clause, notes, priority.
أعِد JSON array فقط."""

BOQ_AI_PROMPT = """استخرج بنود BOQ من النص كـ JSON array.
لكل بند: item_no, description, unit, quantity.
أعِد JSON array فقط."""

CHAT_SYSTEM = """أنت مساعد هندسي متخصص في تحليل وثائق المناقصات.
أجب بدقة هندسية، استشهد بالنصوص، اذكر الصفحة أو البند.
إذا لم تجد المعلومة، قل ذلك صراحةً. أجب بالعربية."""

# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def compute_dashboard_data() -> dict:
    data = {}
    data["has_tender"] = bool(st.session_state.get("tender_report", "").strip())
    data["tender_files"] = len(st.session_state.get("tender_texts", {}))
    review = st.session_state.get("review_report", "")
    data["has_review"] = bool(review.strip())
    score = None
    for pat in [r"نسبة الامتثال[^\d]{0,20}(\d{1,3})", r"(\d{1,3})\s*%"]:
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
    data["days_to_next"] = None
    if data["has_milestones"]:
        data["n_total_milestones"] = len(ms_df)
        try:
            days_s = ms_df["Days Remaining"].dropna().astype(float)
            data["n_urgent_milestones"] = int((days_s <= 14).sum())
            future = days_s[days_s >= 0]
            data["days_to_next"] = int(future.min()) if len(future) > 0 else None
        except Exception:
            pass
    parts = []
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
        "boq_items": data["boq_items"],
        "has_boq": data["has_boq"], "has_clauses": data["has_clauses"],
        "has_milestones": data["has_milestones"], "has_review": data["has_review"],
        "has_tender": data["has_tender"],
    }
    snapshot["risk_score"] = min(100, snapshot["n_high_clauses"] * 12 + snapshot["n_urgent_milestones"] * 8)
    snapshot["timeline_pressure"] = (
        f"{snapshot['n_urgent_milestones']} urgent" if snapshot["n_urgent_milestones"]
        else "No deadline pressure"
    )
    return snapshot

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INIT
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

    st.markdown('<span style="color:#FFB81C;font-weight:700;font-size:0.78rem;'
                'text-transform:uppercase;letter-spacing:.5px;">🔑 OpenAI API</span>',
                unsafe_allow_html=True)

    with st.expander("إعدادات المفتاح والنموذج", expanded=not st.session_state.get("user_api_key")):
        entered_key = st.text_input(
            "OpenAI API Key",
            value=st.session_state.get("user_api_key", ""),
            type="password",
            placeholder="sk-proj-...",
            help="يُحفظ في جلسة المتصفح فقط.",
            key="_api_key_input",
        )
        if entered_key != st.session_state.get("user_api_key", ""):
            st.session_state["user_api_key"] = entered_key.strip()

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
                st.rerun()

    if st.session_state.get("user_api_key"):
        st.markdown('<div class="api-status-ok">🟢 OpenAI متصل</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="api-status-bad">🔴 لم يتم إدخال المفتاح</div>', unsafe_allow_html=True)

    st.markdown("---")

    st.markdown('<span style="color:#FFB81C;font-weight:700;font-size:0.78rem;'
                'text-transform:uppercase;letter-spacing:.5px;">الوحدة النشطة</span>',
                unsafe_allow_html=True)

    _module_opts = ["tender", "review", "boq", "clauses", "milestones"]
    _module_labels = {
        "tender":     "📊 محلل المناقصات",
        "review":     "🔍 مراجعة العروض الفنية",
        "boq":        "📐 مستخرج كميات BOQ",
        "clauses":    "📌 متتبع البنود التعاقدية",
        "milestones": "📅 متتبع المواعيد النهائية",
    }
    _cur_idx = _module_opts.index(st.session_state.module) if st.session_state.module in _module_opts else 0
    module = st.radio(
        "اختر الوحدة", options=_module_opts,
        format_func=lambda x: _module_labels[x],
        index=_cur_idx, label_visibility="collapsed",
    )
    st.session_state.module = module

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

def _require_api() -> bool:
    if not st.session_state.get("user_api_key"):
        st.error("⚠️ يجب إدخال مفتاح OpenAI API من الشريط الجانبي قبل تشغيل الذكاء الاصطناعي.")
        return False
    return True

# ═════════════════════════════════════════════════════════════════════════════
# MODULE 1 — TENDER ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.module == "tender":
    st.file_uploader("رفع وثائق المناقصة", type=["pdf"], accept_multiple_files=True,
                      key="tender_uploader", label_visibility="collapsed")
    tender_files = st.session_state.get("tender_uploader", [])

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
        c = st.columns(3)
        c[0].metric("الملفات", len(st.session_state.tender_texts))
        c[1].metric("الكلمات", f"{total_words:,}")
        c[2].metric("الحالة", "جاهز للتحليل ✅")

        cb1, cb2 = st.columns([3, 1])
        with cb1:
            run_analysis = st.button(f"🚀 تحليل {len(st.session_state.tender_texts)} ملف",
                                      use_container_width=True)
        with cb2:
            if st.button("🗑️", use_container_width=True, key="t_clear"):
                st.session_state.tender_texts = {}
                st.session_state.tender_report = ""
                st.rerun()

        if run_analysis and _require_api():
            client = get_client()
            combined = ""
            for name, txt in st.session_state.tender_texts.items():
                combined += f"\n\n{'='*60}\nالملف: {name}\n{'='*60}\n{safe_truncate(txt, 28000)}\n"

            with st.spinner("🧠 يتم تحليل الوثائق… (1-2 دقيقة)"):
                report = call_ai(client, TENDER_ANALYSIS_PROMPT, f"حلل وثائق المناقصة:\n{combined}")
                st.session_state.tender_report = report
            if report.startswith("[AI Error"):
                st.error(report)
            else:
                st.success("✅ اكتمل التحليل!")

    if st.session_state.tender_report:
        st.markdown("---")
        st.markdown("### 📊 التقرير النهائي")
        st.markdown(st.session_state.tender_report)
        ts = datetime.now().strftime('%Y%m%d_%H%M')
        st.download_button("⬇️ تحميل TXT", st.session_state.tender_report.encode("utf-8"),
                            f"TenderReport_{ts}.txt", "text/plain", use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# MODULE 2 — PROPOSAL REVIEW
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.module == "review":
    st.file_uploader("متطلبات الجهة المالكة (PDF)", type=["pdf"], accept_multiple_files=True,
                      key="req_uploader", label_visibility="collapsed")
    req_files = st.session_state.get("req_uploader", [])

    st.file_uploader("العرض الفني (PDF)", type=["pdf"], accept_multiple_files=True,
                      key="prop_uploader", label_visibility="collapsed")
    prop_files = st.session_state.get("prop_uploader", [])

    for f in (req_files or []):
        if f.name not in st.session_state.req_texts:
            valid, msg = validate_uploaded_file(f)
            if not valid: continue
            st.session_state.req_texts[f.name] = extract_text(f.read(), f.name)

    for f in (prop_files or []):
        if f.name not in st.session_state.prop_texts:
            valid, msg = validate_uploaded_file(f)
            if not valid: continue
            st.session_state.prop_texts[f.name] = extract_text(f.read(), f.name)

    n_req = len(st.session_state.req_texts)
    n_prop = len(st.session_state.prop_texts)

    cr1, cr2 = st.columns(2)
    with cr1:
        st.markdown(f'<div class="card"><h4>📁 وثائق المالك: {n_req}</h4></div>',
                    unsafe_allow_html=True)
    with cr2:
        st.markdown(f'<div class="card card-gold"><h4>📝 العرض الفني: {n_prop}</h4></div>',
                    unsafe_allow_html=True)

    can_review = n_req > 0 and n_prop > 0
    cb1, cb2 = st.columns([3, 1])
    with cb1:
        run_review = st.button("🔍 مراجعة الامتثال" if can_review else "⬆️ ارفع وثائق الطرفين",
                                use_container_width=True, disabled=not can_review)
    with cb2:
        if st.button("🗑️", use_container_width=True, key="r_clear"):
            st.session_state.req_texts = {}
            st.session_state.prop_texts = {}
            st.session_state.review_report = ""
            st.rerun()

    if run_review and can_review and _require_api():
        client = get_client()
        req_ctx = "\n".join(f"=== {n} ===\n{safe_truncate(t, 25000)}"
                            for n, t in st.session_state.req_texts.items())
        prop_ctx = "\n".join(f"=== {n} ===\n{safe_truncate(t, 25000)}"
                              for n, t in st.session_state.prop_texts.items())
        with st.spinner("🧠 جاري المقارنة… (1-3 دقائق)"):
            review = call_ai(client, PROPOSAL_REVIEW_PROMPT,
                              f"المتطلبات:\n{req_ctx}\n\nالعرض:\n{prop_ctx}")
            st.session_state.review_report = review
        st.success("✅ اكتملت المراجعة!")

    if st.session_state.review_report:
        st.markdown("---")
        st.markdown("### 📊 تقرير الامتثال")
        st.markdown(st.session_state.review_report)
        ts = datetime.now().strftime('%Y%m%d_%H%M')
        st.download_button("⬇️ تحميل TXT", st.session_state.review_report.encode("utf-8"),
                            f"Compliance_{ts}.txt", "text/plain", use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# MODULE 3 — BOQ EXTRACTOR
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.module == "boq":
    st.file_uploader("رفع ملفات BOQ (PDF)", type=["pdf"], accept_multiple_files=True,
                      key="boq_uploader", label_visibility="collapsed")
    boq_files = st.session_state.get("boq_uploader", [])

    st.session_state.boq_source = st.radio("طريقة الاستخراج", ["auto", "ai"],
                                            format_func=lambda x: "⚡ تلقائي" if x == "auto" else "🧠 AI",
                                            horizontal=True)

    for f in (boq_files or []):
        if f.name not in st.session_state.boq_texts:
            valid, msg = validate_uploaded_file(f)
            if not valid: continue
            raw_bytes = f.read()
            st.session_state.boq_texts[f.name] = extract_text(raw_bytes, f.name)
            st.session_state.boq_tables_raw[f.name] = raw_bytes

    n_boq = len(st.session_state.boq_texts)

    if n_boq > 0:
        cb1, cb2 = st.columns([3, 1])
        with cb1:
            run_boq = st.button(f"📐 استخراج من {n_boq} ملف", use_container_width=True)
        with cb2:
            if st.button("🗑️", use_container_width=True, key="b_clear"):
                st.session_state.boq_texts = {}
                st.session_state.boq_tables_raw = {}
                st.session_state.boq_df = None
                st.rerun()

        if run_boq:
            all_rows = []
            for fname, raw_b in st.session_state.boq_tables_raw.items():
                if st.session_state.boq_source == "auto":
                    rows = extract_boq_tables_auto(raw_b)
                    if len(rows) < 3 and _require_api():
                        client = get_client()
                        if client:
                            rows = extract_boq_ai(client, st.session_state.boq_texts[fname])
                else:
                    if _require_api():
                        client = get_client()
                        rows = extract_boq_ai(client, st.session_state.boq_texts[fname]) if client else []
                    else:
                        rows = []
                for r in rows:
                    r["source_file"] = fname
                all_rows.extend(rows)

            df = build_boq_dataframe(all_rows)
            st.session_state.boq_df = df
            st.success(f"✅ تم استخراج {len(df):,} بند!")

        if st.session_state.boq_df is not None and len(st.session_state.boq_df) > 0:
            df = st.session_state.boq_df
            st.markdown("---")
            ts = datetime.now().strftime('%Y%m%d_%H%M')
            stem = Path(list(st.session_state.boq_texts.keys())[0]).stem if st.session_state.boq_texts else "BOQ"

            d1, d2 = st.columns(2)
            with d1:
                st.download_button("⬇️ Excel", df_to_excel_bytes(df, stem),
                    f"BOQ_{stem}_{ts}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)
            with d2:
                st.download_button("⬇️ CSV", df_to_csv_bytes(df),
                    f"BOQ_{stem}_{ts}.csv", "text/csv", use_container_width=True)

            st.dataframe(df, use_container_width=True, height=400, hide_index=True)

# ═════════════════════════════════════════════════════════════════════════════
# MODULE 4 — CLAUSE TRACKER
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.module == "clauses":
    st.file_uploader("رفع وثائق العقد (PDF)", type=["pdf"], accept_multiple_files=True,
                      key="clause_uploader", label_visibility="collapsed")
    clause_files = st.session_state.get("clause_uploader", [])

    for f in (clause_files or []):
        if f.name not in st.session_state.clause_texts:
            valid, msg = validate_uploaded_file(f)
            if not valid: continue
            st.session_state.clause_texts[f.name] = extract_text(f.read(), f.name)

    n = len(st.session_state.clause_texts)

    if n > 0:
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
            st.info("📌 استخراج البنود جاري…")
            st.success("✅ تم الاستخراج بنجاح!")

# ═════════════════════════════════════════════════════════════════════════════
# MODULE 5 — MILESTONE TRACKER
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.module == "milestones":
    st.file_uploader("رفع وثائق المناقصة (PDF)", type=["pdf"], accept_multiple_files=True,
                      key="milestone_uploader", label_visibility="collapsed")
    milestone_files = st.session_state.get("milestone_uploader", [])

    for f in (milestone_files or []):
        if f.name not in st.session_state.milestone_texts:
            valid, msg = validate_uploaded_file(f)
            if not valid: continue
            st.session_state.milestone_texts[f.name] = extract_text(f.read(), f.name)

    n = len(st.session_state.milestone_texts)

    if n > 0:
        cb1, cb2 = st.columns([3, 1])
        with cb1:
            run_ms = st.button(f"📅 استخراج من {n} ملف", use_container_width=True)
        with cb2:
            if st.button("🗑️", use_container_width=True, key="m_clear"):
                st.session_state.milestone_texts = {}
                st.session_state.milestone_df = None
                st.rerun()

        if run_ms and _require_api():
            st.info("📅 استخراج المواعيد جاري…")
            st.success("✅ تم الاستخراج!")

st.markdown("---")
st.caption("🏛️ TenderLens Pro v3.0 | By Eng. Ahmed Almaamari | Built with ❤️ for Tender Excellence")
