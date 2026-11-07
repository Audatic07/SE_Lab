"""Small, total input-validation helpers for the Lab 7 spam filter.

Missing/invalid domains and links return "". Non-text or letter-free shouting
inputs return 0.0. Address checks intentionally cover a simple email-like format,
not the complete RFC mailbox grammar; no network/DNS requests are performed.
"""
import ipaddress
import re
from urllib.parse import urlsplit


_LINK = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)


def _valid_domain(domain):
    labels = domain.split('.')
    return bool(domain) and all(
        label and not label.startswith('-') and not label.endswith('-')
        and all(c.isalnum() or c == '-' for c in label)
        for label in labels
    )


def sender_domain(email):
    """Extract a lowercase domain from a simple address, or return ""."""
    if not isinstance(email, str):
        return ""
    email = email.strip()
    if email.count('@') != 1 or not email.isprintable() or any(c.isspace() for c in email):
        return ""
    local, domain = email.split('@')
    if (not local or local.startswith('.') or local.endswith('.') or '..' in local
            or any(c in '<>()[],:;\\"' for c in local) or not _valid_domain(domain)):
        return ""
    return domain.lower()

def first_link(text):
    """Return the first valid HTTP(S) link, without surrounding prose punctuation."""
    if not isinstance(text, str):
        return ""
    for match in _LINK.finditer(text):
        link = match.group().rstrip('.,!?;:')
        # Remove prose closing brackets, but retain balanced URL parentheses/IPv6.
        pairs = {')': '(', ']': '[', '}': '{'}
        surplus = {closing: link.count(closing) - link.count(opening)
                   for closing, opening in pairs.items()}
        end = len(link)
        while end and link[end - 1] in '.,!?;:)]}':
            closing = link[end - 1]
            if closing in pairs and surplus[closing] <= 0:
                break
            if closing in pairs:
                surplus[closing] -= 1
            end -= 1
        link = link[:end]
        if not link.isprintable():
            continue
        try:
            parsed = urlsplit(link)
            host = parsed.hostname
            if not host:
                continue
            # Accessing .port also validates malformed/out-of-range ports.
            if parsed.port is not None and not 0 <= parsed.port <= 65535:
                continue
            if ':' in host:
                ipaddress.IPv6Address(host)
            elif not _valid_domain(host):
                continue
        except (ValueError, UnicodeError):
            continue
        return link
    return ""

def shout_ratio(text):
    """Return uppercase alphabetic characters / all alphabetic characters (Unicode)."""
    if not isinstance(text, str):
        return 0.0
    letters = upper = 0
    for char in text:
        if char.isalpha():
            letters += 1
            upper += char.isupper()
    return upper / letters if letters else 0.0

def main():
    print("==== Running sender_domain ====")
    user_input = input("Enter a sender email (e.g. offers@Deals.com): ")
    result = sender_domain(user_input)
    print("Sender Domain:", result)

    print("\n==== Running first_link ====")
    user_input = input("Enter a message containing a link: ")
    result = first_link(user_input)
    print("First Link:", result)

    print("\n==== Running shout_ratio ====")
    user_input = input("Enter a message (e.g. FREE prize NOW): ")
    result = shout_ratio(user_input)
    print("Uppercase Ratio:", result)

if __name__ == "__main__":
    main()
