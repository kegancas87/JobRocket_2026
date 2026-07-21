"""
Bulk CV Upload Service — helpers for parsing filenames, extracting text from
PDF/DOCX/DOC files, and pulling basic profile fields (email, phone, skills).

Used by the admin bulk CV upload endpoint. Nothing here mutates the database —
all extraction is pure functions so it's easy to test and reuse.
"""
from __future__ import annotations

import io
import re
import unicodedata
import uuid
from pathlib import Path
from typing import Optional, Tuple, List

# CV keywords to strip from filenames when detecting a person's name
_FILENAME_STOPWORDS = {
    "cv", "resume", "curriculum", "vitae", "profile", "final",
    "v1", "v2", "v3", "draft", "copy", "updated", "new", "old",
    "2024", "2025", "2026",
}

# A pragmatic list of common tech/business skills to keyword-match against
# extracted CV text. Not exhaustive — but a solid starting point that avoids
# false positives on common English words.
_COMMON_SKILLS = [
    # Programming languages
    "Python", "JavaScript", "TypeScript", "Java", "C#", "C++", "PHP", "Ruby",
    "Go", "Rust", "Kotlin", "Swift", "Scala", "R", "MATLAB", "Perl",
    # Frontend
    "React", "Angular", "Vue", "Svelte", "Next.js", "Nuxt.js", "HTML", "CSS",
    "Tailwind", "Bootstrap", "SASS", "LESS", "Redux",
    # Backend / frameworks
    "Node.js", "Express", "Django", "Flask", "FastAPI", "Spring", "Laravel",
    "Rails", ".NET", "ASP.NET",
    # Databases
    "MongoDB", "PostgreSQL", "MySQL", "SQLite", "Redis", "Cassandra",
    "DynamoDB", "Oracle", "SQL Server", "Firebase",
    # DevOps / Cloud
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Jenkins", "GitHub Actions",
    "GitLab CI", "Terraform", "Ansible", "CircleCI",
    # Data / AI
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Pandas",
    "NumPy", "Scikit-learn", "Data Analysis", "Data Science", "SQL", "NoSQL",
    "Power BI", "Tableau", "Excel",
    # Design / product
    "Figma", "Adobe XD", "Photoshop", "Illustrator", "Sketch", "InDesign",
    "UI/UX", "Wireframing", "Prototyping",
    # Project management / soft
    "Agile", "Scrum", "Kanban", "JIRA", "Confluence", "Trello", "Asana",
    "Project Management", "Product Management", "Leadership",
    "Communication", "Teamwork", "Problem Solving",
    # Business / finance
    "Accounting", "Bookkeeping", "SAP", "Xero", "QuickBooks", "Payroll",
    "Auditing", "Financial Analysis", "Budgeting", "Reporting",
    # Marketing / sales
    "SEO", "SEM", "Google Analytics", "Google Ads", "Facebook Ads",
    "Content Marketing", "Copywriting", "Email Marketing", "CRM", "Salesforce",
    "HubSpot",
]

# Pre-compile skill matcher (case-insensitive, word-boundary style)
_SKILL_PATTERNS = [
    (skill, re.compile(r"(?<![A-Za-z0-9])" + re.escape(skill) + r"(?![A-Za-z0-9])", re.IGNORECASE))
    for skill in _COMMON_SKILLS
]

# Email + phone regex
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(
    r"(?:(?:\+?27|0)[\s\-]?)?(?:\(0\)|0)?(?:\d[\s\-]?){8,10}\d"
)


