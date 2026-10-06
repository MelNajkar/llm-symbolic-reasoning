import argparse
import os
import time
import pandas as pd


from llm_client import generate_prolog
from prompt_builder import build_translation_prompt
from postprocessor import clean_llm_output, repair_prolog_output
from validator import validate_prolog
from evaluator import exact_match, normalized_match, classify_error
from prolog_executor import validate_with_swipl

DATA_PATH = "data/dataset.csv"
OUTPUT_DIR = "outputs"
PREDICTIONS_PATH = "outputs/predictions.csv"
REPORT_PATH = "outputs/evaluation_report.txt"
CATEGORY_SUMMARY_PATH = "outputs/category_summary.csv"
PROMPTS_PATH = "outputs/generated_prompts.txt"


def write_overall_metrics(file, results_df):
    total = len(results_df)
    exact_accuracy = results_df["exact_match"].mean()
    normalized_accuracy = results_df["normalized_match"].mean()
    syntax_before_repair = results_df["syntax_valid_before_repair"].mean()
    syntax_after_repair = results_df["syntax_valid"].mean()
    repair_rate = results_df["repair_changed"].mean()

    file.write("Overall Metrics\n")
    file.write("===============\n")
    file.write(f"Total examples: {total}\n")
    file.write(f"Exact match accuracy: {exact_accuracy:.2%}\n")
    file.write(f"Normalized match accuracy: {normalized_accuracy:.2%}\n")
    file.write(f"Surface syntax validity before repair: {syntax_before_repair:.2%}\n")
    file.write(f"Surface syntax validity after repair: {syntax_after_repair:.2%}\n")
    file.write(f"Repair applied rate: {repair_rate:.2%}\n")

    if results_df["swipl_available"].any():
        swipl_validity = results_df["swipl_valid"].mean()
        file.write(f"SWI-Prolog load validity rate: {swipl_validity:.2%}\n\n")
    else:
        file.write("SWI-Prolog load validity rate: not available\n\n")


def build_category_summary(results_df):
    summary = (
        results_df
        .groupby("type")
        .agg(
            examples=("id", "count"),
            exact_match_accuracy=("exact_match", "mean"),
            normalized_match_accuracy=("normalized_match", "mean"),
            syntax_validity_before_repair=("syntax_valid_before_repair", "mean"),
            syntax_validity_after_repair=("syntax_valid", "mean"),
            swipl_load_validity_rate=("swipl_valid", "mean"),
        )
        .reset_index()
    )

    percentage_columns = [
        "exact_match_accuracy",
        "normalized_match_accuracy",
        "syntax_validity_before_repair",
        "syntax_validity_after_repair",
        "swipl_load_validity_rate",
    ]

    for column in percentage_columns:
        summary[column] = summary[column] * 100

    return summary


def write_category_metrics(file, category_summary):
    file.write("Category-Level Metrics\n")
    file.write("======================\n")

    for _, row in category_summary.iterrows():
        file.write(f"\nCategory: {row['type']}\n")
        file.write(f"Examples: {int(row['examples'])}\n")
        file.write(f"Exact match accuracy: {row['exact_match_accuracy']:.2f}%\n")
        file.write(f"Normalized match accuracy: {row['normalized_match_accuracy']:.2f}%\n")
        file.write(
            "Surface syntax validity before repair: "
            f"{row['syntax_validity_before_repair']:.2f}%\n"
        )
        file.write(
            "Surface syntax validity after repair: "
            f"{row['syntax_validity_after_repair']:.2f}%\n"
        )
        file.write(
            "SWI-Prolog load validity rate: "
            f"{row['swipl_load_validity_rate']:.2f}%\n"
        )


def write_error_counts(file, results_df):
    file.write("\n\nError Type Counts\n")
    file.write("=================\n")

    error_counts = results_df["error_type"].value_counts()

    for error_type, count in error_counts.items():
        file.write(f"- {error_type}: {count}\n")


