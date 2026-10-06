def normalize_prolog(text: str) -> str:
    """
    Normalize Prolog strings for comparison.

    This removes spaces and lowercases the text.
    It keeps punctuation because punctuation matters in Prolog.
    """

    return text.strip().replace(" ", "").lower()


def exact_match(predicted: str, gold: str) -> bool:
    return predicted.strip() == gold.strip()


def normalized_match(predicted: str, gold: str) -> bool:
    return normalize_prolog(predicted) == normalize_prolog(gold)


def classify_error(predicted: str, gold: str, syntax_valid: bool) -> str:
    """
    Simple error classification for report analysis.
    """

    if exact_match(predicted, gold):
        return "none"

    if normalized_match(predicted, gold):
        return "formatting_difference"

    if not syntax_valid:
        return "syntax_error"

    if predicted.split("(")[0] != gold.split("(")[0]:
        return "predicate_error"

    return "semantic_or_argument_error"