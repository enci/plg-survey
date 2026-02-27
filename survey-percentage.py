#!/usr/bin/env python3

import json
from pathlib import Path
from typing import Any, Dict, List


def load_json(path: Path) -> Any:
	with path.open("r", encoding="utf-8") as file:
		return json.load(file)


def is_answered(value: Any) -> bool:
	if value is None:
		return False
	if isinstance(value, str):
		return value.strip() != ""
	if isinstance(value, list):
		return len(value) > 0
	if isinstance(value, dict):
		return any(is_answered(item_value) for item_value in value.values())
	return True


def count_answers_by_question(
	responses: List[Dict[str, Any]],
	schema_questions: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
	total_respondents = len(responses)
	counts: List[Dict[str, Any]] = []

	for question_key, question_info in schema_questions.items():
		question_text = question_info.get("question", question_key)
		question_type = question_info.get("type", "unknown")

		answered_count = sum(
			1 for response in responses if is_answered(response.get(question_key))
		)

		result_row: Dict[str, Any] = {
			"question_key": question_key,
			"question_type": question_type,
			"question_text": question_text,
			"responses": answered_count,
			"total_respondents": total_respondents,
		}

		if question_type == "matrix":
			items = question_info.get("items", [])
			item_counts: Dict[str, int] = {}

			for item in items:
				item_counts[item] = sum(
					1
					for response in responses
					if is_answered((response.get(question_key) or {}).get(item))
				)

			result_row["matrix_item_responses"] = item_counts

		counts.append(result_row)

	return counts


def print_counts(counts: List[Dict[str, Any]]) -> None:
	if not counts:
		print("No questions found.")
		return

	print("Responses per question")
	print("=" * 80)

	for row in counts:
		print(
			f"{row['question_key']}: {row['responses']}/{row['total_respondents']} "
			f"({row['question_type']})"
		)

		matrix_item_counts = row.get("matrix_item_responses")
		if matrix_item_counts:
			for item_name, item_count in matrix_item_counts.items():
				print(f"  - {item_name}: {item_count}/{row['total_respondents']}")


def escape_latex(text: str) -> str:
	replacements = {
		"\\": r"\textbackslash{}",
		"&": r"\&",
		"%": r"\%",
		"$": r"\$",
		"#": r"\#",
		"_": r"\_",
		"{": r"\{",
		"}": r"\}",
		"~": r"\textasciitilde{}",
		"^": r"\textasciicircum{}",
	}
	return "".join(replacements.get(char, char) for char in text)


def build_latex_table(counts: List[Dict[str, Any]]) -> str:
	filtered_counts = [row for row in counts if row.get("question_key") != "id"]

	lines = [
		r"\begin{table}[htbp]",
		r"\centering",
		r"\caption{Survey response counts per question}",
		r"\label{app:survey-response-counts}",
		r"\begin{tabular}{p{0.72\textwidth}rr}",
		r"\hline",
		"Question & Responses & Rate " + r"\\",
		r"\hline",
	]

	for index, row in enumerate(filtered_counts, start=1):
		question_text = escape_latex(str(row.get("question_text") or row["question_key"]))
		responses = int(row["responses"])
		total = int(row["total_respondents"])
		rate = (responses / total * 100.0) if total else 0.0
		lines.append(f"{index}. {question_text} & {responses}/{total} & {rate:.1f}\\% \\\\")

	lines.extend([
		r"\hline",
		r"\end{tabular}",
		r"\end{table}",
	])

	return "\n".join(lines) + "\n"


def main() -> None:
	root_dir = Path(__file__).resolve().parent
	schema_path = root_dir / "survey-questions-schema.json"
	responses_path = root_dir / "procedural-level-generation-survey.json"
	output_path = root_dir / "survey-response-counts.json"
	latex_output_path = root_dir / "survey-response-counts.tex"

	schema = load_json(schema_path)
	responses = load_json(responses_path)

	schema_questions = schema.get("questions", {})
	counts = count_answers_by_question(responses, schema_questions)

	with output_path.open("w", encoding="utf-8") as file:
		json.dump(counts, file, indent=2, ensure_ascii=False)

	latex_table = build_latex_table(counts)
	with latex_output_path.open("w", encoding="utf-8") as file:
		file.write(latex_table)

	print_counts(counts)
	print(f"\nSaved detailed counts to: {output_path}")
	print(f"Saved LaTeX table to: {latex_output_path}")


if __name__ == "__main__":
	main()