def save_prompts(dataset):
    with open(PROMPTS_PATH, "w", encoding="utf-8") as file:
        for _, row in dataset.iterrows():
            file.write("=" * 80 + "\n")
            file.write(f"Example ID: {row['id']}\n")
            file.write(f"Type: {row['type']}\n")
            file.write("-" * 80 + "\n")
            file.write(build_translation_prompt(row["natural_language"]))
            file.write("\n\n")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Translate controlled English sentences into Prolog terms."
    )

    parser.add_argument(
        "--mode",
        choices=["mock", "experiment", "api"],
        default="mock",
        help="Generation mode: mock, experiment, or api.",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional number of examples to evaluate.",
    )

    parser.add_argument(
        "--mixed-api-test",
        action="store_true",
        help="Run API mode on a fixed mixed subset of 5 examples.",
        
    )

    parser.add_argument(
        "--mixed-api-test-10",
        action="store_true",
        help="Run API mode on a fixed mixed subset of 10 examples.",
    )


    return parser.parse_args()


def main():
    args = parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    dataset = pd.read_csv(DATA_PATH)

    if args.mixed_api_test_10:
        mixed_ids = [1, 2, 11, 12, 21, 22, 29, 30, 37, 38]
        dataset = dataset[dataset["id"].isin(mixed_ids)]
    elif args.mixed_api_test:
        mixed_ids = [1, 11, 21, 29, 37]
        dataset = dataset[dataset["id"].isin(mixed_ids)]
    elif args.limit is not None:
        dataset = dataset.head(args.limit)
    # Save generated prompts for transparency and report documentation.
    save_prompts(dataset)

    results = []

    for _, row in dataset.iterrows():
        sentence = row["natural_language"]
        gold = row["gold_prolog"]

        if args.mode == "api":
            time.sleep(15)

        raw_prediction = generate_prolog(sentence, mode=args.mode)

        cleaned_prediction = clean_llm_output(raw_prediction)
        validation_before_repair = validate_prolog(cleaned_prediction)

        predicted = repair_prolog_output(cleaned_prediction)
        validation = validate_prolog(predicted)

        swipl_validation = validate_with_swipl(predicted)

        is_exact = exact_match(predicted, gold)
        is_normalized = normalized_match(predicted, gold)
        error_type = classify_error(
            predicted=predicted,
            gold=gold,
            syntax_valid=validation["syntax_valid"],
        )

        results.append(
            {
                "id": row["id"],
                "type": row["type"],
                "natural_language": sentence,
                "gold_prolog": gold,
                "raw_prediction": raw_prediction,
                "cleaned_prolog": cleaned_prediction,
                "predicted_prolog": predicted,
                "repair_changed": cleaned_prediction != predicted,
                "exact_match": is_exact,
                "normalized_match": is_normalized,
                "syntax_valid_before_repair": validation_before_repair["syntax_valid"],
                "syntax_valid": validation["syntax_valid"],
                "swipl_available": swipl_validation["swipl_available"],
                "swipl_valid": swipl_validation["swipl_valid"],
                "swipl_error": swipl_validation["swipl_error"],
                "error_type": error_type,
            }
        )

   
    results_df = pd.DataFrame(results)

    if args.mode == "api":
        predictions_path = "outputs/api_predictions.csv"
        report_path = "outputs/api_evaluation_report.txt"
        category_summary_path = "outputs/api_category_summary.csv"
    else:
        predictions_path = PREDICTIONS_PATH
        report_path = REPORT_PATH
        category_summary_path = CATEGORY_SUMMARY_PATH

    results_df.to_csv(predictions_path, index=False)

    category_summary = build_category_summary(results_df)
    category_summary.to_csv(category_summary_path, index=False)

    with open(report_path, "w", encoding="utf-8") as file:
        file.write("Evaluation Report\n")
        file.write("=================\n\n")
        file.write(f"Generation mode: {args.mode}\n\n")

        write_overall_metrics(file, results_df)
        write_category_metrics(file, category_summary)
        write_error_counts(file, results_df)

    print("Pipeline completed successfully.")
    print(f"Generation mode: {args.mode}")
    print(f"Predictions saved to: {predictions_path}")
    print(f"Category summary saved to: {category_summary_path}")
    print(f"Generated prompts saved to: {PROMPTS_PATH}")
    print(f"Evaluation report saved to: {report_path}")

if __name__ == "__main__":
    main()