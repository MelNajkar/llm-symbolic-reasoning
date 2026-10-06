import os
import time
from prompt_builder import build_translation_prompt


def mock_generate_prolog(sentence: str) -> str:
    """
    Perfect mock LLM function.

    This simulates ideal LLM translations and is used to verify that the
    pipeline, validator, and evaluator work correctly.
    """

    mock_outputs = {
        "John likes pizza.": "likes(john,pizza).",
        "Mary studies artificial intelligence.": "studies(mary,artificial_intelligence).",
        "Rome is a city.": "city(rome).",
        "Alice knows Bob.": "knows(alice,bob).",
        "The dog chases the cat.": "chases(dog,cat).",
        "Sara reads books.": "reads(sara,books).",
        "Tom plays football.": "plays(tom,football).",
        "Paris is a capital.": "capital(paris).",
        "The bird flies.": "flies(bird).",
        "Anna teaches mathematics.": "teaches(anna,mathematics).",

        "John is the father of Mary.": "father(john,mary).",
        "Mary is the mother of Anna.": "mother(mary,anna).",
        "Bob is a friend of Alice.": "friend(bob,alice).",
        "The cat is on the table.": "on(cat,table).",
        "The book is inside the bag.": "inside(book,bag).",
        "Luca lives in Bologna.": "lives_in(luca,bologna).",
        "Marta works at the university.": "works_at(marta,university).",
        "The train goes to Milan.": "goes_to(train,milan).",
        "The student uses a computer.": "uses(student,computer).",
        "The teacher explains the lesson.": "explains(teacher,lesson).",

        "If someone studies then they pass.": "pass(X) :- studies(X).",
        "If someone works then they earn money.": "earn_money(X) :- works(X).",
        "If something is a cat then it is an animal.": "animal(X) :- cat(X).",
        "If someone exercises then they are healthy.": "healthy(X) :- exercises(X).",
        "If something is a bird then it can fly.": "can_fly(X) :- bird(X).",
        "If someone reads then they learn.": "learns(X) :- reads(X).",
        "If something is a city then it is a place.": "place(X) :- city(X).",
        "If someone teaches then they work.": "works(X) :- teaches(X).",

        "If someone is hungry and is a cat then they meow.": "meow(X) :- hungry(X), cat(X).",
        "If someone is a student and studies then they pass.": "pass(X) :- student(X), studies(X).",
        "If someone is a person and works then they earn money.": "earn_money(X) :- person(X), works(X).",
        "If something is a bird and has wings then it can fly.": "can_fly(X) :- bird(X), has_wings(X).",
        "If someone is tired and sleeps then they recover.": "recover(X) :- tired(X), sleeps(X).",
        "If something is a vehicle and has wheels then it moves.": "moves(X) :- vehicle(X), has_wheels(X).",
        "If someone is a teacher and explains lessons then they educate.": "educates(X) :- teacher(X), explains_lessons(X).",
        "If someone is a student and attends class then they learn.": "learns(X) :- student(X), attends_class(X).",

        "Mary is a student. Mary studies. If someone is a student and studies then they pass.": "student(mary). studies(mary). pass(X) :- student(X), studies(X).",
        "Tom is hungry. Tom is a cat. If someone is hungry and is a cat then they meow.": "hungry(tom). cat(tom). meow(X) :- hungry(X), cat(X).",
        "Luca is a person. Luca works. If someone is a person and works then they earn money.": "person(luca). works(luca). earn_money(X) :- person(X), works(X).",
        "Tweety is a bird. Tweety has wings. If something is a bird and has wings then it can fly.": "bird(tweety). has_wings(tweety). can_fly(X) :- bird(X), has_wings(X).",
    }

    return mock_outputs.get(sentence, "translation_error.")


