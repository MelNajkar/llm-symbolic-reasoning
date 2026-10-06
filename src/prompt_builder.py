def build_translation_prompt(sentence: str) -> str:
    """
    Build a few-shot prompt for translating controlled English sentences
    into Prolog facts and rules.

    This prompt is inspired by LoRP-style translation: the LLM is not asked
    to solve the problem directly, but to convert natural language into a
    symbolic Prolog representation.
    """

    prompt = f"""
You are a translator from controlled English to Prolog.

Your task is to translate the English sentence into valid Prolog.

Rules:
- Output only Prolog.
- Do not explain.
- Use lowercase atoms.
- Use underscores for multi-word concepts.
- End every fact or rule with a period.
- Use variables such as X, Y, Z for general rules.
- Use the Prolog rule format: head :- body.
- For conjunctions, separate predicates with commas.

Examples:

English: John likes pizza.
Prolog: likes(john,pizza).

English: Mary studies artificial intelligence.
Prolog: studies(mary,artificial_intelligence).

English: If someone studies then they pass.
Prolog: pass(X) :- studies(X).

English: If someone is a student and studies then they pass.
Prolog: pass(X) :- student(X), studies(X).

English: Mary is a student. Mary studies. If someone is a student and studies then they pass.
Prolog: student(mary). studies(mary). pass(X) :- student(X), studies(X).

Now translate the following sentence.

English: {sentence}
Prolog:
""".strip()

    return prompt