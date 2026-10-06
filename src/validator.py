import re


def has_balanced_parentheses(text: str) -> bool:
    count = 0

    for char in text:
        if char == "(":
            count += 1
        elif char == ")":
            count -= 1

        if count < 0:
            return False

    return count == 0


def ends_with_period(text: str) -> bool:
    return text.strip().endswith(".")


def has_valid_predicate_format(text: str) -> bool:
    """
    Basic predicate check.
    Accepts facts like:
        likes(john,pizza).
    And rules like:
        pass(X) :- studies(X).
    """

    text = text.strip()

    if ":-" in text:
        head, body = text.split(":-", 1)
        parts = [head.strip()] + [p.strip() for p in body.replace(".", "").split(",")]
    else:
        parts = [text.replace(".", "").strip()]

    predicate_pattern = r"^[a-z][a-zA-Z0-9_]*\s*\(.*\)$"

    for part in parts:
        if not re.match(predicate_pattern, part):
            return False

    return True


def validate_prolog(text: str) -> dict:
    """
    Returns validation details for a generated Prolog expression.
    """

    text = text.strip()

    checks = {
        "ends_with_period": ends_with_period(text),
        "balanced_parentheses": has_balanced_parentheses(text),
        "valid_predicate_format": has_valid_predicate_format(text),
    }

    checks["syntax_valid"] = all(checks.values())

    return checks