def experiment_generate_prolog(sentence: str) -> str:
    """
    Imperfect simulated LLM function.

    This mode intentionally contains realistic translation errors.
    It is useful for producing meaningful evaluation results and error
    analysis without depending on an external API.
    """

    experiment_outputs = {
        # Facts: mostly correct
        "John likes pizza.": "likes(john,pizza).",
        "Mary studies artificial intelligence.": "studies(mary,artificial_intelligence).",
        "Rome is a city.": "city(rome).",
        "Alice knows Bob.": "knows(alice,bob).",
        "The dog chases the cat.": "chase(dog,cat).",  # predicate error
        "Sara reads books.": "reads(sara,books).",
        "Tom plays football.": "plays(tom,football).",
        "Paris is a capital.": "capital(paris).",
        "The bird flies.": "flies(bird).",
        "Anna teaches mathematics.": "teaches(anna,mathematics)",  # missing period

        # Relations: some argument/predicate errors
        "John is the father of Mary.": "father(john,mary).",
        "Mary is the mother of Anna.": "mother(mary,anna).",
        "Bob is a friend of Alice.": "friend(alice,bob).",  # argument order error
        "The cat is on the table.": "on(cat,table).",
        "The book is inside the bag.": "inside(book,bag).",
        "Luca lives in Bologna.": "lives(luca,bologna).",  # predicate error
        "Marta works at the university.": "works_at(marta,university).",
        "The train goes to Milan.": "goes_to(train,milan).",
        "The student uses a computer.": "uses(student,computer).",
        "The teacher explains the lesson.": "explains(teacher,lesson).",

        # One-condition rules: harder
        "If someone studies then they pass.": "pass(X) :- studies(X).",
        "If someone works then they earn money.": "earn_money(X) :- works(X).",
        "If something is a cat then it is an animal.": "animal(X) :- cat(X).",
        "If someone exercises then they are healthy.": "healthy(X) :- exercise(X).",  # predicate error
        "If something is a bird then it can fly.": "can_fly(X) :- bird(X).",
        "If someone reads then they learn.": "learns(X) :- reads(X).",
        "If something is a city then it is a place.": "place(X) :- city(X).",
        "If someone teaches then they work.": "works(X) :- teaches(X)",  # missing period

        # Two-condition rules: more errors
        "If someone is hungry and is a cat then they meow.": "meow(X) :- hungry(X), cat(X).",
        "If someone is a student and studies then they pass.": "pass(X) :- student(X), studies(X).",
        "If someone is a person and works then they earn money.": "earn_money(X) :- works(X).",  # missing condition
        "If something is a bird and has wings then it can fly.": "can_fly(X) :- bird(X), has_wings(X).",
        "If someone is tired and sleeps then they recover.": "recover(X) :- tired(X), sleep(X).",  # predicate error
        "If something is a vehicle and has wheels then it moves.": "moves(X) :- vehicle(X), has_wheels(X).",
        "If someone is a teacher and explains lessons then they educate.": "educates(X) :- teacher(X), explains_lessons(X).",
        "If someone is a student and attends class then they learn.": "learns(X) :- student(X).",  # missing condition

        # Multi-sentence: hardest
        "Mary is a student. Mary studies. If someone is a student and studies then they pass.": "student(mary). studies(mary). pass(X) :- student(X), studies(X).",
        "Tom is hungry. Tom is a cat. If someone is hungry and is a cat then they meow.": "hungry(tom). cat(tom). meow(X) :- cat(X), hungry(X).",  # logically same but different order
        "Luca is a person. Luca works. If someone is a person and works then they earn money.": "person(luca). works(luca). earn_money(X) :- works(X).",  # missing condition
        "Tweety is a bird. Tweety has wings. If something is a bird and has wings then it can fly.": "bird(tweety). has_wings(tweety). can_fly(X) :- bird(X), has_wings(X)",
    }

    return experiment_outputs.get(sentence, "translation_error.")


def api_generate_prolog(sentence: str) -> str:
    """
    Real LLM API generation using the Google Gen AI SDK.

    The API key must be stored in the GEMINI_API_KEY environment variable.
    The function builds the same translation prompt used in the rest of the
    pipeline and sends it to a Gemini model.

    A small retry mechanism is included because free-tier API calls may fail
    temporarily due to quota limits or high model demand.
    """
    from google import genai
    
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY is not set. "
            "Run: export GEMINI_API_KEY='your-api-key'"
        )

    prompt = build_translation_prompt(sentence)
    client = genai.Client(api_key=api_key)

    max_retries = 3
    wait_seconds = 60

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
            )
            return response.text.strip()

        except Exception as e:
            print(f"API attempt {attempt + 1} failed: {e}")

            if attempt < max_retries - 1:
                print(f"Waiting {wait_seconds} seconds before retrying...")
                time.sleep(wait_seconds)
            else:
                return "api_error."


def generate_prolog(sentence: str, mode: str = "mock") -> str:
    """
    Generate Prolog from an English sentence.

    Available modes:
    - mock: perfect reproducible outputs
    - experiment: imperfect simulated LLM outputs
    - api: placeholder for future LLM API integration
    """

    if mode == "mock":
        return mock_generate_prolog(sentence)

    if mode == "experiment":
        return experiment_generate_prolog(sentence)

    if mode == "api":
        return api_generate_prolog(sentence)

    raise ValueError(f"Unknown generation mode: {mode}")