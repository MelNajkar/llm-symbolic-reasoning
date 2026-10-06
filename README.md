# From Natural Language Sentences to Prolog Terms via LLMs

This project implements a simplified LLM-based formula extractor inspired by LoRP, a framework that combines large language models with Prolog-based symbolic reasoning.

The goal of the project is to translate controlled English sentences into Prolog facts and rules, validate the generated outputs, and evaluate them against a manually created gold dataset.

## Project Structure

```text
sdai-nl2prolog/
├── data/
│   └── dataset.csv
├── outputs/
│   ├── predictions.csv
│   ├── category_summary.csv
│   ├── generated_prompts.txt
│   └── evaluation_report.txt
├── src/
│   ├── main.py
│   ├── prompt_builder.py
│   ├── llm_client.py
│   ├── postprocessor.py
│   ├── validator.py
│   └── evaluator.py
├── README.md
└── requirements.txt
```

## Dataset

The dataset contains 40 controlled English examples divided into five categories:

- simple facts
- binary relations
- one-condition rules
- two-condition rules
- multi-sentence examples

Each example contains a natural-language input and a manually written gold Prolog output.

## Generation Modes

The system supports three modes:

### Mock mode

Perfect predefined translations used to verify that the pipeline works correctly.

```bash
python3 src/main.py --mode mock
```

### Experiment mode

Simulated imperfect LLM outputs used to produce realistic evaluation results and error analysis.

```bash
python3 src/main.py --mode experiment
```

### API mode

Real Gemini API mode used for a small supplementary mixed-subset test.

```bash
python3 src/main.py --mode api
```
## Installation

Install dependencies:

```bash
pip install -r requirements.txt
```
## Usage

Run the experiment mode:

```bash
python3 src/main.py --mode experiment
```

### Run 10-example mixed API test

```bash
python3 src/main.py --mode api --mixed-api-test-10
```


### SWI-Prolog validation


If SWI-Prolog is installed, the pipeline also checks whether generated Prolog outputs can be loaded by the `swipl` interpreter. This provides an execution-oriented validation step in addition to surface-level syntax checks.

The program generates the following files in the `outputs/` folder:

- `predictions.csv`: detailed prediction results for every example
- `category_summary.csv`: category-level evaluation metrics
- `generated_prompts.txt`: prompts generated for each input sentence
- `evaluation_report.txt`: overall metrics and error counts

## Evaluation Metrics

The project uses the following metrics:
- exact match accuracy
- normalized exact match accuracy
- syntax validity rate
- error type classification

## Error Types

The evaluator classifies errors into:
- none
- formatting_difference
- syntax_error
- predicate_error
- semantic_or_argument_error

## Notes

The main experiment mode is designed to be reproducible without requiring paid APIs or external LLM services. The API mode connects the same pipeline to a real Gemini API call and was used for a small supplementary mixed-subset test.

Mock mode and experiment mode do not require a Gemini API key. API mode requires the `GEMINI_API_KEY` environment variable. SWI-Prolog load validation requires SWI-Prolog to be installed and available through the `swipl` command.