# ---------------------------------------------------------------------------
# Filename → name detection
# ---------------------------------------------------------------------------
def _slugify(text: str) -> str:
    """Turn a string into a URL/email-safe slug."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    return text or "cv"


def extract_name_from_filename(filename: str) -> Tuple[Optional[str], Optional[str]]:
    """Best-effort name detection from a CV filename.

    Handles common patterns like:
      • John_Smith_CV.pdf
      • John Smith - Resume.pdf
      • CV - John Smith.docx
      • john.smith.pdf
      • SmithJohn_CV.pdf   (returned as-is; can't reliably split CamelCase surnames)

    Returns (first_name, last_name). Either may be None if we can't detect one.
    """
    if not filename:
        return None, None

    stem = Path(filename).stem  # remove extension

    # Split on common separators
    tokens = re.split(r"[_\-\.\s]+", stem)

    # Filter stopwords, numbers, and single-char tokens
    words: List[str] = []
    for tok in tokens:
        clean = tok.strip()
        if not clean:
            continue
        if clean.lower() in _FILENAME_STOPWORDS:
            continue
        if not re.search(r"[A-Za-z]", clean):
            continue
        if len(clean) < 2:
            continue
        # Only keep tokens that look like a name word (mostly letters)
        letters = sum(1 for c in clean if c.isalpha())
        if letters / max(len(clean), 1) < 0.7:
            continue
        words.append(clean)

    if not words:
        return None, None

    if len(words) == 1:
        # Try to split CamelCase, e.g. JohnSmith → John Smith
        camel = re.findall(r"[A-Z][a-z]+", words[0])
        if len(camel) >= 2:
            return camel[0].title(), " ".join(camel[1:]).title()
        return words[0].title(), None

    first = words[0].title()
    last = " ".join(w.title() for w in words[1:])
    # Sanity cap on length
    if len(last) > 40:
        last = last[:40]
    return first, last


# ---------------------------------------------------------------------------
# Email generation
# ---------------------------------------------------------------------------
def generate_bulk_email(filename: str, existing_slugs: set) -> str:
    """Build a unique email based on the CV filename.

    Strategy:
      • Slugify the filename stem (john-smith-cv)
      • Compose `<slug>@jobrocket.co.za`
      • If that slug is already used (either in DB or in this batch),
        suffix a short random id: `<slug>+ab3f9@jobrocket.co.za`
    """
    stem = Path(filename).stem
    slug = _slugify(stem)[:40]  # cap length so email stays sane
    if slug not in existing_slugs:
        existing_slugs.add(slug)
        return f"{slug}@jobrocket.co.za"

    # Collision — add short random suffix
    suffix = uuid.uuid4().hex[:5]
    slug_with_suffix = f"{slug}+{suffix}"
    existing_slugs.add(slug_with_suffix)
    return f"{slug_with_suffix}@jobrocket.co.za"


# ---------------------------------------------------------------------------
# CV text extraction
# ---------------------------------------------------------------------------
def extract_text_from_cv(content: bytes, extension: str) -> str:
    """Extract plain text from a CV file. Best-effort — returns '' on failure.

    Supports .pdf (pypdf) and .docx (python-docx). Old .doc format is not
    supported here without external tools like antiword/libreoffice, so those
    files are saved but no text is extracted.
    """
    ext = extension.lower().lstrip(".")
    try:
        if ext == "pdf":
            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(content))
            parts = []
            for page in reader.pages:
                try:
                    parts.append(page.extract_text() or "")
                except Exception:
                    continue
            return "\n".join(parts)

        if ext == "docx":
            from docx import Document

            doc = Document(io.BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs)

        # .doc (legacy) — not supported without external tools
        return ""
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Extract profile fields from CV text
# ---------------------------------------------------------------------------
def extract_email_from_text(text: str) -> Optional[str]:
    if not text:
        return None
    m = _EMAIL_RE.search(text)
    return m.group(0).lower() if m else None


def extract_phone_from_text(text: str) -> Optional[str]:
    if not text:
        return None
    # Look for South African-style numbers (10 digits or +27 prefix)
    m = _PHONE_RE.search(text)
    if not m:
        return None
    phone = re.sub(r"[^\d+]", "", m.group(0))
    # Basic sanity: length 10-13 digits (or +27 followed by 9)
    digits = re.sub(r"\D", "", phone)
    if 9 <= len(digits) <= 13:
        return phone
    return None


def extract_skills_from_text(text: str, max_skills: int = 30) -> List[str]:
    if not text:
        return []
    found: List[str] = []
    seen = set()
    for skill, pattern in _SKILL_PATTERNS:
        if skill in seen:
            continue
        if pattern.search(text):
            found.append(skill)
            seen.add(skill)
        if len(found) >= max_skills:
            break
    return found
