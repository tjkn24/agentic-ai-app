import re

# OWASP LLM01 — Prompt Injection patterns
# Extend this list with more sophisticated checks (e.g. DeepTeam, Garak)
INJECTION_PATTERNS = [
    r"ignore (all |previous |above )?instructions",
    r"you are now",
    r"disregard your (system |)prompt",
    r"act as (a |an )?(different|new|unrestricted)",
    r"jailbreak",
    r"<\|.*?\|>",           # token injection attempts
    r"system:\s*you",       # fake system message injection
]

def check_prompt_injection(text: str) -> bool:
    """Returns True if injection pattern detected."""
    lower = text.lower()
    return any(re.search(p, lower) for p in INJECTION_PATTERNS)

def sanitize_output(text: str) -> str:
    """
    OWASP LLM02 — Insecure Output Handling.
    Strip anything that could be executed by a downstream renderer.
    """
    text = re.sub(r"<script.*?>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"javascript:", "", text, flags=re.IGNORECASE)
    return text.strip()
