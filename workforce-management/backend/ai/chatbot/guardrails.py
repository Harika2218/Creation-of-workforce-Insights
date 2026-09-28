"""
Input and Output Security Guardrails
------------------------------------
Defends against prompt injection, system prompt extraction, credential leaks,
and unauthorized data exfiltration. Strips sensitive PII before LLM reasoning.
"""

from typing import Tuple, Dict, Any, List
import re

class GuardrailEngine:
    """
    Validates user queries against adversarial patterns and sanitizes context.
    """

    PROMPT_INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
        r"disregard\s+(all\s+)?(previous|prior)\s+rules",
        r"reveal\s+(your\s+)?(system\s+prompt|instructions|initial\s+prompt)",
        r"what\s+is\s+your\s+system\s+prompt",
        r"act\s+as\s+(an\s+unrestricted|a\s+root|sudo|jailbreak)",
        r"bypass\s+(all\s+)?(authorization|security|rbac|permissions)",
        r"show\s+(me\s+)?(everyone['’]?s\s+salary|all\s+passwords|api\s+keys)",
        r"dump\s+(the\s+entire\s+)?database",
        r"drop\s+database",
        r"sql\s+injection",
        r"\{\{.*\}\}",
        r"<script.*?>",
    ]

    SECRET_MASKS = [
        (r"Bearer\s+[A-Za-z0-9\-\._~\+\/]+=*", "[REDACTED_TOKEN]"),
        (r"(password|pwd|secret|api_key|jwt_secret)\s*[:=]\s*['\"][^'\"]+['\"]", r"\1: [REDACTED]"),
        (r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "[REDACTED_CARD]"),
        (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b", "[EMAIL_MASKED]"),
        (r"\+?\d{1,3}[-\s]?\d{10}\b", "[PHONE_MASKED]"),
    ]

    @classmethod
    def check_query_safety(cls, query: str) -> Tuple[bool, str]:
        """
        Checks if the input query contains prompt injection or adversarial attempts.
        Returns (is_safe, error_or_sanitized_message).
        """
        q_clean = query.strip()

        for pattern in cls.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, q_clean, re.IGNORECASE):
                return False, (
                    "Security Notice: Your message contains instructions or patterns that conflict "
                    "with our system safety policies. Please rephrase your HR query directly."
                )

        return True, q_clean

    @classmethod
    def sanitize_pii(cls, text: str) -> str:
        """
        Redacts unnecessary PII (passwords, phone numbers, external emails)
        before context is passed to the LLM.
        """
        sanitized = text
        for pattern, replacement in cls.SECRET_MASKS:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        return sanitized

    @classmethod
    def verify_output_safety(cls, output: str) -> str:
        """
        Ensures the generated assistant response does not leak internal keys or secrets.
        """
        safe_output = output
        # Mask any accidental JWT tokens or environment secrets
        safe_output = re.sub(r"ey[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+", "[REDACTED_JWT]", safe_output)
        safe_output = re.sub(r"mongodb(?:\+srv)?:\/\/[^\s]+", "[REDACTED_DB_URI]", safe_output)
        return safe_output
