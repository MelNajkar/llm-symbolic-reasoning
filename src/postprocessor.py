def clean_llm_output(text: str) -> str:
    """
    Clean raw LLM output before validation and evaluation.

    LLMs may return explanations, markdown code blocks, or labels such as
    'Prolog:'. This function removes common unwanted formatting while keeping
    the Prolog expression itself.
    """

    if text is None:
        return ""

    cleaned = str(text).strip()

    # Remove markdown code fences if present
    cleaned = cleaned.replace("```prolog", "")
    cleaned = cleaned.replace("```", "")

    # Remove common labels
    prefixes = ["Prolog:", "prolog:", "Output:", "output:", "Answer:", "answer:"]
    for prefix in prefixes:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()

    # Keep only the first non-empty line if the model adds explanation after it
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    if lines:
        cleaned = " ".join(lines)

    return cleaned.strip()

def repair_prolog_output(text: str) -> str:
    """
    Apply simple rule-based repairs to generated Prolog output.

    This function only fixes surface-level formatting problems.
    It does not invent missing predicates, arguments, or logical conditions.
    """

    if text is None:
        return ""

    repaired = str(text).strip()

    if not repaired:
        return repaired

    # Normalize spacing around the Prolog rule operator
    repaired = repaired.replace(":-", " :- ")

    # Remove repeated spaces
    repaired = " ".join(repaired.split())

    # Add a final period if the output looks like Prolog but misses it
    if not repaired.endswith("."):
        if "(" in repaired and ")" in repaired:
            repaired += "."

    return repaired