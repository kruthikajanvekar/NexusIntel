
import re

def validate_email(email: str) -> bool:
    """Basic regex for email validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def clean_url(url: str) -> str:
    """Ensure URL has scheme."""
    if not url.startswith(('http://', 'https://')):
        return 'https://' + url
    return url

def format_timestamp(ts):
    """Format datetime for UI display."""
    return ts.strftime("%B %d, %Y - %H:%M")
