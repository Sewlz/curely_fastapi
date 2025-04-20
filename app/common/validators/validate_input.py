import re
from uuid import UUID
from datetime import date
from typing import Optional

SCRIPT_TAG_RE = re.compile(r"<script.*?>.*?</script>", re.IGNORECASE)
SQL_FORBIDDEN_KEYWORDS = ('drop ', 'alter ', 'insert ', 'delete ', 'update ', '--')

def validate_no_scripts(value: str) -> str:
    if SCRIPT_TAG_RE.search(value):
        raise ValueError("Input contains disallowed <script> tags.")
    return value

def validate_no_sql_keywords(value: str) -> str:
    if any(keyword in value.lower() for keyword in SQL_FORBIDDEN_KEYWORDS):
        raise ValueError("Input contains SQL injection keywords.")
    return value

def validate_safe_text(value: str) -> str:
    value = validate_no_scripts(value)
    value = validate_no_sql_keywords(value)
    return value

def validate_uuid(value: str) -> str:
    try:
        UUID(value)
    except (ValueError, TypeError):
        raise ValueError("Invalid UUID format.")
    return value

def validate_safe_url(value: str) -> str:
    if not isinstance(value, str) or not value.startswith(("http://", "https://")):
        raise ValueError("Invalid URL format.")
    return value

def validate_dob(value: Optional[date]) -> Optional[date]:
    if value and value > date.today():
        raise ValueError("Date of birth cannot be in the future.")
    return value